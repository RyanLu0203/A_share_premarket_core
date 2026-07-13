from __future__ import annotations

from typing import Any, Callable

from fastapi import HTTPException


def safe_call(call: Callable[[], Any]) -> Any:
    try:
        return call()
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
