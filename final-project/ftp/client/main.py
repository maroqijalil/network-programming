import argparse
import sys
from ftp import FTPClient


def get_ftp(args: argparse.Namespace) -> FTPClient:
  ftp = FTPClient(args.host, args.port, "files")

  if ftp.login(args.user, args.passwd):
    return ftp

  else:
    raise Exception("user not logged-in")


def get_input_by_confirm(confirm, determine, default = ""):
  print(confirm, end='')
  command = input()

  if not any(avail == command for avail in ['y', 'n', '']):
    raise Exception("input isn't valid")

  result = default
  if command == 'n':
    print(determine, end='')
    result = input()
  
  return result


def problem_1(args: argparse.Namespace):
  ftp = get_ftp(args)
  print(ftp.get_content("220").strip(" ()"))


def problem_2(args: argparse.Namespace):
  ftp = get_ftp(args)

  ftp.send(['RMD files/test1\r\n'])
  print(ftp.get_content("215"))


def problem_3(args: argparse.Namespace):
  dirname = get_input_by_confirm(
    "using default folder? (y/n) ",
    "which folder it is? "
  )

  ftp = get_ftp(args)

  print(f"\ncontents of /{dirname}")
  ftp.ls(dirname)


def problem_4(args: argparse.Namespace):
  filename = get_input_by_confirm(
    "using default file to upload? (y/n) ",
    "what is the filename? ",
    "baymax.jpg"
  )

  targetdir = get_input_by_confirm(
    "using default target folder? (y/n) ",
    "where is the target folder? "
  )

  ftp = get_ftp(args)

  print("\nstoring", filename)
  ftp.store(filename, targetdir)
  print("success to store", filename)


def problem_5(args: argparse.Namespace):
  dirname = get_input_by_confirm(
    "create default folder? (y/n) ",
    "what is the detail folder? ",
    "test1"
  )

  ftp = get_ftp(args)

  print(f"\ncreating /{dirname}")
  if ftp.mkdir(dirname):
    print("success")
  else:
    print("fail")


def problem_6(args: argparse.Namespace):
  ftp = get_ftp(args)

  ftp.send(['PWD\r\n'])


def problem_7(args: argparse.Namespace):
  source = get_input_by_confirm(
    "rename the default folder? (y/n) ",
    "what the folder it is? ",
    "test1"
  )

  target = get_input_by_confirm(
    "using default name of target folder? (y/n) ",
    "what is the name of target folder name? ",
    "test2"
  )

  ftp = get_ftp(args)

  print(f"\nrenaming /{source} to be /{target}")
  if ftp.rename(source, target):
    print("success")
  else:
    print("fail")


def problem_8(args: argparse.Namespace):
  dirname = get_input_by_confirm(
    "delete default folder? (y/n) ",
    "what is the detail folder? ",
    "test2"
  )

  ftp = get_ftp(args)

  print(f"\nremoving /{dirname}")
  if ftp.rmdir(dirname):
    print("success")
  else:
    print("fail")


def problem_9(args: argparse.Namespace):
  filename = get_input_by_confirm(
    "delete default folder? (y/n) ",
    "what is the detail folder? ",
    "test2"
  )

  ftp = get_ftp(args)

  ftp.retreive(filename)


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Connect HTTPClient on defined host and port')
  parser.add_argument('--host', help='specify the host that will be connected to', type=str, default='localhost')
  parser.add_argument('--port', help='specify the port which is used', type=int, default=21)
  parser.add_argument('--user', help='specify the username that will be used to login', type=str, default='netpro')
  parser.add_argument('--passwd', help='enter the password corespond with the user', type=str, default='123')

  args = parser.parse_args()
  if ('--user' in vars(args) and '--passwd' not in vars(args)):
    parser.error('the --user argument requires the --passwd')

  try:
    while True:
      print('>> ', end='')
      command = input()

      try:
        if "1" in command:
          problem_1(args)

        if "2" in command:
          problem_2(args)

        if "3" in command:
          problem_3(args)

        if "4" in command:
          problem_4(args)

        if "5" in command:
          problem_5(args)

        if "6" in command:
          problem_6(args)

        if "7" in command:
          problem_7(args)

        if "8" in command:
          problem_8(args)

        if "9" in command:
          problem_9(args)

      except Exception as e:
        print(e)

  except KeyboardInterrupt:
    print("")
    sys.exit(0)
