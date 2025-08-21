from enum import Enum, EnumMeta
from itertools import islice
from typing import Union


def deep_merge(d1: dict, d2: dict) -> dict:
    """
    Recursively deep merges two dictionaries.
    Values from d2 will overwrite or be merged into d1.
    """
    result = d1.copy()  # Start with a shallow copy of dict1
    for key, value in d2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            # Both values are dicts: recurse
            result[key] = deep_merge(result[key], value)
        else:
            # Otherwise, override or add
            result[key] = value
    return result


def str_to_bool(s: Union[str, int]) -> bool:
    """
    Converts a string or integer into a boolean.
    """
    if isinstance(s, str):
        return s.lower() in ("true", "True", "yes", "Yes", "y", "Y", "1")
    elif isinstance(s, int):
        return bool(s)
    elif s is None:
        return False
    else:
        raise AttributeError(f"Can't handle object of type {type(s)}")


def str_is_bool(s: str) -> bool:
    """
    Determines whether a string is a boolean or not
    """
    return s in (
        "true",
        "True",
        "yes",
        "Yes",
        "y",
        "Y",
        "1",
        "false",
        "False",
        "no",
        "No",
        "n",
        "N",
        "0",
    )


def str_is_float(s: str) -> bool:
    """
    Determines whether a string is a float or not
    """
    try:
        float(s)
    except ValueError:
        return False

    return True


def wrap_in_html_tag(s: str, t: str) -> str:
    """Wraps the passed string in the passed html element tag."""

    return f"<{t}>{s}</{t}>"


class IndexableEnumMeta(EnumMeta):
    """
    Enum subclass that facilitates enums that are both convertible to strings (without needing to access the value
    attribute), and accessible via indexing (both integer indexing and slicing and dict-type access via strings).
    """

    def __getitem__(self, index):
        if isinstance(index, slice):
            return [
                self._member_map_[i]
                for i in islice(self._member_map_, index.start, index.stop, index.step)
            ]
        elif isinstance(index, int):
            try:
                return self._member_map_[next(islice(self._member_map_, index, index + 1))]
            except StopIteration as e:
                raise IndexError from e
        elif isinstance(index, str):
            return next(i for i, (_, v) in enumerate(self._member_map_.items()) if v == index)
        return self._member_map_[index]


class IndexableStrEnum(str, Enum, metaclass=IndexableEnumMeta):
    def __int__(self: IndexableEnumMeta):
        return next(i for i, (_, v) in enumerate(self._member_map_.items()) if v == self)

    """
    Implementation of the :class IndexableEnumMeta: class with a string mixin.

    Example:

    >>> class Level(IndexableStrEnum):
    ...     WARNING = "warning"
    ...     ERROR = "error"
    ...     ALERT = "alert"
    ...
    >>> Level[2]
    'alert'
    >>> Level["alert"]
    2
    >>> Level("alert")
    <Level.ALERT: 'alert'>
    >>> int(Level.ALERT)
    2
    """
