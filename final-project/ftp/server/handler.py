from email.policy import default
from threading import Thread
from typing import List
from utils import Reply
import socket


class ClientHandler(Thread):
  def __init__(self, command_socket: socket.socket, user: str, passwd: str) -> None:
    Thread.__init__(self)

    self.user = user
    self.passwd = passwd

    self.command_socket = command_socket
    self.data_socket: socket.socket = None

  def __del__(self) -> None:
    if self.data_socket:
      self.data_socket.close()

    self.command_socket.close()
  
  def check_auth(self) -> None:
    if len(self.user) or len(self.passwd):
      return Reply(530, "Please login with USER and PASS.")
  
  def validate_user(self, user) -> Reply:
    self.user.replace(user, "")

    if len(self.user):
      return Reply(530, "Permission denied.")
    
    return Reply(331, "Please specify the password.")
  
  def validate_passwd(self, passwd) -> Reply:
    if len(self.user):
      return Reply(503, "Login with USER first.")

    self.passwd.replace(passwd, "")

    if len(self.passwd):
      return Reply(530, "Login incorrect.")
    
    return Reply(230, "Login successful.")

  def run(self):
    while True:
      command = self.command_socket.recv(4096)

      if command:
        try:
          commands = command.decode("utf-8").split()
          command = commands[0]

          argument = ""
          if len(commands) > 1: argument = commands[1]

          reply: Reply = None

          if command == "USER":
            reply = self.validate_user(argument)

          elif command == "PASS":
            reply = self.validate_passwd(argument)

          if reply:
            self.command_socket.sendall(reply.get().encode("utf-8"))

        except Exception as e:
          pass

      else:
        self.command_socket.close()
        break
