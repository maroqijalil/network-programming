import argparse
import socket
import sys
import utils


class Client():
  def __init__(self, host, port) -> None:
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    self.server_host = host
    self.server_port = port
  
  def __del__(self):
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
  
  def command(self, command) -> None:
    commands = command.split(" ")

    if (commands[0] == "unduh" and len(commands) >= 2):
      self.socket.send(command.encode('utf-8'))
      utils.handle_receive_file(self.socket)

    else:
      print("command isn't valid, try again.")
      print("usage: unduh [filename]")


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Connect TCPClient on defined host and port')
  parser.add_argument('--host', help='specify the host that will be connected to', type=str, default='localhost')
  parser.add_argument('--port', help='specify the port which is used', type=int, default=5000)

  args = parser.parse_args()

  client = Client(args.host, args.port)

  try:
    if client.connect():
      while True:
        print('>> ', end='')
        client.command(input())

  except KeyboardInterrupt:
    sys.exit(0)
