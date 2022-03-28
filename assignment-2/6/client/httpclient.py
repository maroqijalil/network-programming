from bs4 import BeautifulSoup
import socket


class Request:
  def __init__(self):
    self.route = ''
    self.host = ''

  def create(self) -> bytes:
    return (
      f'GET {self.route} HTTP/1.1\r\n'
      f'Host: {self.host}\r\n'
      'Connection: close\r\n'
      '\r\n'
    ).encode('utf-8')


class Response:
  def __init__(self):
    self.header = ''
    self.body = ''
    
    self.header_flag = 0

  def process_header(self, buffer) -> bool:
    if not buffer:
      return True

    self.header += buffer.decode('utf-8')

    if (self.header_flag % 2 == 0) and (buffer == b'\r'):
      self.header_flag += 1
    elif (self.header_flag % 2 == 1) and (buffer == b'\n'):
      self.header_flag += 1
    else:
      self.header_flag = 0

    if self.header_flag >= 3:
      return True

    return False

  def get_content_length(self) -> int:
    length = 0
    for line in self.header.splitlines():
      if line.__contains__('Content-Length'):
        length = int(line.split()[1])

    return length

  def process_body(self, buffer) -> int:
    self.body += buffer.decode('utf-8')

    return len(self.body)


class HttpClient:
  def __init__(self, host, port):
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    self.server_host = host
    self.server_port = port

  def __del__(self):
    self.socket.shutdown(socket.SHUT_RDWR)
    self.socket.close()

  def connect(self) -> bool:
    try:
      self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
      try:
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
      except AttributeError:
        pass

      self.socket.connect((self.server_host, self.server_port))

      return True

    except Exception:
      return False

  def get(self, route):
    request = Request()
    request.route = route
    request.host = self.server_host

    self.socket.sendall(request.create())

    response = Response()
    while True:
      buffer = self.socket.recv(1)

      if response.process_header(buffer):
        break

    body_length = response.get_content_length()
    get_length = 0

    while get_length < body_length:
      buffer = self.socket.recv(body_length - get_length)
      get_length = response.process_body(buffer)

    
    soup = BeautifulSoup(response.body, features="lxml")
    for line in soup.get_text().splitlines():
      if (len(line) > 0) and (line != '\n'):
        print(line)
