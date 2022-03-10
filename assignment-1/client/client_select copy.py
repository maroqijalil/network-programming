import os
import socket
import sys
import re

class Client():
  def __init__(self, host, port) -> None:
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    self.server_host = host
    self.server_port = port
    
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

      self.socket.connect((self.server_host, self.server_port))

      return True

    except Exception:
      return False
  
  def validate(self):
    header = b''
    header_comma_counter = 0
    header_end_flag = 3

    file_name = ''
    file_size = 0

    while True:
      response = self.socket.recv(1)
      if response:
        header += response

      else:
        header = b''
        break
      
      if header_comma_counter >= 2:
        header_end_flag -= 1
      
      if response == b',':
        header_comma_counter += 1
      
      if header_end_flag <= 0:
        break
    
    if len(header) != 0:
      contents = re.findall(r': [\w\.-]+,', header.decode('utf-8'))
      file_name = contents[0][2:-1]
      file_size = int(contents[1][2:-1])

    return len(header), file_name, file_size
  
  def command(self, command) -> None:
    commands = command.split(" ")

    if (commands[0] == "unduh"):
      self.socket.send(command.encode('utf-8'))
      header_size, file_name, file_size = self.validate()

      if header_size != 0:
        print(f'downloading {file_name} ...')

        data = b''
        while len(data) < file_size:
          reponse = self.socket.recv(file_size - len(data))

          if reponse:
            data += reponse

        with open(self.files_path + file_name, 'wb') as file:
          file.write(data)

          print(f'{file_name} downloaded')

    else:
      print("command isn't valid, try again.")
      print("usage: unduh [filename]")


if __name__ == '__main__':
  client = Client('localhost', 5000)

  try:
    if client.connect():
      while True:
        sys.stdout.write('>> ')
        client.command(sys.stdin.readline())

  except KeyboardInterrupt:
    sys.exit(0)
