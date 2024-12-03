from math import ceil

from fastapi import FastAPI, Request, Response
from fastapi.routing import APIRoute

from backend.common.exception import errors


def ensure_unique_route_names(app: FastAPI) -> None:
    """
    Check that the route name is unique

    :param app:
    :return:
    """
    temp_routes = set()
    for route in app.routes:
        if isinstance(route, APIRoute):
            if route.name in temp_routes:
                raise ValueError(f'Non-unique route name: {route.name}')
            temp_routes.add(route.name)


async def http_limit_callback(request: Request, response: Response, expire: int):
    """
    Default callback function when requesting limits

    :param request:
    :param response:
    :param expire: milliseconds remaining
    :return:
    """
    expires = ceil(expire / 1000)
    raise errors.HTTPError(code=429, msg='Requests are too frequent, please try again later', headers={'Retry-After': str(expires)})
