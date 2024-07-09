from src.build_scopes import build_scope_graph
from src.languages import PythonParse
from src.scope_resolution.definition import LocalDef
from src.scope_resolution.scope import LocalScope
from src.build_scopes import ScopeGraph
from src.utils import TextRange


def test_parent_scope():
    scope_graph = ScopeGraph(TextRange(start=1, end=6))

    scope1 = LocalScope(1, 5)
    scope2 = LocalScope(2, 4)
    scope3 = LocalScope(3, 4)
    scope4 = LocalScope(1, 4)

    scope_graph.insert_local_scope(scope1)
    scope_graph.insert_local_scope(scope2)
    scope_graph.insert_local_scope(scope3)
    scope_graph.insert_local_scope(scope4)

    graph_state = """
1 --ScopeToScope-> 0
2 --ScopeToScope-> 1
3 --ScopeToScope-> 2
4 --ScopeToScope-> 1
"""
    assert scope_graph.to_str() == graph_state
