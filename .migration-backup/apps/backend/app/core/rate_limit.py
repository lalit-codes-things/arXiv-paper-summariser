from __future__ import annotations

import importlib.util
from collections.abc import Callable
from typing import Any, TypeVar

F = TypeVar('F', bound=Callable[..., Any])

if importlib.util.find_spec('slowapi') is not None:
    from slowapi import Limiter
    from slowapi.util import get_remote_address

    limiter = Limiter(key_func=get_remote_address)
else:
    class _NoopLimiter:
        def limit(self, _rule: str) -> Callable[[F], F]:
            def decorator(func: F) -> F:
                return func
            return decorator

    limiter = _NoopLimiter()
