import socketserver
import sys
import threading
import utils


class ThreadedServer(socketserver.BaseRequestHandler):
  def handle(self):
    print(threading.current_thread().name, self.request.getpeername(), end="")
    while True:
      try:
        data = self.request.recv(1024)
        if data:
          print(self.client_address, data.decode('utf-8'))

          utils.handle_send_file(self.request, data)
        else:
          self.request.close()
          break
      except Exception as e:
        print(e)
        break

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass
  
if __name__ == "__main__":
  server =  ThreadedTCPServer(('localhost', 5001), ThreadedServer)
  try:
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = False
    server_thread.start()
    print(len(threading.enumerate()))
  
  except KeyboardInterrupt:
      server_thread.daemon = True
      server.shutdown()
      sys.exit(0)