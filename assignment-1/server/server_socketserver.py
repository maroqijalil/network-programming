import argparse
import socketserver
import sys
import utils


class Server(socketserver.BaseRequestHandler):
  def handle(self):
    data = self.request.recv(1024)
    print(self.client_address, data.decode('utf-8'))

    utils.handle_send_file(self.request, data)


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Run TCPServer on defined host and port')
  parser.add_argument('--host', help='specify the host that will be used', type=str, default='localhost')
  parser.add_argument('--port', help='specify the port which is used', type=int, default=5001)

  args = parser.parse_args()

  with socketserver.TCPServer((args.host, args.port), Server) as server:
    try:
      server.serve_forever()

    except KeyboardInterrupt:
      sys.exit(0)
