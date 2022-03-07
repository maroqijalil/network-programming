import socket
import select
import sys
from os.path import exists
from os.path import dirname

SERVER_HOST = 'localhost'
SERVER_PORT = 5000
BUF_SIZE = 1024

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (SERVER_HOST, SERVER_PORT)
server_socket.bind(server_address)
server_socket.listen(5)

input_socket = [server_socket]

try:
  while True:
    read_ready, write_ready, exception = select.select(input_socket, [], [])

    for sock in read_ready:
      if sock == server_socket:
        client_socket, client_address = server_socket.accept()
        input_socket.append(client_socket)
      
      else:
        data = sock.recv(BUF_SIZE).decode()
        print(sock.getpeername(), data)
        if data:
          cmd = data.split(" ")
          file_name = cmd[1][:-1]
          current_path = dirname(__file__)
          file_path = current_path + r'{}'.format("\\dataset\\") + r'{}'.format(file_name)

          if not exists(file_path):
            sock.send("file-doesn't-exist".encode())

          else:
            sock.send("file-exist".encode())
            print('sending', file_name)
            if data != '':
              file = open(file_path, 'rb')
              data = file.read(BUF_SIZE)
              while data:
                sock.send(data)
                data = file.read(BUF_SIZE)
              
              sock.shutdown(socket.SHUT_RDWR)
              sock.close()
              input_socket.remove(sock)
        else:
          sock.shutdown(socket.SHUT_RDWR)
          sock.close()
          input_socket.remove(sock)
          
except KeyboardInterrupt:
  server_socket.close()
  sys.exit(0)
  