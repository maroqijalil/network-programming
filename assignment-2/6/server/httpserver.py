import os
import sys
from magic import Magic
import socket
import select
import threading
from typing import Callable, List


class Response:
  def __init__(self):
    self.status_code = 200
    self.status = 'OK'

    self.type = ''
    self.content_length = 0

    self.body = b''

  def create(self) -> bytes:
    header = (
      f'HTTP/1.1 {self.status_code} {self.status}\r\n'
      f'Content-Type: {self.type}\r\n'
      f'Content-Length: {self.content_length}\r\n'
      '\r\n'
    ).encode('utf-8')

    return header + self.body

  @staticmethod
  def get_file_response(filename):
    response = Response()
    filename = os.path.dirname(__file__) + filename
    
    content = ''
    with open(filename, 'rb') as file:
      content = file.read()

    mime = Magic(mime=True)

    response.type = mime.from_file(filename)
    if response.type == "text/html":
      response.type += "; charset=utf-8"

    response.content_length = len(content)
    response.body = content

    return response

  @staticmethod
  def get_404_response():
    response = Response.get_file_response('/404.html')

    response.status_code = 404
    response.status = 'Not found'

    return response


class Route:
  def __init__(self, routes: List[str], response_callback: Callable[[], Response]):
    self.routes = routes
    self.response_callback = response_callback

  def is_match(self, request) -> bool:
    request_header = request.split("\r\n")

    if request_header[0]:
      requested_route = request_header[0].split()[1]

      if len(self.routes) > 0:
        for route in self.routes:
          if requested_route == route:
            return True

    return False


class ClientHandler(threading.Thread):
  def __init__(self, socket, routes):
    threading.Thread.__init__(self)

    self.socket = socket
    self.routes: List[Route] = routes

  def run(self):
    while True:
      request = self.socket.recv(4096)

      if request:
        is_match = False
        response = b''

        request = request.decode("utf-8")

        print(self.socket.getpeername(), end=": ")
        print(request)

        for route in self.routes:
          if route.is_match(request):
            response = route.response_callback().create()
            is_match = True

            break

        if not is_match:
          response = Response.get_404_response().create()

        self.socket.sendall(response)

      else:
        self.socket.close()
        break


class HttpServer:
  def __init__(self, host, port):
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    self.host = host
    self.port = port

    self.routes: List[Route] = []
    self.threads: List[ClientHandler] = []

  def __del__(self):
    self.socket.close()

  def add_route(self, route: Route):
    self.routes.append(route)

  def connect(self) -> bool:
    try:
      self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
      try:
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
      except AttributeError:
        pass

      self.socket.bind((self.host, self.port))
      self.socket.listen(100)

      return True

    except Exception:
      return False

  def run(self):
    is_running = True

    while is_running:
      try:
        read_ready_sockets, _, _ = select.select([self.socket], [], [])

        for ready_socket in read_ready_sockets:
          if ready_socket == self.socket:
            client_socket, _ = self.socket.accept()

            client = ClientHandler(client_socket, self.routes)
            client.start()
            self.threads.append(client)

      except KeyboardInterrupt:
        is_running = False

    self.socket.close()
    for client in self.threads:
      client.join()
