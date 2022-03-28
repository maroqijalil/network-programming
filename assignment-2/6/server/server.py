import routes
import sys
import config
from httpserver import HttpServer


if __name__ == '__main__':
  config = config.get_config('./httpserver.conf')

  server = HttpServer(
    config['server']['host'],
    int(config['server']['port'])
  )

  server.add_route(routes.create_route_file('/index.html', ['/', 'index.html']))

  try:
    if server.connect():
      server.run()

  except KeyboardInterrupt:
    sys.exit(0)
