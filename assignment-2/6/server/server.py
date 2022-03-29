import routes
import config
from httpserver import HttpServer


if __name__ == '__main__':
  config = config.get_config('./httpserver.conf')

  server = HttpServer(
    config['server']['host'],
    int(config['server']['port'])
  )

  for route in routes.routes:
    server.add_route(route)

  if server.connect():
    server.run()
