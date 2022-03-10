import socketserver
import sys
import utils


class Server(socketserver.BaseRequestHandler):
  def handle(self):
    data = self.request.recv(1024)
    print(self.client_address, data.decode('utf-8'))

    utils.handle_send_file(self.request, data)


if __name__ == "__main__":
  with socketserver.TCPServer(('localhost', 5001), Server) as server:
    try:
      server.serve_forever()

    except KeyboardInterrupt:
      sys.exit(0)
