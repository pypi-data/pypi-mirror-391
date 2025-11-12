from __future__ import annotations

import os
from dataclasses import fields
from typing import Any, ClassVar, Optional, Type, TypeVar

from dotenv import load_dotenv, dotenv_values

from .cast import cast_env_value
from .exceptions import EnvValidationError

# default behavior: try to load .env from current working directory
load_dotenv()

T = TypeVar("T")

class _ConfigMeta(type):
    def __str__(cls) -> str:
        if not hasattr(cls, "settings") or not hasattr(cls, "_should_mask"):
            return cls.__name__

        if cls.settings is None:
            return "Config not loaded yet."

        header = f"=== Loaded {cls.settings.__class__.__name__} ==="
        lines: list[str] = []
        for f in fields(cls.settings):
            name = f.name
            value = getattr(cls.settings, name)
            if cls._should_mask(name):
                masked = cls._mask_value(str(value))
                lines.append(f"{name}={masked}")
            else:
                lines.append(f"{name}={value!r}")
        return header + "\n" + "\n".join(lines)

    def __repr__(cls) -> str:
        if not hasattr(cls, "settings") or cls.settings is None:
            return "Config(not loaded)"
        parts: list[str] = []
        for f in fields(cls.settings):
            name = f.name
            value = getattr(cls.settings, name)
            parts.append(f"{name}={value!r}")
        return f"{cls.settings.__class__.__name__}({', '.join(parts)})"



class Config(metaclass=_ConfigMeta):
    """
    Static-like config holder.

    Example usage:
        from myenvconfig import Config
        from dataclasses import dataclass

        @dataclass
        class Settings:
            API_KEY: str
            DEBUG: bool

        Config.load(Settings)  # or Config.load(Settings, env_path=".env.local")
        print(Config.settings.API_KEY)
        print(Config)
    """

    # The schema dataclass
    settings: ClassVar[Optional[Any]] = None
    _hidden_substrings: ClassVar[list[str]] = ["KEY"]

    @classmethod
    def load(
        cls,
        schema: Type[T],
        env_path: Optional[str] = None,
        hidden_substrings: Optional[list[str]] = None,
    ) -> T:
        """
        Load environment variables into the provided dataclass schema.

        :param schema: dataclass type to be instantiated from environment variables.
        :param env_path: optional path to a .env file to load first.
        :param hidden_substrings: list of substrings that, if found in a field name,
                                  will cause its value to be masked in __str__. Defaults to ["KEY"].
        """

        file_values: dict[str, str] = {}
        if env_path:
            # load into process env (keeps behavior for normal use)
            load_dotenv(env_path, override=True)
            # but also read JUST this file, so tests don't leak env vars
            file_values = dotenv_values(env_path)
        
        if hidden_substrings is not None:
            cls._hidden_substrings = hidden_substrings

        data: dict[str, Any] = {}
        for f in fields(schema):
            if file_values:
                # when env_path is provided, trust ONLY that file
                env_value = file_values.get(f.name)
            else:
                # normal mode: read from process environment
                env_value = os.getenv(f.name)

            if env_value is None:
                raise EnvValidationError(f"Missing env var: {f.name}")
            try:
                data[f.name] = cast_env_value(env_value, f.type)
            except ValueError as e:
                raise EnvValidationError(
                    f"Invalid value for {f.name}: {env_value} ({e})"
                ) from e

        instance = schema(**data)
        cls.settings = instance
        return instance


    @classmethod
    def _should_mask(cls, field_name: str) -> bool:
        """Return True if this field name matches any of the configured hidden substrings."""
        for substr in cls._hidden_substrings:
            if substr and substr in field_name:
                return True
        return False

    @staticmethod
    def _mask_value(value: str) -> str:
        """
        Mask value for debug output.
        Shows the first 3 characters, then asterisks.
        """
        if not value:
            return "***"
        if len(value) <= 3:
            return value + "***"
        return value[:3] + "*" * 5
