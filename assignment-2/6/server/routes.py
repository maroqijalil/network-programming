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
