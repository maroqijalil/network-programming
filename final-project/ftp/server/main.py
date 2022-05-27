from utils import Config
from ftp import FTPServer


if __name__ == '__main__':
  try:
    config = Config('./ftp.conf')

    server = FTPServer(config.get())

    if server.connect():
      server.run()
  
  except Exception as e:
    print(e)
