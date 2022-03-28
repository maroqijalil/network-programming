from configparser import ConfigParser
import socket
import select
import sys
import utils


class HttpServer():
  def __init__(self, host, port):
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    self.host = host
    self.port = port

    self.input_sockets = []

  def __del__(self):
    self.socket.close()

  def connect(self) -> bool:
    try:
      self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
      try:
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
      except AttributeError:
        pass

      self.socket.bind((self.host, self.port))
      self.socket.listen(100)

      self.input_sockets.append(self.socket)

      return True

    except Exception:
      return False

  def run(self):
    read_ready_sockets, _, _ = select.select(self.input_sockets, [], [])

    for ready_socket in read_ready_sockets:
      if ready_socket == self.socket:
        client_socket, _ = self.socket.accept()
        self.input_sockets.append(client_socket)

      else:
        data = ready_socket.recv(4096)

        data = data.decode("utf-8")
        request_header = data.split("\r\n")
        request_file = request_header[0].split()[1]
        response_header = b""
        response_data = b""

        if (
          request_file == "index.html"
          or request_file == "/"
          or request_file == "/index.html"
        ):
          f = open("index.html", "r")
          response_data = f.read()
          f.close()

          content_length = len(response_data)
          response_header = (
            "HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=UTF-8\r\nContent-Length:"
            + str(content_length)
            + "\r\n\r\n"
          )

          ready_socket.sendall(
            response_header.encode("utf-8") + response_data.encode("utf-8")
          )

        else:
          ready_socket.sendall(b"HTTP/1.1 404 Not found\r\n\r\n")


if __name__ == '__main__':
  config = utils.get_config('./httpserver.conf')

  server = HttpServer(
    config['server']['address'],
    int(config['server']['port'])
  )

  try:
    if server.connect():
      while True:
        server.run()

  except KeyboardInterrupt:
    sys.exit(0)
