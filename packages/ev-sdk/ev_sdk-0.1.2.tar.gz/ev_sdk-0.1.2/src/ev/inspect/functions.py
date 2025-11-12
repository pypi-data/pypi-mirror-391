from __future__ import annotations

import argparse
import ast
import inspect
from datetime import datetime
from typing import TYPE_CHECKING, Any, ParamSpec, TypeVar, Union, get_args, get_origin

if TYPE_CHECKING:
    from collections.abc import Callable

__all__: tuple[str, ...] = ("parse_args",)

_P = ParamSpec("_P")
_R = TypeVar("_R")

# Supported scalar types and their corresponding annotations
_SCALAR_ANNOTATIONS = {
    str: "str",
    bool: "bool",
    int: "int",
    float: "float",
    object: "str",  # TODO(rchowell): support for object-annotated arguments
}

# Supported collection types for validation
_COLLECTION_ANNOTATIONS = {list, dict}


def parse_args(function: Callable[_P, _R], args: list[str]) -> dict[str, Any]:
    parser = _derive_parser(function)
    namespace = parser.parse_args(args)
    return vars(namespace)


def _parse_bool(value: str) -> bool:
    """Parse a string to boolean, accepting various formats."""
    if value.lower() == "true":
        return True
    elif value.lower() == "false":
        return False
    else:
        raise ValueError(f"Invalid boolean value: {value}")


def _parse_list(value: str) -> list[Any]:
    """Parse a string representation of a list."""
    try:
        parsed = ast.literal_eval(value)
        if not isinstance(parsed, list):
            raise ValueError(f"Value is not a list: {value}")
        return parsed
    except (ValueError, SyntaxError) as e:
        raise ValueError(f"Invalid list format: {value}") from e


def _parse_dict(value: str) -> dict[str, Any]:
    """Parse a string representation of a dict."""
    try:
        parsed = ast.literal_eval(value)
        if not isinstance(parsed, dict):
            raise ValueError(f"Value is not a dict: {value}")
        return parsed
    except (ValueError, SyntaxError) as e:
        raise ValueError(f"Invalid dict format: {value}") from e


def _parse_datetime(value: str) -> datetime:
    formats = [
        "%Y-%m-%d",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S.%fZ",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    raise ValueError(f"Could not parse datetime: {value}")


def _get_type_parser(annotation: type) -> Callable[[str], Any]:
    """Get the appropriate type parser for argparse based on the annotation."""
    if annotation == inspect._empty:
        return str
    elif annotation in _SCALAR_ANNOTATIONS:
        if annotation is bool:
            return _parse_bool
        return annotation
    elif annotation == datetime:
        return _parse_datetime

    # handle Optional[T] which is Union[T, None]
    ann_origin = get_origin(annotation)
    ann_args = get_args(annotation)
    if ann_origin is not None:
        if ann_origin is Union and type(None) in ann_args:
            non_none_types = [arg for arg in ann_args if arg is not type(None)]
            if len(non_none_types) == 1:
                return _get_type_parser(non_none_types[0])
        elif ann_origin is list:
            return _parse_list
        elif ann_origin is dict:
            return _parse_dict

    # fallback
    return str


def _derive_parser(function: Callable[_P, _R]) -> argparse.ArgumentParser:
    signature = inspect.signature(function)
    parser = argparse.ArgumentParser(prog=function.__name__)

    for name, param in signature.parameters.items():
        # skip self parameter for methods
        if name == "self":
            continue

        type_parser = _get_type_parser(param.annotation)

        if param.default is inspect._empty:
            # required argument: positional or --name
            parser.add_argument(
                f"--{name}",
                type=type_parser,
                required=True,
                help=f"Required {name} (can be specified as positional or --{name})",
            )
        else:
            # optional argument: positional or --name, with default
            parser.add_argument(
                f"--{name}",
                type=type_parser,
                nargs="?",
                default=param.default,
                help=f"Optional {name} (default: {param.default}, can be specified as positional or --{name})",
            )

    return parser
