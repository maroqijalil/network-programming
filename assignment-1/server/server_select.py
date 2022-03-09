import socket
import select
import sys
import os

SERVER_HOST = 'localhost'
SERVER_PORT = 5000
BUF_SIZE = 1024
FORMAT = 'utf-8'
DATASET_PATH = os.path.dirname(__file__) + r'{}'.format("\\dataset\\")

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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
        data = sock.recv(BUF_SIZE).decode(FORMAT)
        print(sock.getpeername(), data)

        if data:
          data = data.split(" ")
          file_name = data[1][:-1]
          file_path = DATASET_PATH + r'{}'.format(file_name)

          if not os.path.exists(file_path):
            sock.send("file doesn't exist".encode(FORMAT))

          else:
            sock.send(("file exist, start sending {}".format(file_name)).encode(FORMAT))

            file_size = os.path.getsize(file_path)
            header = ("\nfile-name: {},\nfile-size: {},\n\n\n".format(file_name, file_size))
            sock.send(header.encode(FORMAT))

            file = open(file_path, 'rb')
            data = file.read(BUF_SIZE)
            while data:
              sock.send(data)
              data = file.read(BUF_SIZE)
            print("successfully send {}".format(file_name))
            file.close()
              
            sock.close()
            input_socket.remove(sock)
        else:
          sock.close()
          input_socket.remove(sock)
          
except KeyboardInterrupt:
  server_socket.close()
  sys.exit(0)
  