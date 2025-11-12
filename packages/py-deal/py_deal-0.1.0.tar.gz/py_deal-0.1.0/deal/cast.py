# casting.py
from __future__ import annotations

import json
from typing import Any, get_args, get_origin

from .exceptions import EnvValidationError


def cast_env_value(value: str, target_type: Any) -> Any:
    """
    Convert a string coming from .env into the target_type declared in the dataclass.
    Supports: str, int, float, bool, Optional[T], list[T] (comma-separated), dict[K, V] (JSON).
    """
    origin = get_origin(target_type)

    # Handle Optional[T] / Union[T, None]
    if origin is not None:
        args = get_args(target_type)

        # list[T]
        if origin is list:
            return _cast_list(value, args)

        # dict[K, V]
        if origin is dict:
            return _cast_dict(value, args)

        # Union[...] ⇒ suportamos Optional[T]
        non_none = [a for a in args if a is not type(None)]  # noqa: E721
        if len(non_none) == 1:
            return cast_env_value(value, non_none[0])
        raise EnvValidationError(f"Unsupported union type: {target_type!r}")

    # scalar
    return _cast_scalar(value, target_type)


def _cast_scalar(value: str, target_type: Any) -> Any:
    """Cast a single scalar value (str, int, float, bool)."""
    if target_type is str:
        return value
    if target_type is int:
        return int(value)
    if target_type is float:
        return float(value)
    if target_type is bool:
        return value.lower() in ("1", "true", "yes", "y", "on")
    # unknown type → return raw
    return value


def _cast_list(value: str, args: tuple[Any, ...]) -> list[Any]:
    """
    Cast a comma-separated string into a list of the given element type.
    Example .env: TAGS=foo,bar,baz
    """
    if not args:
        raise EnvValidationError("List field must specify an element type, e.g. list[str].")

    elem_type = args[0]
    raw_items = [item.strip() for item in value.split(",") if item.strip()]

    return [cast_env_value(item, elem_type) for item in raw_items]

def is_any_type(t: Any) -> bool:
    """
    Return True if t represents an 'any' type, even if the user wrote `any` (built-in)
    instead of `typing.Any`.
    """
    if t is Any:
        return True
    # user may have used lowercase built-in `any`
    if t is any:  # type: ignore[name-defined]
        return True
    # sometimes annotations can come as strings
    if isinstance(t, str) and t.lower() == "any":
        return True
    return False

def _cast_dict(value: str, args: tuple[Any, ...]) -> dict[Any, Any]:
    """
    Cast a JSON string into a dict.
    Example .env: DB_CONFIG={"host": "localhost", "port": 5432}
    """
    if not value.strip():
        return {}

    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as e:
        raise EnvValidationError(f"Invalid JSON for dict field: {value!r}") from e

    # If no key/value types were provided, return as-is
    if not args:
        return parsed

    key_type, val_type = args

    casted: dict[Any, Any] = {}
    for k, v in parsed.items():
        # keys: only cast if a type was really specified
        if key_type is Any:
            casted_key = k
        else:
            casted_key = cast_env_value(str(k), key_type)

        # values: if the user said "Any", keep what JSON gave us
        if is_any_type(val_type):
            casted_val = v
        else:
            # if it's already a scalar (int, float, bool, str), cast;
            # if it's nested (dict/list), you could extend here later
            if isinstance(v, (str, int, float, bool)):
                casted_val = cast_env_value(str(v), val_type)
            else:
                casted_val = v

        casted[casted_key] = casted_val

    return casted
