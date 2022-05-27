import socket


class Socket:
  def __init__(self, host: str, port: int) -> None:
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    self.host = host
    self.port = port
  
  def connect(self, listen_for: int = 1):
    try:
      self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
      try:
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
      except AttributeError:
        pass

      self.socket.bind((self.host, self.port))
      self.socket.listen(listen_for)

      return True

    except Exception:
      return False
  
  def get(self) -> socket.socket:
    return self.socket
