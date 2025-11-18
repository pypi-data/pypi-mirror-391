"""Module providing a lazy-loaded attribute wrapper."""

from __future__ import annotations

from threading import RLock
from typing import TYPE_CHECKING, Any, NoReturn, final

if TYPE_CHECKING:
    from collections.abc import Callable

    from lazy_bear.lazy_imports import LazyLoader

_lock = RLock()


@final
class NotFoundType:
    """Sentinel type for not found attributes."""

    def __repr__(self) -> str:
        return "<NOT_FOUND>"


NOT_FOUND: NotFoundType = NotFoundType()


@final
class LazyAttr:
    """A lazy-loaded attribute from a LazyLoader module."""

    __slots__: tuple = ("_attr_name", "_cached_attr", "_loader")

    _loader: LazyLoader
    _attr_name: str
    _cached_attr: Any

    def __init__(self, n: str, loader: LazyLoader) -> None:  # pragma: no cover
        """Initialize a lazy-loaded attribute."""
        object.__setattr__(self, "_loader", loader)
        object.__setattr__(self, "_attr_name", n)
        object.__setattr__(self, "_cached_attr", None)

    @property
    def _attr(self) -> Any:  # pragma: no cover
        """Get the lazy-loaded attribute.

        This will load the attribute from the module if it hasn't been loaded yet.
        It will also replace the reference in the parent's globals to point to the
        loaded attribute for future accesses, basically getting rid of the LazyAttr wrapper.

        We want to get rid of the wrapper to avoid overhead on future accesses.

        Pytest will make this tricky to test since it frontloads modules and will
        trip this method early.
        """
        cached = self._cached_attr
        if cached is not None:
            return cached

        with _lock:
            if self._cached_attr is None:
                self._cached_attr = getattr(self._loader._load(), self._attr_name, NOT_FOUND)
                parent_globals: dict[str, Any] = self._loader._parent_globals
                global_attr: Any | NotFoundType = parent_globals.get(self._attr_name, NOT_FOUND)
                if global_attr is not NOT_FOUND and global_attr is self:
                    parent_globals[self._attr_name] = self._cached_attr
            if self._cached_attr is NOT_FOUND:
                raise AttributeError(f"Attribute '{self._attr_name}' not found in module '{self._loader._name}'")
            return self._cached_attr

    def _ensure_loaded(self) -> Any:
        """Ensure the attribute is loaded and return it.

        Returns:
            Any: Load the attribute if not already loaded, otherwise return the cached value.
        """
        return self._cached_attr if self._cached_attr is not None else self._attr

    @property
    def value(self) -> Any:  # pragma: no cover
        """Get the lazy-loaded attribute value."""
        return self._ensure_loaded()

    def unwrap(self) -> Any:  # pragma: no cover
        """Alias for value to get the lazy-loaded attribute."""
        return self._ensure_loaded()

    @property
    def __class__(self) -> type:  # pragma: no cover
        """Return the class of the wrapped value for transparent type checking.

        THIS BREAKS PICKLE AND COPY MODULES! BE AWARE OF THIS! BUT I DO NOT CARE!

        This will allow things like isinstance() and issubclass() to work as expected.
        Obviously it is not ideal but this helps to address some edge cases where
        the item is not unwrapped before type checking. Ideally the item would
        be extracted and the wrapper discarded but that is not always possible.
        Like within a local scope for example (within a function).

        __wrapped__ will not fix isinstance checks there needs to be a way to bridge
        the gap when the wrapper is still present.

        Honestly, I do not care about pickle or copy support here, if you need
        those you can unwrap the attribute manually before pickling/copying.

        All of this is a work in progress so maybe we can figure out a way to do
        this. If you wanna suggest something better, please let me know but
        just saying "documentation" is not a solution here, we want this to be
        as seamless as possible.

        I'm not going to change this unless you give me a better solution. Got it?  :D <3
        """
        if self._cached_attr is not None:
            return self._cached_attr.__class__
        return type(self)

    @__class__.setter
    def __class__(self, value: type) -> NoReturn:  # pragma: no cover
        raise TypeError("Cannot set __class__ on LazyAttr")

    def __reduce_ex__(self, protocol: Any) -> NoReturn:
        """Prevent pickling of LazyAttr with helpful error message."""
        raise TypeError(
            "LazyAttr cannot be pickled directly due to __class__ override. "
            "Use .value or .unwrap() to get the underlying object first."
        )

    @property
    def __wrapped__(self) -> Any:  # pragma: no cover
        """PEP 8 standard attribute for accessing wrapped object.

        This will trigger the loading of the attribute if it hasn't been loaded yet.
        """
        return self._ensure_loaded()

    def __call__(self, *args, **kwargs) -> Any:
        """Call the lazy-loaded attribute if it is callable."""
        target: Callable[..., Any] = self._ensure_loaded()
        if not callable(target):
            raise TypeError(f"Attribute '{self._attr_name}' is not callable.")
        return target(*args, **kwargs)

    def __getattr__(self, name: str) -> Any:  # pragma: no cover
        if name in self.__slots__:
            return super().__getattribute__(name)
        attr = self._ensure_loaded()
        return getattr(attr, name)

    def __setattr__(self, name: str, value: Any) -> None:  # pragma: no cover
        if name in self.__slots__:
            super().__setattr__(name, value)
            return
        if self._cached_attr is None:
            raise AttributeError(f"Cannot set attribute '{name}' before '{self._attr_name}' is loaded.")
        attr = self._ensure_loaded()
        setattr(attr, name, value)

    def __dir__(self) -> list[str]:  # pragma: no cover
        """List the attributes of the lazy-loaded attribute.

        This will trigger the loading of the attribute if it hasn't been loaded yet.
        """
        return dir(self._ensure_loaded())

    def __getitem__(self, key: str) -> Any:  # pragma: no cover
        return self._ensure_loaded()[key]

    def __setitem__(self, key: str, value: Any) -> None:  # pragma: no cover
        self._ensure_loaded()[key] = value

    def __iter__(self):  # pragma: no cover
        return iter(self._ensure_loaded())

    def __contains__(self, item: object) -> bool:  # pragma: no cover
        return item in self._ensure_loaded()

    def __len__(self) -> int:  # pragma: no cover
        return len(self._ensure_loaded())

    def __or__(self, other: Any) -> Any:  # pragma: no cover
        return self._ensure_loaded() | other

    def __ror__(self, other: Any) -> Any:  # pragma: no cover
        return other | self._ensure_loaded()

    def __eq__(self, other: object) -> bool:  # pragma: no cover
        return self._ensure_loaded() == other

    def __ne__(self, other: object) -> bool:  # pragma: no cover
        return self._ensure_loaded() != other

    def __hash__(self) -> int:  # pragma: no cover
        return hash(self._ensure_loaded())

    def __int__(self) -> int:  # pragma: no cover
        return int(self._ensure_loaded())

    def __float__(self) -> float:  # pragma: no cover
        return float(self._ensure_loaded())

    def __repr__(self) -> str:  # pragma: no cover
        if self._cached_attr is None:
            return f"<lazy attribute '{self._attr_name}' from module '{self._loader._name}' (Not loaded yet)>"  # pyright: ignore[reportPrivateUsage]
        return repr(self._cached_attr)

    def __str__(self) -> str:  # pragma: no cover
        return str(self._ensure_loaded())


__all__ = ["LazyAttr"]
