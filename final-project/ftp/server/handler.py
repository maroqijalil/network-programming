from random import randint
from threading import Thread
from typing import Callable, List, Optional
from utils import Reply, Socket
import os
import socket
import time


class DataHandler(Thread):
  def __init__(self, data_socket: socket.socket):
    Thread.__init__(self)

    self.socket = data_socket
    
    self.client_socket: socket.socket = None

    self.callback: Callable[[socket.socket], Reply] = None
    self.is_running = True

    self.reply: Reply = None

  def __del__(self) -> None:
    self.socket.close()

  def close(self) -> None:
    self.is_running = False
  
  def set_callback(self, callback: Callable[[socket.socket], Reply]) -> None:
    self.callback = callback

  def run(self):
    while self.is_running:
      if not self.client_socket:
        self.client_socket, _ = self.socket.accept()
      
      if self.callback:
        self.reply = self.callback(self.client_socket)
        self.client_socket.close()

        self.callback = None

  @staticmethod
  def is_port_open(host, port):
    data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    result = data_socket.connect_ex((host, port))
    data_socket.close()

    return result

  @staticmethod
  def handle(command_socket: socket.socket, data_handler, callback: Callable[[], None]) -> None:
    start_time = time.perf_counter()

    while True:
      reply = data_handler.reply
      if reply:
        command_socket.sendall(reply.get().encode("utf-8"))
        break

      if time.perf_counter() - start_time > 3.0:
        break
    
    callback()


class FileRenaming:
  def __init__(self, source) -> None:
    self.source = source

  def execute(self, target) -> None:
    os.rename(self.source, target)


class DataConnection:
  def __init__(self) -> None:
    self.type = "ascii"
    self.handler: DataHandler = None
    self.executor: Thread = None

  def get_read_type(self) -> str:
    if self.type == "utf-8":
      return "rb"
    elif self.type == "ascii":
      return "r"

  def get_write_type(self) -> str:
    if self.type == "utf-8":
      return "wb"
    elif self.type == "ascii":
      return "w"

  def get_mode_type(self) -> str:
    if self.type == "utf-8":
      return "Binary"
    elif self.type == "ascii":
      return "ASCII"

  def set_handler(self, handler: DataHandler) -> None:
    self.handler = handler
    self.handler.start()

  def set_type(self, type) -> None:
    if type == "I":
      self.type = "utf-8"

    if type == "A":
      self.type = "ascii"

  def close(self) -> None:
    if self.handler:
      self.handler.close()
      self.handler.join()
      self.handler = None

    self.executor = None

  def check_connection(self) -> Optional[Reply]:
    if not self.handler:
      return Reply(425, "Use PORT or PASV first.")

    return None
  
  def run(self, command_socket: socket.socket) -> None:
    if self.handler and self.handler.callback and not self.executor:
      self.executor = Thread(target=DataHandler.handle, args=(command_socket, self.handler, self.close))
      self.executor.start()


class CommandHandler(Thread):
  def __init__(self, host: str, socket: socket.socket, root: str, user: str, passwd: str) -> None:
    Thread.__init__(self)

    self.host = host
    self.root = root
    self.user = user
    self.passwd = passwd
    self.workdir = "/"

    self.socket = socket

    self.reply = Reply(220, "(myFTP 0.0.0)")
    self.is_running = True

    self.data_connection: DataConnection = DataConnection()

    self.file_renaming: FileRenaming = None

  def __del__(self) -> None:
    self.socket.close()
  
  def check_auth(self) -> Optional[Reply]:
    if len(self.user) or len(self.passwd):
      return Reply(530, "Please login with USER and PASS.")
  
  def validate_user(self, user) -> Reply:
    self.user = self.user.replace(user, "")

    if len(self.user):
      return Reply(530, "Permission denied.")
    
    return Reply(331, "Please specify the password.")
  
  def validate_password(self, passwd) -> Reply:
    if len(self.user):
      return Reply(503, "Login with USER first.")

    self.passwd = self.passwd.replace(passwd, "")

    if len(self.passwd):
      return Reply(530, "Login incorrect.")
    
    return Reply(230, "Login successful.")

  def handle_directory(self, path: str) -> str:
    if path[0] != "/":
      path = self.workdir + path

    return self.root + path

  def cwd(self, directory: str) -> Reply:
    if directory:
      if os.path.isdir(self.handle_directory(directory)):
        self.workdir += directory

        return Reply(250, "Directory successfully changed.")

    return Reply(550, "Failed to change directory.")

  def type(self, type: str) -> Reply:
    self.data_connection.set_type(type)
    return Reply(200, f"Switching to {self.data_connection.get_mode_type()} mode.")

  def pasv(self) -> Reply:
    port = None
    start_time = time.perf_counter()

    while True:
      port = randint(59999, 65535)

      if DataHandler.is_port_open(self.host, port):
        break

      if time.perf_counter() - start_time > 3.0:
        break

    if port:
      data_socket = Socket(self.host, port)

      if data_socket.connect():
        self.data_connection.set_handler(DataHandler(data_socket.get()))

        address = self.host.split('.')
        port = [int(port / 256), (port % 256)]

        return Reply(227, f"Entering Passive Mode ({address[0]},{address[1]},{address[2]},{address[3]},{port[0]},{port[1]}).")

    return Reply(421, "Failed to enter Passive Mode.")

  def ls(self, directory: str = "") -> Reply:
    directory = self.handle_directory(directory)

    def callback(client_socket: socket.socket) -> Reply:
      try:
        items = ""

        if os.path.exists(directory):
          for item in os.popen(f"ls -n {directory}").readlines():
            if len(item) and (item[0] == '-' or item[0] == 'd'):
              items += item.replace('\n', "")
              items += "\r\n"

        client_socket.sendall(items.encode(self.data_connection.type))
        return Reply(226, "Directory send OK.")

      except Exception as e:
        print(e)
        return Reply(451, "Requested action aborted. Local error in processing.")

    self.data_connection.handler.set_callback(callback)

    return Reply(150, "Here comes the directory listing.")

  def retr(self, filename: str) -> Reply:
    if filename:
      callback = None

      try:
        filepath = self.handle_directory(filename)
        content = ""

        if os.path.isfile(filepath):
          with open(filepath, self.data_connection.get_read_type()) as file:
            content = file.read()

          if self.data_connection.type == "ascii":
            content = content.encode(self.data_connection.type)

          def callback(client_socket: socket.socket) -> Reply:
            client_socket.sendall(content)
            return Reply(226, "Transfer complete.")

      except Exception as e:
        print(e)
        return Reply(451, "Requested action aborted. Local error in processing.")

      if callback:
        self.data_connection.handler.set_callback(callback)
        return Reply(150, f"Opening {self.data_connection.get_mode_type()} mode data connection for {filename} ({len(content)} bytes).")

      else:
        self.data_connection.handler = None

    return Reply(550, "Failed to open file.")

  def stor(self, filename: str) -> Reply:
    if filename:
      def callback(client_socket: socket.socket) -> Reply:
        try:
          filepath = self.handle_directory(filename)
          content = b""

          while True:
            buffer = client_socket.recv(1024)

            if buffer:
              content += buffer
            else:
              break

          if not os.path.isfile(filepath):
            with open(filepath, self.data_connection.get_write_type()) as file:
              file.write(content)

          return Reply(226, "Transfer complete.")

        except Exception as e:
          print(e)
          return Reply(451, "Requested action aborted. Local error in processing.")

      self.data_connection.handler.set_callback(callback)

    return Reply(150, "Ok to send data.")

  def run(self):
    while self.is_running:
      command = self.socket.recv(4096).decode("utf-8")

      print(self.socket.getpeername(), end=": ")
      print(command)

      if command:
        try:
          commands = command.split()
          command = commands[0]

          argument = ""
          if len(commands) > 1: argument = commands[1]

          reply = Reply()

          if command == "USER":
            reply = self.validate_user(argument)

          elif command == "PASS":
            reply = self.validate_password(argument)

          elif command == "CWD":
            reply = self.cwd(argument)

          elif command == "TYPE":
            reply = self.type(argument)

          elif command == "PASV":
            reply = self.pasv()

          elif command == "LIST":
            reply = self.ls(argument)

          elif command == "RETR":
            reply = self.retr(argument)

          elif command == "STOR":
            reply = self.stor(argument)

          elif command == "STOR":
            reply = self.stor(argument)

          elif command == "QUIT":
            reply = Reply(221, "Goodbye.")
            self.is_running = False
          
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

    self.data_connection.close()
