from enum import Enum
from typing import List, Optional, NewType
from pydantic.dataclasses import dataclass

from scope_graph.scope_resolution.graph import Node
from scope_graph.moatless.epic_split import CodeNode
from scope_graph.utils import TextRange


ChunkNodeID = NewType("ChunkNodeID", str)


@dataclass
class ChunkMetadata:
    file_path: str
    file_name: str
    file_type: str
    category: str
    tokens: int
    span_ids: List[str]
    start_line: int
    end_line: int
    community: Optional[int] = None


class ChunkNode(Node):
    id: ChunkNodeID
    metadata: ChunkMetadata
    content: str

    @property
    def range(self):
        return TextRange(
            start_byte=0,
            end_byte=0,
            start_point=(self.metadata.start_line, 0),
            end_point=(self.metadata.end_line, 0),
        )

    def set_community(self, community: int):
        self.metadata.community = community

    def __hash__(self):
        return hash(self.id + "".join(self.metadata.span_ids))

    def __str__(self):
        return f"{self.id}"

    def to_node(self):
        return CodeNode(
            id=self.id,
            text=self.content,
            metadata=self.metadata.__dict__,
            content=self.content,
        )


class EdgeKind(str, Enum):
    ImportToExport = "ImportToExport"
