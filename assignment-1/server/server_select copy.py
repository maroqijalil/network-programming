import socket
import select
import sys
import os


class Server():
  def __init__(self, host, port) -> None:
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    self.host = host
    self.port = port

    self.input_sockets = []
    
    self.files_path = os.path.dirname(__file__) + "/dataset/"
  
  def __del__(self):
    self.socket.close()
  
  def connect(self) -> bool:
    try:
      self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
      try:
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
      except AttributeError:
        pass

      self.socket.bind((self.host, self.port))
      self.socket.listen(100)

      self.input_sockets.append(self.socket)

      return True

    except Exception:
      return False
  
  def run(self) -> None:
    read_ready_sockets, _, _ = select.select(self.input_sockets, [], [])

    for ready_socket in read_ready_sockets:
      if ready_socket == self.socket:
        client_socket, _ = self.socket.accept()
        self.input_sockets.append(client_socket)
      
      else:
        data = ready_socket.recv(1024).decode('utf-8')
        print(ready_socket.getpeername(), data)

        if data:
          commands = data.split(" ")
          file_name = commands[1][:-1]
          file_path = self.files_path + file_name

          if not os.path.exists(file_path):
            ready_socket.send(b'file doesn\'t exist')

          else:
            file_size = os.path.getsize(file_path)

            header = (f'\nfile-name: {file_name},\nfile-size: {file_size},\n\n\nflag').encode('utf-8')

            data = b''
            with open(file_path, 'rb') as file:
              data = file.read()

            ready_socket.sendall(header + data)

        else:
          ready_socket.close()
          self.input_sockets.remove(ready_socket)


if __name__ == '__main__':
  server = Server('localhost', 5000)

  try:
    if server.connect():
      while True:
        server.run()

  except KeyboardInterrupt:
    sys.exit(0)
