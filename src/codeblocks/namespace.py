from config import NAMESPACE_DELIMETERS, LANGUAGE
from pathlib import Path

delimiter = NAMESPACE_DELIMETERS[LANGUAGE]


class NameSpace:
    def __init__(self, parent: str, child: str = ""):
        self.parent = parent.split(delimiter)
        self.child = child.split(delimiter)

    def to_path(self):
        return Path(*self.parent)

    @property
    def root(self):
        return self.parent[0]

    def __hash__(self):
        return hash(tuple(self.parent, self.child))

    def __str__(self):
        return delimiter.join(self.parent + self.child)
