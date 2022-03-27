import socket
import ssl

class HttpClient:
  def __init__(self, address, using_ssl = False):
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    port = 80
    if (using_ssl):
      self.socket = ssl.wrap_socket(self.socket, keyfile=None, certfile=None, \
        server_side=False, cert_reqs=ssl.CERT_NONE, ssl_version=ssl.PROTOCOL_SSLv23)

      port = 443

    self.socket.connect((address, port))

    self.address = address

  def request_route(self, route, header_only = False):
    self.socket.sendall((f'GET {route} HTTP/1.1\r\nHost: {self.address}\r\nConnection: close\r\n\r\n').encode('utf-8'))

    response = ''
    header_flag = 0
    while True:
      buffer = self.socket.recv(1)

      if not buffer:
          break

      if (header_flag % 2 == 0) and (buffer == b'\r'):
        header_flag += 1
      elif (header_flag % 2 == 1) and (buffer == b'\n'):
        header_flag += 1
      else:
        header_flag = 0

      response += buffer.decode('utf-8')

      if (header_flag >= 3) and header_only:
        break

    if header_only:
      return response[:-3]
    else:
      responses = response.split('\r\n\r\n')

      if len(responses) > 0:
        return responses[0]
