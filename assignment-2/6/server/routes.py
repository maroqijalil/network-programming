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

routes: List[Route] = [
  create_route_file('/index.html', ['/', 'index.html']),
  create_route_file('/dataset/brain.jpeg'),
  create_route_file('/dataset/lagu.mp3'),
  create_route_file('/dataset/project.pdf'),
  create_route_file('/dataset/test.txt')
]
