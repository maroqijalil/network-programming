import os
import socketserver

SERVER_HOST = 'localhost'
SERVER_PORT = 5000
BUF_SIZE = 1024
FORMAT = 'utf-8'

class TCPSocketHandler(socketserver.BaseRequestHandler):
  def handle(self):
    self.data = self.request.recv(BUF_SIZE).decode()
    print(self.data[:-1])
    if self.data:
      cmd = self.data.split(" ")
      file_name = cmd[1][:-1]
      current_path = os.path.dirname(__file__)
      file_path = current_path + r'{}'.format("\\dataset\\") + r'{}'.format(file_name)

      if not os.path.exists(file_path):
        self.request.send("file doesn't exist".encode())
      
      else:
        self.request.send(("file exist, start sending {}".format(file_name)).encode(FORMAT))

        file_size = os.path.getsize(file_path)
        header = ("\nfile-name: {},\nfile-size: {},\n\n\n".format(file_name, file_size))
        self.request.send(header.encode(FORMAT))
        
        if self.data != '':
          file = open(file_path, 'rb')
          self.data = file.read(BUF_SIZE)
          while self.data:
            self.request.send(self.data)
            self.data = file.read(BUF_SIZE)

if __name__ == "__main__":
    server = socketserver.TCPServer((SERVER_HOST, SERVER_PORT), TCPSocketHandler)
    server.serve_forever()