from enum import Enum
from typing import Literal

from fastapi import APIRouter

_global_index = 0


def route(
    method: Literal["GET", "POST", "PUT", "DELETE"],
    path: str,
    *,
    tags: list[str] | None = None,
):
    global _global_index
    _global_index += 1

    def decorator(func):
        func._route_info = {
            "index": _global_index,
            "method": method,
            "path": path,
            "tags": tags,
        }
        return func

    return decorator


class BaseRoutes:
    def __init__(self) -> None:
        # Lookup routes
        routes = []
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if callable(attr) and hasattr(attr, "_route_info"):
                route_info = getattr(attr, "_route_info")
                routes.append((route_info["index"], route_info, attr))
        self.routes = routes

    def register(self, router: APIRouter) -> None:
        # Register routes
        for _, route_info, endpoint in sorted(self.routes):
            router.add_api_route(
                path=route_info["path"],
                endpoint=endpoint,
                methods=[route_info["method"]],
                tags=route_info["tags"],
            )


class BaseRouter(APIRouter):
    def __init__(
        self,
        *,
        prefix: str = "",
        tags: list[str | Enum] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(prefix=prefix, tags=tags, **kwargs)

        # Lookup routes
        routes = []
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if callable(attr) and hasattr(attr, "_route_info"):
                route_info = getattr(attr, "_route_info")
                routes.append((route_info["index"], route_info, attr))

        # Register routes
        for _, route_info, endpoint in sorted(routes):
            self.add_api_route(
                path=route_info["path"],
                endpoint=endpoint,
                methods=[route_info["method"]],
                tags=route_info["tags"],
            )
