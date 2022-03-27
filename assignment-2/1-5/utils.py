import socket

class HttpClient:
  def __init__(self, address):
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.socket.connect((address, 80))

    self.address = address
  
  def request_route(self, route):
    self.socket.sendall((f'GET {route} HTTP/1.1\r\nHost: {self.address}\r\nConnection: close\r\n\r\n').encode('utf-8'))

    response = ''
    while True:
      buffer = self.socket.recv(1)

      if not buffer:
          break

      response += buffer.decode('utf-8')

    responses = response.split('\r\n\r\n')

    if len(responses) > 0:
      if len(responses) > 1:
        return responses[0], responses[1]

      return responses[0]


if __name__ == '__main__':
  client = HttpClient("www.its.ac.id")
  header, body = client.request_route('/')
