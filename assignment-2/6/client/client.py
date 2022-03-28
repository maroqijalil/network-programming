import argparse
from httpclient import HttpClient
import sys


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Connect HTTPClient on defined host and port')
  parser.add_argument('--host', help='specify the host that will be connected to', type=str, default='localhost')
  parser.add_argument('--port', help='specify the port which is used', type=int, default=8000)

  args = parser.parse_args()

  client = HttpClient(args.host, args.port)

  try:
    if client.connect():
      while True:
        print('>> ', end='')
        client.get(input())

  except KeyboardInterrupt:
    sys.exit(0)
