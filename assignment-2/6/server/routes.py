import os
from posixpath import dirname
from typing import List
from httpserver import Response, Route


def create_route_file(filepath, additional_route = []) -> Route:
  def create_response() -> Response:
    response = Response.get_file_response(filepath)

    response.status_code = 200
    response.status = 'OK'

    return response

  return Route(
    routes=[filepath] + additional_route,
    response_callback=create_response
  )

def create_route_dir(filepath, additional_route = []) -> Route:
  def create_response() -> Response:
    response = Response.get_file_response('/dir.html')

    response.body = response.body.replace(b'dirname', filepath.encode('utf-8'))
    listdir = ''
    listfile = ''

    fullpath = os.path.dirname(__file__) + filepath
    for _, directories, files in os.walk(fullpath):
      for directory in directories:
        listdir += f'<li>{directory}</li>\r\n'

      for file in files:
        listfile += f'<li>{file}</li>\r\n'

    if listdir == '':
      listdir = '-'
    if listfile == '':
      listfile = '-'

    response.body = response.body.replace(b'listdir', listdir.encode('utf-8'))
    response.body = response.body.replace(b'listfile', listfile.encode('utf-8'))

    response.content_length = len(response.body)

    response.status_code = 200
    response.status = 'OK'

    return response

  return Route(
    routes=[filepath] + additional_route,
    response_callback=create_response
  )

routes: List[Route] = [
  create_route_file('/index.html', ['/', 'index.html']),
  create_route_file('/dataset/brain.jpeg', ['dataset/brain.jpeg']),
  create_route_file('/dataset/lagu.mp3', ['dataset/lagu.mp3']),
  create_route_file('/dataset/project.pdf', ['dataset/project.pdf']),
  create_route_file('/dataset/test.txt', ['dataset/test.txt']),
  create_route_dir('/dataset', ['dataset'])
]
