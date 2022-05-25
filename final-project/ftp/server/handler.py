import os
from threading import Thread
from typing import List, Optional
from utils import Reply
import socket


class ClientHandler(Thread):
  def __init__(self, command_socket: socket.socket, root: str, user: str, passwd: str) -> None:
    Thread.__init__(self)

    self.root = root
    self.user = user
    self.passwd = passwd
    self.workdir = "/"

    self.command_socket = command_socket
    self.data_socket: socket.socket = None

    self.reply = Reply(220, "(myFTP 0.0.0)")

  def __del__(self) -> None:
    if self.data_socket:
      self.data_socket.close()

    self.command_socket.close()
  
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
  
  def cwd(self, directory: str) -> Reply:
    if directory:
      if directory[0] != "/":
        directory = self.workdir + directory
      
      if os.path.isdir(self.root + directory):
        self.workdir = directory

        return Reply(250, "Directory successfully changed.")

    return Reply(550, "Failed to change directory.")

  def run(self):
    while True:
      command = self.command_socket.recv(4096).decode("utf-8")

      print(self.command_socket.getpeername(), end=": ")
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

          elif command == "QUIT":
            reply = Reply(221, "Goodbye.")

          else:
            reply = Reply()

          if reply:
            if self.reply:
              reply = self.reply + reply
              self.reply = None

            self.command_socket.sendall(reply.get().encode("utf-8"))

        except Exception as e:
          pass

      else:
        self.command_socket.close()
        break
