from __future__ import annotations

from dataclasses import dataclass

from ev.runtime.logging import get_logger

__all__: tuple[str, ...] = ("ObjectRef",)


@dataclass
class ObjectRef:
    """Reference to a python object in some module (or file).

    Examples:
        - `file.py` - Execute the file directly via __main__ guard.
        - `file.py:function_name` - Execute specific function in the file.
        - `file.py:ClassName` - Instantiate and run class (requires `__call__` method).
        - `file.py:ClassName.method_name` - Execute specific method on class.
        - `module.submodule:function` - Import from module path and execute.
    """

    module: str
    symbol: str | None = None

    @staticmethod
    def parse(ref: str) -> ObjectRef:
        """Parses an object reference from argument from the form `file.py:object`."""
        logger = get_logger()
        logger.debug("Parsing object reference: %s", ref)

        if ref.find(":") > 1:
            file, symbol = ref.split(":", 1)
            logger.debug("Parsed file: %s, symbol: %s", file, symbol)
        else:
            file, symbol = ref, None
            logger.debug("Parsed file: %s, no symbol specified", file)

        return ObjectRef(file, symbol)
