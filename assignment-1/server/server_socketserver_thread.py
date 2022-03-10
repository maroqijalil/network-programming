import argparse
import socketserver
import sys
import threading
import utils


class Server(socketserver.BaseRequestHandler):
  def handle(self):
    try:
      data = self.request.recv(1024)
      if data:
        print(self.client_address, data.decode('utf-8'))

        utils.handle_send_file(self.request, data)

      else:
        self.request.close()

    except Exception:
      return


class ThreadedServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Run TCPServer on defined host and port')
  parser.add_argument('--host', help='specify the host that will be used', type=str, default='localhost')
  parser.add_argument('--port', help='specify the port which is used', type=int, default=5002)

  args = parser.parse_args()

  server = ThreadedServer((args.host, args.port), Server)

  try:
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = False
    server_thread.start()
  
  except KeyboardInterrupt:
    server.shutdown()
    sys.exit(0)
