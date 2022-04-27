from ctypes import Union
import socket
from typing import List
from urllib import response


class FTPClient:
  def __init__(self, host, port = 21, workdir = "files"):
    self.conn_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.data_socket: socket.socket = None

    FTPClient.handle_reuse(self.conn_socket)
    self.conn_socket.connect((host, port))

    self.workdir = workdir
    self.host = host
    self.responses: List[str] = []
  
  def __del__(self):
    self.send(['QUIT\r\n'])
    self.conn_socket.close()

    if self.data_socket:
      self.data_socket.close()

    self.summary()
    
  @staticmethod
  def handle_reuse(sock: socket.socket):
    try:
      sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
      try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
      except AttributeError:
        pass

    except Exception:
      pass
  
  def send(self, commands: List[str]):
    for command in commands:
      self.conn_socket.send(command.encode('utf-8'))
      response = self.conn_socket.recv(1024)
      response = response.strip().decode('utf-8').split('\r\n')
      self.responses.extend(response)
  
  def get_response(self, substr) -> str:
    for response in self.responses:
      if substr in response:
        return response
    
    return ""
  
  def get_data(self) -> str:
    response = ""
    while True:
      data = self.data_socket.recv(1024)

      if data:
        response += data.strip().decode('utf-8')
      else:
        break
    
    return response

  def login(self, user, passwd) -> bool:
    self.send([f'USER {user}\r\n', f'PASS {passwd}\r\n'])

    if not self.get_response("230"):
      self.send(['\r\n'])

      if not self.get_response("230"):
        return False

    return True

  def pasv(self):
    self.send(['PASV\r\n'])

    response = self.get_response("Passive Mode")
    content = response.split("(")[1].split(")")[0].split(",")

    p1, p2 = int(content[4]), int(content[5])
    port = p1 * 256 + p2

    self.data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    FTPClient.handle_reuse(self.data_socket)
    self.data_socket.connect((self.host, port))

  def type(self, type):
    self.send([f'TYPE {type}\r\n'])

  def ls(self, dirname = ""):
    self.type('I')
    self.pasv()
    self.send([f'LIST {self.workdir}/{dirname}\r\n'])

    dirs = []
    files = []
    for data in self.get_data().split('\r\n'):
      datas = data.split(" ")

      try:
        if data[0] == 'd':
          dirs.append(datas[-1])
        else:
          files.append(datas[-1])
      except:
        pass

    if dirs:
      print("directories:")
      for dir in dirs:
        print(f' /{dir}')

    if files:
      print("files:")
      for file in files:
        print(f' {file}')
  
  def mkdir(self, dirname) -> bool:
    self.send([f'MKD {self.workdir}/{dirname}\r\n'])

    if self.get_response("257"):
      return True

    return False

  def summary(self):
    print("\nsummary:")
    for response in self.responses:
      print(response)
    print("")
