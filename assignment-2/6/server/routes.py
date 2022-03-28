from typing import List
from httpserver import Response, Route


def create_route_file(filepath, additional_route = []) -> Route:
  def create_file_response(filename) -> Response:
    response = Response()

    content = ''
    with open(filename, 'r') as file:
      content = file.read()

    response.status_code = 200
    response.status = 'OK'
    response.type = 'text/html; charset=UTF-8'
    response.data_length = len(content)
    response.body = content

    return response

  route = Route(
    routes=[]
  )
