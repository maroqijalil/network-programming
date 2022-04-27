import argparse
import sys
import os
from typing import Tuple
from ftp import FTPClient


def get_ftp(args: argparse.Namespace) -> FTPClient:
  ftp = FTPClient(args.host, args.port, "files")

  if ftp.login(args.user, args.passwd):
    return ftp
  else:
    raise Exception("user not logged-in")


def problem_1(args: argparse.Namespace):
  ftp = get_ftp(args)

  message = ftp.get_response("220").replace("220", "").strip(" ()")
  print(message)


def problem_2(args: argparse.Namespace):
  ftp = get_ftp(args)

  ftp.send(['SYST\r\n'])
  print("success")

def problem_3(args: argparse.Namespace):
  ftp = get_ftp(args)

  ftp.ls()


def problem_4(args: argparse.Namespace, command):
  ftp = get_ftp(args)
  commands = command.split(" ")
  file_name = "baymax.jpg"
  if len(commands) > 1:
    file_name = commands[1]

  ftp.store(file_name)
  print("successfully store", file_name)


def problem_5(args: argparse.Namespace):
  ftp = get_ftp(args)

  if ftp.mkdir("test1"):
    print("success")
  else:
    print("fail")


def problem_6(args: argparse.Namespace):
  ftp = get_ftp(args)

  ftp.send(['PWD\r\n'])


def problem_7(args: argparse.Namespace):
  ftp = get_ftp(args)

  if ftp.rename("test1", "test2"):
    print("success")
  else:
    print("fail")

def problem_8(args: argparse.Namespace):
  ftp = get_ftp(args)

  if ftp.remove("test2"):
    print("success")
  else:
    print("fail")


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
          problem_4(args, command)

        if "5" in command:
          problem_5(args)

        if "6" in command:
          problem_6(args)

        if "7" in command:
          problem_7(args)

        if "8" in command:
          problem_8(args)

      except Exception as e:
        print(e)

  except KeyboardInterrupt:
    print("")
    sys.exit(0)
