from pydantic import BaseModel

from dataclasses import dataclass
from typing import TypeAlias, Tuple
import json


SymbolId: TypeAlias = str


@dataclass
class Point:
    row: int
    col: int


class TextRange(BaseModel):
    start_byte: int
    end_byte: int
    start_point: Point
    end_point: Point

    def __init__(
        self,
        *,
        start_byte: int,
        end_byte: int,
        start_point: Tuple[int, int],
        end_point: Tuple[int, int]
    ):
        super().__init__(
            start_byte=start_byte,
            end_byte=end_byte,
            start_point=Point(*start_point),
            end_point=Point(*end_point),
        )

    def contains(self, range: "TextRange"):
        return range.start_byte >= self.start_byte and range.end_byte <= self.end_byte


def load_sys_modules(lang):
    SYS_MODULES_LIST = "src/languages/{lang}/sys_modules.json"

    with open(SYS_MODULES_LIST.format(lang=lang), "r") as file:
        return json.loads(file.read())["modules"]
