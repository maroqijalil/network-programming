import socket


class Socket:
  def __init__(self, host: str, port: int) -> None:
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    self.host = host
    self.port = port
  
  def connect(self):
    try:
      self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
      try:
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
      except AttributeError:
        pass

      self.socket.connect((self.host, self.port))

      return True

    except Exception:
      return False
  
  def get(self) -> socket.socket:
    return self.socket


class Input:
  @staticmethod
  def get_input_by_confirm(confirm, determine, default = ""):
    while True:
      print(confirm, end='')
      command = input()

      if any(avail == command for avail in ['y', 'n', '']):
        break

    result = default
    if command == 'n':
      print(determine, end='')
      result = input()
    
    return result


class Path:
  @staticmethod
  def merge(first: str, second: str) -> str:
    if second[0] != "/":
      second = "/" + second
    if second[-1] == "/":
      second = second[:-1]

    return f"{first}{second}"
