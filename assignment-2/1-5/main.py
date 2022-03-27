import re
from utils import HttpClient


def run_program(using_ssl):
  client = HttpClient("www.its.ac.id", using_ssl)
  header = client.request_route('/', using_ssl)

  print("Host: www.its.ac.id")
  response_statuses = header.splitlines()[0].split(' ')
  content_encoding = "Content-Encoding: "
  for line in header.splitlines():
    if line.__contains__("Content-Encoding"):
      contents = line.split(' ')

      if len(contents) > 1:
        content_encoding += contents[1]
  
  print("Response-Status:", end="")
  for index in range(1, len(response_statuses)):
    print(f' {response_statuses[index]}', end="")
  print("")
  print(content_encoding)
  print(f'HTTP-Version: {response_statuses[0]}')
  
  client = HttpClient("classroom.its.ac.id", using_ssl)
  header = client.request_route('/', using_ssl)

  print("")
  print("Host: classroom.its.ac.id")
  print("Content-Type-Charset: ", end="")
  for line in header.splitlines():
    if line.__contains__("Content-Type"):
      contents = re.findall(r'charset=[\w\.-]+', line)

      if len(contents) > 0:
        print(contents[0][8:])
      else:
        print("")


if __name__ == '__main__':
  run_program(False)

  print("")
  print("Using SSL")
  run_program(True)
