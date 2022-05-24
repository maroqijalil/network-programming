from configparser import ConfigParser
from handler import ClientHandler
from typing import List
import select
import socket


class FTPServer:
  def __init__(self, config: ConfigParser) -> None:
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    self.host = config['host']
    self.port = int(config['port'])
    self.user = config['user']
    self.passwd = config['password']

    self.threads: List[ClientHandler] = []

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

            client = ClientHandler(client_socket, self.user, self.passwd)
            client.start()
            self.threads.append(client)

      except KeyboardInterrupt:
        is_running = False

    self.socket.close()
    for client in self.threads:
      client.join()
