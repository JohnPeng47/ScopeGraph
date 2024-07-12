from dataclasses import dataclass, asdict
from typing import Optional, List

from src.utils import TextRange
from src.graph import NodeKind


def parse_from(buffer: bytearray, range: TextRange) -> str:
    return buffer[range.start_byte : range.end_byte].decode("utf-8")


def parse_alias(buffer: bytearray, range: TextRange):
    return buffer[range.start_byte : range.end_byte].decode("utf-8")


def parse_name(buffer: bytearray, range: TextRange):
    return buffer[range.start_byte : range.end_byte].decode("utf-8")


class LocalImportStmt:
    """
    Represents a local import statement of the form:

    from <from_names> import <names> as <alias>
    from module import name1, name2, name3 as alias
    """

    def __init__(
        self,
        range: TextRange,
        names: List[str],
        from_name: List[str] = "",
        aliases: Optional[List[str]] = [],
    ):
        self.range = range
        self.from_name = from_name
        self.aliases = aliases
        self.names = names

    # TODO: these are the serialization methods to convert to ScopeNode
    def to_node(self):
        json_node = {
            "range": self.range.dict(),
            "type": NodeKind.IMPORT,
            "data": {
                "from_name": self.from_name,
                "aliases": self.aliases,
                "names": self.names,
            },
        }
        # print("JSON_NODE: ", json_node)
        return json_node

    # Technically, this is the only python specific method
    def __str__(self):
        from_name = f"from {self.from_name} " if self.from_name else ""
        # TODO: fix this
        alias_str = f" as {self.aliases}" if self.aliases else ""

        names = ", ".join(self.names)

        return f"{from_name}import {names}{alias_str}"
