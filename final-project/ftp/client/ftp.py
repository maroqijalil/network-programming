import socket
import os
from typing import List
from utils import Socket


class FTPClient:
  def __init__(self, host, port = 21, workdir = ""):
    self.socket = Socket(host, port)

    self.data_socket: socket.socket = None

    self.workdir = workdir
    self.host = host
    self.responses: List[str] = []

  def close_data_connection(self) -> None:
    self.data_socket.close()
    self.data_socket = None

  def __del__(self):
    self.send(['QUIT\r\n'])
    self.socket.close()

  def connect(self) -> bool:
    if self.socket.connect(100):
      self.socket = self.socket.get()

      return True
    
    return False
  
  def send(self, commands: List[str]):
    for command in commands:
      self.socket.send(command.encode('utf-8'))
      response = self.socket.recv(1024)
      response = response.strip().decode('utf-8').split('\r\n')
      self.responses.extend(response)
  
  def get_response(self, substr) -> str:
    for response in self.responses:
      if substr in response:
        return response
    
    return ""
  
  def get_content(self, code) -> str:
    response = self.get_response(code)
    return response.replace(code, "").strip()
  
  def get_data(self) -> str:
    response = ""
    while True:
      data = self.data_socket.recv(1024)

      if data:
        response += data.strip().decode('utf-8')
      else:
        break
    
    self.close_data_connection()
    
    return response

  def login(self, user, passwd) -> bool:
    self.send([f'USER {user}\r\n', f'PASS {passwd}\r\n'])

    if not self.get_response("230"):
      self.send(['\r\n'])

      if not self.get_response("230"):
        return False

    return True

  def cd(self, dirname) -> bool:
    self.send([f'CWD {dirname}\r\n'])

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
  
  def retreive(self, filename):
    self.type('I')
    self.pasv()
    self.send([f'RETR {filename}\r\n'])

    filename = os.getcwd() + f"/dataset/{filename}"

    if not os.path.exists(filename):
      with open(filename, "wb") as file:
        file.write(self.get_data())

  def store(self, filename, targetdir = ""):
    self.type('I')
    self.pasv()
    filepath = os.getcwd() + "/dataset/" + filename

    if os.path.exists(filepath):
      with open(filepath, 'rb') as file:
        self.data_socket.sendall(file.read())
        self.close_data_connection()

        self.send([f'STOR {filename}\r\n'])

    else:
      raise Exception(f"file not found in {filepath}")

  def rename(self, source, target) -> bool:
    self.send([f'RNFR {self.workdir}/{source}\r\n'])
    self.send([f'RNTO {self.workdir}/{target}\r\n'])

    if self.get_response("250"):
      return True

    return False

  def rmdir(self, dirname) -> bool:
    self.send([f'RMD {self.workdir}/{dirname}\r\n'])

    if self.get_response("250"):
      return True

    return False

  def run(self) -> None:
    if self.socket is Socket:
      return

    while self.is_running:
      command = self.socket.recv(4096).decode("utf-8")

      print(self.socket.getpeername(), end=": ")
      print(command)

      if command:
        try:
          commands = command.split()
          command = commands[0]

          argument = ""
          if len(commands) > 1:
            argument = commands[1]

          reply = Reply()

          if command == "USER":
            reply = self.validate_user(argument)

          elif command == "QUIT":
            reply = Reply(221, "Goodbye.")
            self.is_running = False

          elif not self.check_auth():
            reply = self.check_auth()

            if command == "PASS":
              reply = self.validate_password(argument)

            elif command == "CWD":
              reply = self.cwd(argument)

            elif command == "TYPE":
              reply = self.type(argument)

            elif command == "PASV":
              reply = self.pasv()

            elif command == "RNFR":
              reply = self.rnfr(argument)

            elif command == "RNTO":
              reply = self.rnto(argument)

            elif command == "MKD":
              reply = self.mkd(argument)

            elif command == "PWD":
              reply = self.pwd()

            elif command == "HELP":
              reply = self.help()

            elif command == "DELE":
              reply = self.dele(argument)

            elif command == "RMD":
              reply = self.rmd(argument)

            elif command in ["LIST", "RETR", "STOR"]:
              if not self.data_connection.check_connection():
                if command == "LIST":
                  reply = self.ls(argument)

                elif command == "RETR":
                  reply = self.retr(argument)

                elif command == "STOR":
                  reply = self.stor(argument)

              else:
                reply = self.data_connection.check_connection()

          if self.reply:
            reply = self.reply + reply
            self.reply = None

          self.data_connection.run(self.socket)

          self.socket.sendall(reply.get().encode("utf-8"))

        except Exception as e:
          print(e)
          pass

      else:
        break

    print()
