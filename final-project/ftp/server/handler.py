from random import randint
from threading import Thread
from typing import List, Optional
from utils import Reply, Socket
import os
import socket
import time


class DataHandler(Thread):
  def __init__(self, socket: socket.socket, type: str):
    Thread.__init__(self)

    self.socket = socket
    self.type = type

  def run(self):
    while True:
      client_socket, _ = self.socket.accept()

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

  def retr(self, filepath: str) -> Reply:
    if filepath:
      filepath = self.handle_workdir(filepath)

  def run(self):
    while True:
      command = self.socket.recv(4096).decode("utf-8")

      print(self.socket.getpeername(), end=": ")
      print(command)

      if command:
        try:
          commands = command.split()
          command = commands[0]

          argument = ""
          if len(commands) > 1: argument = commands[1]

          reply: Reply = None

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
            reply = self.pasv()

          elif command == "QUIT":
            reply = Reply(221, "Goodbye.")

          else:
            reply = Reply()

          if reply:
            if self.reply:
              reply = self.reply + reply
              self.reply = None

            self.socket.sendall(reply.get().encode("utf-8"))

        except Exception as e:
          pass

      else:
        self.socket.close()
        break
    
    if self.data_thread:
      self.data_thread.join()
