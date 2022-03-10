import socket
import select
import sys
import os
import utils


class Server():
  def __init__(self, host, port) -> None:
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
  
  def run(self) -> None:
    read_ready_sockets, _, _ = select.select(self.input_sockets, [], [])

    for ready_socket in read_ready_sockets:
      if ready_socket == self.socket:
        client_socket, _ = self.socket.accept()
        self.input_sockets.append(client_socket)
      
      else:
        try:
          data = ready_socket.recv(1024)
          print(ready_socket.getpeername(), data.decode('utf-8'))

          if data:
            utils.handle_send_file(ready_socket, data)

          else:
            ready_socket.close()
            self.input_sockets.remove(ready_socket)

        except socket.error:
          print(ready_socket.getpeername(), 'left the server')

          ready_socket.close()
          self.input_sockets.remove(ready_socket)


if __name__ == '__main__':
  server = Server('localhost', 5000)

  try:
    if server.connect():
      while True:
        server.run()

  except KeyboardInterrupt:
    sys.exit(0)
