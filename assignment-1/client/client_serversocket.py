import os
import socket
import sys

SERVER_HOST = 'localhost'
SERVER_PORT = 5000
BUF_SIZE = 1024
FORMAT = 'utf-8'

server_address = (SERVER_HOST, SERVER_PORT)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(server_address)

sys.stdout.write('>> ')

try:
  while True:
    msg = sys.stdin.readline()
    cmd = msg.split(" ")
    if (cmd[0] == "unduh"):
      client_socket.send(bytes(msg, 'utf-8'))
      response = client_socket.recv(1024).decode('utf-8')
      if response == "file doesn't exist":
        print("file doesn't exist on server.")

        client_socket.close()
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(server_address) 
        
      else:
        header = client_socket.recv(256).decode(FORMAT)
        print(header, end="")

        filename = cmd[1][:-1]
        write_name = 'from_socketserver_'+ filename
        if os.path.exists(write_name):
          os.remove(write_name)
        
        with open(write_name,'wb') as file:
          while True:
            data = client_socket.recv(1024)
            if not data:
              break
            file.write(data)
        print(filename, ' successfully downloaded.')
        client_socket.close()
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(server_address) 
    else:
      print("command isn't valid, try again.")
      print("usage: unduh [filename]")
    sys.stdout.write('>> ')

except KeyboardInterrupt:
  client_socket.close()
  sys.exit(0)
