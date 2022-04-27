import sys
import config
from ftp import FTP

if __name__ == '__main__':
  conf = config.get_config('./ftp.conf')

  try:
    ftp = FTP(
      conf['ftp']['host'],
      int(conf['ftp']['port'])
    )

    is_success = ftp.login(
      conf['ftp']['user'],
      conf['ftp']['passwd']
    )

    if not is_success:
      raise Exception("user not logged in")
  
    for response in ftp.responses:
      if '220' in response:
        message = response.replace('220', '').strip(' ()')
        print(message)

  except Exception:
    sys.exit(1)

  except KeyboardInterrupt:
    sys.exit(0)
