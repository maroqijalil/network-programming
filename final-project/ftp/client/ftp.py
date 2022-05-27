import socket
import os
from handler import DataConnection, DataHandler
from typing import List
from utils import Input, Socket


class FTPClient:
  def __init__(self, host, port = 21):
    self.socket = Socket(host, port)

    self.host = host
    self.root = os.getcwd()

    self.data_connection: DataConnection = DataConnection()

    self.responses: List[str] = []

  def close_data_connection(self) -> None:
    self.data_socket.close()
    self.data_socket = None

  def __del__(self):
    self.send('QUIT\r\n')
    self.socket.close()

  def connect(self) -> bool:
    if self.socket.connect():
      self.socket = self.socket.get()

      return True

    return False
  
  def send(self, command: str) -> str:
    self.socket.send(command.encode('utf-8'))

    response = self.socket.recv(1024)
    response = response.decode('utf-8').split('\r\n')

    print(response)

    self.responses.extend(response)

    return response

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

  def pasv(self):
    reply = self.send('PASV\r\n')

    content = reply.split("(")[1].split(")")[0].split(",")
    port = (int(content[4]) * 256) + int(content[5])

    print(f"\nTry to connect at {self.host}:{port}.")

    data_socket = Socket(self.host, port)
    if not data_socket.connect():
      print(f"\tFailed to open data connection.\n")

    else:
      self.data_connection.set_handler(DataHandler(data_socket.get()))
      print(f"\tSuccess to open data connection.\n")
  
  def type(self, command: str):
    reply = self.send(f"{command}\r\n")

    if "200" in reply:
      data_type = command.split()[1]
      self.data_connection.set_type(data_type)

  def list(self, command: str):
    reply = self.send(f'{command}\r\n')

    if "150" in reply:
      def callback(server_socket: socket.socket):
        datas = DataHandler.get_data(server_socket)

        dirs = []
        files = []
        for data in datas.decode(self.data_connection.type).split('\r\n'):
          contents = data.split(" ")

          try:
            if data[0] == 'd':
              dirs.append(contents[-1])
            else:
              files.append(contents[-1])
          except:
            pass

        directory = command.split()[1]

        print(f"Contents of {directory}.")
        if dirs:
          print("Directories:")
          for dir in dirs:
            print(f'\t/{dir}')

        if files:
          print("Files:")
          for file in files:
            print(f'\t{file}')
      
      self.data_connection.handler.set_callback(callback)

    else:
      self.data_connection.handler = None

  def retr(self, command):
    reply = self.send(f'{command}\r\n')

    arguments = reply.split()[1:]

    filename = arguments[0].split("/")[-1]
    target = ""

    print()
    if len(arguments) == 1:
      target = Input.get_input_by_confirm(
        "Make default folder to put downloaded file? (y/n) ",
        "Which folder? ",
        "/"
      )

    elif len(arguments) == 2:
      target = arguments[1]

    if not len(target):
      if target[0] != "/":
        target = "/" + target

      target = self.root + target

      if os.path.isdir(target):
        def callback(server_socket: socket.socket):
          print(f"\nDownloading {filename}.")
          content = DataHandler.get_data(server_socket)

          if self.data_connection.type == "ascii":
            content = content.decode(self.data_connection.type)

          with open(f"{target}/{filename}", self.data_connection.get_write_type()) as file:
            file.write(content)
          
          print("\tDownload success.\n")

        self.data_connection.handler.set_callback(callback)

    else:
      print("\nDownload failed, please specify the target directory.\n")
      self.data_connection.handler = None

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

  def run(self) -> None:
    if self.socket is Socket:
      return

    while self.is_running:
      command = input(">> ")

      if command:
        try:
          if "PASV" in command:
            self.pasv()

          elif "TYPE" in command:
            self.type(command)

          elif "LIST" in command or "LS" in command:
            self.list(command)

          if command in ["LIST", "LS", "RETR", "STOR"]:
            commands = command.split()
            command = commands[0]

            argument = ""
            if len(commands) > 1:
              argument = commands[1]

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

          else:
            print(self.send(command))

        except Exception as e:
          print(e)
          pass

      else:
        break

    print()
