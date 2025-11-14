from __future__ import annotations
from typing import Callable, Iterable, List, Sequence, TypeVar, Optional

T = TypeVar("T")
K = TypeVar("K")

def decorate(items: Iterable[T], key: Optional[Callable[[T], K]]) -> List[tuple[K, T]]:
    return [(key(x) if key else x, x) for x in items]  # type: ignore[misc]

def undecorate(pairs: Iterable[tuple[K, T]], reverse: bool = False) -> List[T]:
    out = [x for _, x in pairs]  # type: ignore[misc]
    if reverse:
        out.reverse()
    return out