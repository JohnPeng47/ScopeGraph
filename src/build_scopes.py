from pydantic import BaseModel
from networkx import DiGraph
from tree_sitter import Query, Node

from typing import Dict, Optional, Iterator, List
from enum import Enum

from src.scope_resolution import (
    LocalScope,
    LocalDef,
    LocalImport,
    Reference,
    ScopeStack,
)
from src.graph import ScopeNode, NodeKind, EdgeKind
from src.utils import TextRange


class Scoping(str, Enum):
    GLOBAL = "global"
    HOISTED = "hoist"
    LOCAL = "local"


class ScopeGraph:
    def __init__(self, range: TextRange):
        # TODO: put all this logic into a separate Graph class
        self._graph = DiGraph()
        self._node_counter = 0

        self.root_idx = self.add_node(ScopeNode(range=range, type=NodeKind.SCOPE))

    def insert_local_scope(self, new: LocalScope) -> int:
        """
        Insert local scope to parent
        """
        parent_id = self.scope_by_range(new.range, self.root_idx)
        new_node = ScopeNode(range=new.range, type=NodeKind.SCOPE)
        new_id = self.add_node(new_node)

        self._graph.add_edge(new_id, parent_id, type=EdgeKind.ScopeToScope)

        return new_id

    def scope_by_range(self, range: TextRange, start: int) -> int:
        """
        Returns the smallest child
        """
        node = self.get_node(start)
        if node.range.contains(range):
            for child_id, attrs in [
                (src, attrs)
                for src, dst, attrs in self._graph.in_edges(start, data=True)
                if attrs["type"] == EdgeKind.ScopeToScope
            ]:
                if child := self.scope_by_range(range, child_id):
                    return child
            return start

        return None

    def scope_stack(self, start: int = None):
        """
        Returns stack of parent scope traversed
        """
        start = start if start else self.root_idx
        return ScopeStack(self._graph, start=start)

    def add_node(self, node: ScopeNode) -> int:
        """
        Adds node and increments node_counter for its id
        """
        id = self._node_counter
        self._graph.add_node(id, attrs=node.dict())

        self._node_counter += 1

        return id

    def get_node(self, idx: int):
        return ScopeNode(**self._graph.nodes[idx]["attrs"])


####### Parsing Scopes ########


class LocalDefCapture(BaseModel):
    index: int
    symbol: Optional[str]
    scoping: Scoping


class LocalRefCapture(BaseModel):
    index: int
    symbol: Optional[str]


def build_scope_graph(query: Query, root_node: Node, root: int) -> DiGraph:
    local_def_captures: List[LocalDefCapture] = []
    local_ref_captures: List[LocalRefCapture] = []
    local_scope_capture_index: Optional[int] = None
    local_import_capture_index: Optional[int] = None

    # capture_id -> range map
    capture_map: Dict[int, TextRange] = {}

    for i, (node, capture_name) in enumerate(query.captures(root_node)):
        capture_map[i] = TextRange(start=node.start_point[0], end=node.end_point[0])

        parts = capture_name.split(".")
        match parts:
            case [scoping, "definition", sym]:
                index = i
                symbol = sym
                scoping_enum = Scoping(scoping)

                l = LocalDefCapture(
                    index=index,
                    symbol=symbol,
                    scoping=scoping_enum,
                )
                local_def_captures.append(l)
            case [scoping, "definition"]:
                index = i
                symbol = None
                scoping_enum = Scoping(scoping)

                l = LocalDefCapture(
                    index=index,
                    symbol=symbol,
                    scoping=scoping_enum,
                )
                local_def_captures.append(l)
            case ["local", "reference", sym]:
                index = i
                symbol = sym

                l = LocalRefCapture(index=index, symbol=symbol)
                local_ref_captures.append(l)
            case ["local", "reference"]:
                index = i
                symbol = None

                l = LocalRefCapture(index=index, symbol=symbol)
                local_ref_captures.append(l)
            case ["local", "scope"]:
                local_scope_capture_index = i
            case ["local", "import"]:
                local_import_capture_index = i

    root_range = TextRange(start=root_node.start_point[0], end=root_node.end_point[0])
    scope_graph = ScopeGraph(root_range)

    # insert scopes first
    scope_graph.insert_local_scope(
        ScopeNode(range=capture_map[local_scope_capture_index], type=NodeKind.SCOPE)
    )
