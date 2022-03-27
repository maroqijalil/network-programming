import re
from utils import HttpClient
from bs4 import BeautifulSoup


def run_program(using_ssl):
  client = HttpClient("www.its.ac.id", using_ssl)
  header = client.request_header_route('/')

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
  header = client.request_header_route('/')

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

  print("Get-Menus:")
  client = HttpClient("classroom.its.ac.id", True)
  body = client.request_route('/')
  soup = BeautifulSoup(body, features="lxml")

  for tag in soup.nav.ul.find_all('li'):
    sub_soup = BeautifulSoup(str(tag), features="lxml")
    print(sub_soup.find('a', {'class': 'dropdown-toggle'}).text)

    sub_soup = BeautifulSoup(str(tag), features="lxml")
    for subtag in sub_soup.find_all('a', {'class': 'dropdown-item'}):
      print(BeautifulSoup(str(subtag), features="lxml").text)
