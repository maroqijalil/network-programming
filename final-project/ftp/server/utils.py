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


class Reply:
  def __init__(self, code = 500, message = "Command unrecognized.") -> None:
    self.code = code
    self.message = message

    self.reply = f'{self.code} {self.message}\r\n'

  def __add__(self, other):
    reply = Reply()

    if other:
      reply.reply = self.reply + other.reply
    else:
      reply.reply = self.reply

    return reply

  def get(self) -> str:
    return self.reply
  
  @staticmethod
  def handle_error(e):
    print(e)
    return Reply(451, "Requested action aborted. Local error in processing.")


class Config:
  def __init__(self, filepath) -> None:
    self.filepath = filepath
  
  def get(self) -> dict:
    contents = ''
    with open(self.filepath, 'r') as file:
      contents = file.read()

    config = {}
    if contents != '':
      for line in contents.splitlines():
        if len(line):

          items = line.split('=')

          if len(items) > 1:
            config[items[0]] = items[1]

    else:
      raise Exception("The config not found!")

    return config


class Path:
  @staticmethod
  def merge(first: str, second: str) -> str:
    if len(second) and second[0] != "/":
      second = "/" + second
    if (len(second) > 1) and second[-1] == "/":
      second = second[:-1]

    return f"{first}{second}"
