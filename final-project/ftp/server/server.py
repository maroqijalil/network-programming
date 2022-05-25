from configparser import ConfigParser
import socket
from handler import CommandHandler
from typing import List
from utils import Socket
import select


class FTPServer:
  def __init__(self, config: ConfigParser) -> None:
    self.socket = Socket(config['host'], int(config['port']))

    self.host = config['host']
    self.user = config['user']
    self.passwd = config['password']
    self.root = config['root']

    self.threads: List[CommandHandler] = []

  def __del__(self):
    self.socket.close()

  def connect(self) -> bool:
    if self.socket.connect(100):
      self.socket = self.socket.get()

      return True
    
    return False

  def run(self) -> None:
    if self.socket is Socket:
      return

    is_running = True

    while is_running:
      try:
        read_ready_sockets, _, _ = select.select([self.socket], [], [])

        for ready_socket in read_ready_sockets:
          if ready_socket == self.socket:
            client_socket, _ = self.socket.accept()

            client = CommandHandler(self.host, client_socket, self.root, self.user, self.passwd)
            client.start()
            self.threads.append(client)

      except KeyboardInterrupt:
        is_running = False

    self.socket.close()

    for client in self.threads:
      client.join()
