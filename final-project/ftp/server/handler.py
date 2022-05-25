from random import randint
from threading import Thread
from typing import Callable, List, Optional
from utils import Reply, Socket
import os
import socket
import time


class DataHandler(Thread):
  def __init__(self, data_socket: socket.socket, type: str):
    Thread.__init__(self)

    self.socket = data_socket
    self.type = type
    
    self.client_socket: socket.socket = None

    self.callback: Callable[[socket.socket, str], Reply] = None
    self.is_running = True

    self.reply: Reply = None

  def __del__(self) -> None:
    self.socket.close()

  def get_reply(self) -> Reply:
    return self.reply
  
  def close(self) -> None:
    self.is_running = False
  
  def set_callback(self, callback: Callable[[socket.socket, str], Reply]) -> None:
    self.callback = callback

  def run(self):
    while self.is_running:
      if not self.client_socket:
        self.client_socket, _ = self.socket.accept()
      
      if self.callback:
        self.reply = self.callback(self.client_socket, self.type)
        self.client_socket.close()

        self.callback = None

  @staticmethod
  def is_port_open(host, port):
    data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    result = data_socket.connect_ex((host, port))
    data_socket.close()

    return result


class CommandHandler(Thread):
  def __init__(self, host: str, socket: socket.socket, root: str, user: str, passwd: str) -> None:
    Thread.__init__(self)

    self.host = host
    self.root = root
    self.user = user
    self.passwd = passwd
    self.workdir = "/"

    self.socket = socket

    self.data_type = "ascii"
    self.data_thread: DataHandler = None

    self.reply = Reply(220, "(myFTP 0.0.0)")
    self.is_running = True

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
  
  def handle_workdir(self, path: str) -> str:
    if path[0] != "/":
      path = self.workdir + path
    
    return path

  def cwd(self, directory: str) -> Reply:
    if directory:
      directory = self.handle_workdir(directory)
      
      if os.path.isdir(self.root + directory):
        self.workdir = directory

        return Reply(250, "Directory successfully changed.")

    return Reply(550, "Failed to change directory.")

  def type(self, data_type: str) -> Reply:
    message = ""

    if data_type == "I":
      self.data_type = "utf-8"
      message = "Switching to Binary mode."

    if data_type == "A":
      self.data_type = "ascii"
      message = "Switching to ASCII mode."

    return Reply(200, message)
  
  def check_data_connection(self) -> Reply:
    if not self.data_thread:
      return Reply(425, "Use PORT or PASV first.")

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
        self.data_thread = DataHandler(data_socket.get(), self.data_type)

        address = self.host.split('.')
        port = [int(port / 256), (port % 256)]

        return Reply(227, f"Entering Passive Mode ({address[0]},{address[1]},{address[2]},{address[3]},{port[0]},{port[1]}).")

    return Reply(421, "Failed to enter Passive Mode.")
  
  def get_data_reply(self) -> Reply:
    start_time = time.perf_counter()

    while True:
      if not self.data_thread:
        break

      reply = self.data_thread.get_reply()
      if reply:
        return reply

      if time.perf_counter() - start_time > 3.0:
        break
    
    return None

  def ls(self, directory: str) -> Reply:
    if directory:
      directory = self.handle_workdir(directory)
      directory = self.root + directory

      def callback(client_socket: socket.socket, type: str) -> Reply:
        try:
          items = ""

          for item in os.popen(f"ls -n {directory}").readlines():
            if len(item) and (item[0] == '-' or item[0] == '-'):
              items += item
              items += "\r\n"
          
          client_socket.sendall(items.encode(type))
          return Reply(226, "Directory send OK.")

        except Exception as e:
          return Reply(451, "Requested action aborted. Local error in processing.")

      self.data_thread.set_callback(callback)

      return Reply(150, "Here comes the directory listing.")

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

          elif command == "QUIT":
            reply = Reply(221, "Goodbye.")
            self.is_running = False
          
          if self.reply:
            reply = self.reply + reply
            self.reply = None
          
          if self.data_thread:
            reply = reply + self.get_data_reply()

            self.data_thread.close()
            self.data_thread.join()
            self.data_thread = None

          self.socket.sendall(reply.get().encode("utf-8"))

        except Exception as e:
          pass

      else:
        break
    
    if self.data_thread:
      self.data_thread.join()
