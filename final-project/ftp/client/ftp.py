import socket
import os
from handler import DataConnection, DataHandler
from typing import List
from utils import Path, Input, Socket


class FTPClient:
  def __init__(self, host, port = 21):
    self.socket = Socket(host, port)

    self.host = host
    self.root = os.getcwd()

    self.data_connection: DataConnection = DataConnection()

    self.replies: List[str] = []

  def __del__(self):
    self.send('QUIT\r\n')
    self.socket.close()

    print("Summary:")
    for message in self.replies:
      print(message)

  def connect(self) -> bool:
    if self.socket.connect():
      self.socket = self.socket.get()

      return True

    return False
  
  def send(self, command: str) -> str:
    self.socket.send(command.encode('utf-8'))

    buffer = self.socket.recv(1024).decode('utf-8')
    reply = buffer.strip().split('\r\n')

    for message in reply:
      print(message)
    print()

    self.replies.extend(reply)

    return buffer

  def pasv(self):
    if self.data_connection.handler:
      print(f"There is still connection on transfering data.\n")
      return

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

        directory = "/"
        commands = command.split()
        if len(commands) > 1:
          directory = commands[1]

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
      return

    self.data_connection.handler = None

  def handle_directory(self, directory) -> str:
    return Path.merge(self.root, directory)

  def retr(self, command: str):
    reply = self.send(f'{command}\r\n')

    if "150" in reply:
      arguments = command.split()[1:]

      filename = arguments[0].split("/")[-1]
      filepath = ""

      print()
      if len(arguments) == 1:
        filepath = Input.get_input_by_confirm(
          f"Make the same filename ({filename}) to put downloaded file? (y/n) ",
          "What is the filename? ",
          f"/{filename}"
        )

      elif len(arguments) == 2:
        filepath = arguments[1]

      if len(filepath):
        filepath = self.handle_directory(filepath)
        filename = filepath.split('/')[-1]
        filedir = filepath.replace(f"/{filename}", "")

        if os.path.isdir(filedir):
          def callback(server_socket: socket.socket):
            print(f"\nDownloading {arguments[0]}.")
            content = DataHandler.get_data(server_socket)

            if self.data_connection.type == "ascii":
              content = content.decode(self.data_connection.type)

            with open(filepath, self.data_connection.get_write_type()) as file:
              file.write(content)

            print("\tDownload success.\n")

          self.data_connection.handler.set_callback(callback)
          return

        else:
          print("\nDownload failed, directory not found.\n")

      else:
        print("\nDownload failed, please specify the target filename.\n")

    self.data_connection.handler = None

  def stor(self, command: str):
    reply = self.send(f'{command}\r\n')

    if "150" in reply:
      arguments = command.split()[1:]

      filename = arguments[0].split('/')[-1]
      filepath = ""

      print()
      if len(arguments) == 1:
        filepath = Input.get_input_by_confirm(
          f"Choose the same filename ({filename}) to upload? (y/n) ",
          "Which file? ",
          f"/{filename}"
        )

      elif len(arguments) == 2:
        filepath = arguments[0]

      if len(filepath):
        target_path = self.handle_directory(filepath)

        if os.path.isfile(target_path):
          def callback(server_socket: socket.socket):
            print(f"\nUploading {filepath}.")

            content = ""
            with open(target_path, self.data_connection.get_read_type()) as file:
              content = file.read()

            if self.data_connection.type == "ascii":
              content = content.encode(self.data_connection.type)

            server_socket.sendall(content)
            print(f"\n{filepath} uploaded.")
          
          self.data_connection.handler.set_callback(callback)

        else:
          print("\nUpload failed, file not found.\n")

      else:
        print("\nUpload failed, please specify the target filename.\n")

    self.data_connection.handler = None

  def run(self) -> None:
    if self.socket is Socket:
      return

    while True:
      try:
        command = input(">> ")

        if command:
          try:
            if "PASV" in command:
              self.pasv()

            elif "TYPE" in command:
              self.type(command)

            elif "LIST" in command or "LS" in command:
              self.list(command)

            elif "RETR" in command:
              self.retr(command)

            elif "STOR" in command:
              self.stor(command)

            else:
              self.send(command)

            self.data_connection.run(self.socket)

            if "QUIT" in command:
              break

          except Exception as e:
            print(e)
            pass

      except KeyboardInterrupt:
        break

    print()
