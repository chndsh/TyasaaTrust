"""Lightweight stubs for optional dependencies used during import-time.

These allow importing the `backend` package in environments where
FastAPI, Pydantic, SQLAlchemy, or pandas may not be installed.
"""
from __future__ import annotations

from typing import Any, Callable


class FakeRouteDecorator:
    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, fn: Callable) -> Callable:
        return fn


class APIRouter:  # pragma: no cover - import-time stub
    def __init__(self, *args, **kwargs):
        pass

    def get(self, *args, **kwargs):
        return FakeRouteDecorator()

    def post(self, *args, **kwargs):
        return FakeRouteDecorator()


class FastAPI:  # pragma: no cover - import-time stub
    def __init__(self, *args, **kwargs):
        pass

    def get(self, *args, **kwargs):
        return FakeRouteDecorator()

    def include_router(self, router: Any, prefix: str | None = None, tags: list | None = None):
        # no-op for import-time
        return None


class BaseModel:  # very small BaseModel stand-in
    def model_dump(self) -> dict[str, Any]:
        return self.__dict__


def Field(*args, **kwargs):  # mimic pydantic.Field by returning the default
    return kwargs.get("default", None)


class ConfigDict(dict):
    pass
