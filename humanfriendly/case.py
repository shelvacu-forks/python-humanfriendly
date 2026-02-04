# Human friendly input/output in Python.
#
# Author: Peter Odding <peter@peterodding.com>
# Last Change: April 19, 2020
# URL: https://humanfriendly.readthedocs.io

"""
Simple case insensitive dictionaries.

The :class:`CaseInsensitiveDict` class is a dictionary whose string keys
are case insensitive. It works by automatically coercing string keys to
:class:`CaseInsensitiveKey` objects. Keys that are not strings are
supported as well, just without case insensitivity.

At its core this module works by normalizing strings to lowercase before
comparing or hashing them. It doesn't support proper case folding nor
does it support Unicode normalization, hence the word "simple".
"""

# Standard library modules.
import collections
from collections.abc import Iterable, MutableMapping
from typing import Any, overload, TYPE_CHECKING, Final, Iterator

if TYPE_CHECKING:
    from _typeshed import SupportsKeysAndGetItem

# Public identifiers that require documentation.
__all__ = ("CaseInsensitiveDict", "CaseInsensitiveKey")


class CaseInsensitiveKey[T: (str, bytes)]:
    """
    Simple case insensitive dictionary key implementation.

    The :class:`CaseInsensitiveKey` class provides an intentionally simple
    implementation of case insensitive strings to be used as dictionary keys.

    If you need features like Unicode normalization or proper case folding
    please consider using a more advanced implementation like the :pypi:`istr`
    package instead.
    """

    wrapped: Final[T]
    normalized: Final[T]

    def __init__(self, value: T) -> None:
        """Create a :class:`CaseInsensitiveKey` object."""
        self.wrapped = value
        self.normalized = value.lower()

    def __hash__(self) -> int:
        """Get the hash value of the lowercased string."""
        return self.normalized.__hash__()

    def __eq__(self, other: Any) -> bool:
        """Compare two strings as lowercase."""
        if isinstance(other, CaseInsensitiveKey):
            # Fast path (and the most common case): Comparison with same type.
            return self.normalized == other.normalized
        else:
            return False


class CaseInsensitiveDict[KT: (str, bytes), VT](MutableMapping[KT, VT]):
    """
    Simple case insensitive dictionary implementation (that remembers insertion order).

    This class works by overriding methods that deal with dictionary keys to
    coerce string keys to :class:`CaseInsensitiveKey` objects before calling
    down to the regular dictionary handling methods. While intended to be
    complete this class has not been extensively tested yet.
    """

    wrapped: collections.OrderedDict[CaseInsensitiveKey[KT], VT]

    @classmethod
    @overload
    def fromkeys[T: (str, bytes)](
        cls, iterable: Iterable[T], value: None = None, /
    ) -> "CaseInsensitiveDict[T, Any]": ...

    @classmethod
    @overload
    def fromkeys[T: (str, bytes), V](
        cls, iterable: Iterable[T], value: V, /
    ) -> "CaseInsensitiveDict[T, V]": ...

    @classmethod
    def fromkeys[T: (str, bytes)](
        cls, iterable: Iterable[T], value: Any = None, /
    ) -> "CaseInsensitiveDict[T, Any]":
        res = CaseInsensitiveDict()
        for key in iterable:
            res[key] = value
        return res

    @staticmethod
    @overload
    def map_key(k: KT) -> CaseInsensitiveKey[KT]: ...

    @staticmethod
    @overload
    def map_key(k: Any) -> Any: ...

    @staticmethod
    def map_key(k: Any) -> Any:
        if isinstance(k, str):
            return CaseInsensitiveKey(k)
        elif isinstance(k, bytes):
            return CaseInsensitiveKey(k)
        else:
            return k

    @staticmethod
    def map_key_typed(k: KT) -> CaseInsensitiveKey[KT]:
        return CaseInsensitiveKey(k)

    @staticmethod
    def unmap_key(k: CaseInsensitiveKey[KT]) -> KT:
        return k.wrapped

    def __init__(
        self,
        other: "SupportsKeysAndGetItem[KT, VT]|Iterable[tuple[KT, VT]]" = {},
        /,
        **kw: VT,
    ):
        """Initialize a :class:`CaseInsensitiveDict` object."""
        self.wrapped = collections.OrderedDict()
        self.update(other, **kw)

    def popitem(self, last: bool = True) -> tuple[KT, VT]:
        key, val = self.wrapped.popitem(last)
        return (self.unmap_key(key), val)

    def move_to_end(self, key: KT, last: bool = True) -> None:
        self.wrapped.move_to_end(self.map_key_typed(key), last)

    def __getitem__(self, key: KT) -> VT:
        return self.wrapped[self.map_key_typed(key)]

    def __setitem__(self, key: KT, val: VT) -> None:
        self.wrapped[self.map_key_typed(key)] = val

    def __delitem__(self, key: KT) -> None:
        del self.wrapped[self.map_key_typed(key)]

    def __len__(self) -> int:
        return len(self.wrapped)

    def __iter__(self) -> Iterator[KT]:
        return map(self.unmap_key, self.wrapped)
