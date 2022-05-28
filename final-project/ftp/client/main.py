import argparse
import sys
from ftp import FTPClient


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Connect HTTPClient on defined host and port')
  parser.add_argument('--host', help='specify the host that will be connected to', type=str, default='localhost')
  parser.add_argument('--port', help='specify the port which is used', type=int, default=21)

  args = parser.parse_args()

  try:
    client = FTPClient(args.host, args.port)

    if client.connect():
      client.run()

  except Exception as e:
    print(e)