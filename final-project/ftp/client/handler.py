from threading import Thread
from typing import Callable
import socket
import time


class DataHandler(Thread):
  def __init__(self, data_socket: socket.socket):
    Thread.__init__(self)

    self.socket = data_socket
    
    self.server_socket: socket.socket = None

    self.callback: Callable[[socket.socket], None] = None
    self.is_running = True

    self.is_executed: bool = False

  def __del__(self) -> None:
    self.socket.close()

  def close(self) -> None:
    self.is_running = False
  
  def set_callback(self, callback: Callable[[socket.socket], None]) -> None:
    self.callback = callback

  def run(self):
    while self.is_running:
      if self.callback:
        self.is_executed = True

        self.callback(self.server_socket)
        self.server_socket.close()

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
      if data_handler.is_executed:
        print(command_socket.recv(1024).decode("utf-8"))
        break

      if time.perf_counter() - start_time > 3.0:
        break

    callback()

  @staticmethod
  def get_data(server_socket: socket.socket) -> bytes:
    data = b""
    while True:
      buffer = server_socket.recv(1024)

      if buffer:
        data += buffer
      else:
        break

    return data


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
  
  def run(self, command_socket: socket.socket) -> None:
    if self.handler and self.handler.callback and not self.executor:
      self.executor = Thread(target=DataHandler.handle, args=(command_socket, self.handler, self.close))
      self.executor.start()
