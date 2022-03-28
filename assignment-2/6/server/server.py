import socket
import select
import sys
import utils


if __name__ == '__main__':
  config = utils.get_config('./httpserver.conf')

  server = HttpServer(
    config['server']['host'],
    int(config['server']['port'])
  )

  try:
    if server.connect():
      while True:
        server.run()

  except KeyboardInterrupt:
    sys.exit(0)
