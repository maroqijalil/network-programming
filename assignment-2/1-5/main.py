from bs4 import BeautifulSoup
import re
import socket
import ssl


class HttpClient:
  def __init__(self, host, using_ssl = False):
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    port = 80
    if (using_ssl):
      self.socket = ssl.wrap_socket(self.socket, keyfile=None, certfile=None, \
        server_side=False, cert_reqs=ssl.CERT_NONE, ssl_version=ssl.PROTOCOL_SSLv23)

      port = 443

    self.socket.connect((host, port))

    self.host = host

  def __del__(self):
    self.socket.close()

  def request_header_route(self, route) -> str:
    self.socket.sendall((
        f'GET {route} HTTP/1.1\r\n'
        f'Host: {self.host}\r\n'
        'Connection: close\r\n'
        'Accept: text/html\r\n'
        'Accept-Encoding: gzip, deflate, br\r\n'
        '\r\n'
      ).encode('utf-8'))

    response = b''
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

      response += buffer

      if header_flag >= 3:
        break

    return response.decode('utf-8')[:-3]

  def request_route(self, route) -> str:
    self.socket.sendall((
        f'GET {route} HTTP/1.1\r\n'
        f'Host: {self.host}\r\n'
        'Connection: close\r\n'
        'Accept: text/html\r\n'
        '\r\n'
      ).encode('utf-8'))

    response = b''
    header_flag = 0
    start_read = False
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

      if start_read:
        response += buffer

      if header_flag >= 3:
        start_read = True

    return response.decode('utf-8')


def run_program(using_ssl):
  client = HttpClient("www.its.ac.id", using_ssl)
  header = client.request_header_route('/')

  print("Host: www.its.ac.id")
  response_statuses = header.splitlines()[0].split(' ')
  content_encoding = "Content-Encoding: "
  for line in header.splitlines():
    if line.__contains__("Content-Encoding"):
      contents = line.split(' ')

      if len(contents) > 1:
        content_encoding += contents[1]
  
  print("Response-Status:", end="")
  for index in range(1, len(response_statuses)):
    print(f' {response_statuses[index]}', end="")
  print("")
  print(content_encoding)
  print(f'HTTP-Version: {response_statuses[0]}')
  
  client = HttpClient("classroom.its.ac.id", using_ssl)
  header = client.request_header_route('/')

  print("")
  print("Host: classroom.its.ac.id")
  print("Content-Type-Charset: ", end="")
  for line in header.splitlines():
    if line.__contains__("Content-Type"):
      contents = re.findall(r'charset=[\w\.-]+', line)

      if len(contents) > 0:
        print(contents[0][8:])
      else:
        print("")


if __name__ == '__main__':
  run_program(False)

  print("")
  print("==============================")
  print("Using SSL")
  run_program(True)

  print("Get-Menus:")
  client = HttpClient("classroom.its.ac.id", True)
  body = client.request_route('/')
  soup = BeautifulSoup(body, features="lxml")

  for tag in soup.nav.ul.find_all('li'):
    sub_soup = BeautifulSoup(str(tag), features="lxml")
    list = sub_soup.find('a', {'class': 'dropdown-toggle'}).text.split()

    for item in list:
      print(item, end=" ")
    print("")

    for subtag in sub_soup.find_all('a', {'class': 'dropdown-item'}):
      list = BeautifulSoup(str(subtag), features="lxml").text.split()

      print("\t", end="")
      for item in list:
        if len(item) > 0:
          print(item, end=" ")
      print("")
