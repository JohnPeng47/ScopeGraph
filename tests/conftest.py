from pathlib import Path
import os
from typing import Dict
import mimetypes
import fnmatch

from llama_index.core import SimpleDirectoryReader
from scope_graph.moatless.epic_split import EpicSplitter
from scope_graph.moatless.settings import IndexSettings

from scope_graph.chunk_resolution.chunk_graph import ChunkGraph
from scope_graph.repo_resolution.repo_graph import RepoGraph
from scope_graph.utils import TextRange

import pytest


def range(start, end):
    return TextRange(
        start_byte=0, end_byte=0, start_point=(start, 0), end_point=(end, 0)
    )


@pytest.fixture
def chunk_nodes(repo_path: str):
    def file_metadata_func(file_path: str) -> Dict:
        file_path = file_path.replace(repo_path, "")
        if file_path.startswith("/"):
            file_path = file_path[1:]

        test_patterns = [
            "**/test/**",
            "**/tests/**",
            "**/test_*.py",
            "**/*_test.py",
        ]
        category = (
            "test"
            if any(fnmatch.fnmatch(file_path, pattern) for pattern in test_patterns)
            else "implementation"
        )

        return {
            "file_path": file_path,
            "file_name": os.path.basename(file_path),
            "file_type": mimetypes.guess_type(file_path)[0],
            "category": category,
        }

    reader = SimpleDirectoryReader(
        input_dir=repo_path,
        file_metadata=file_metadata_func,
        filename_as_id=True,
        required_exts=[".py"],  # TODO: Shouldn't be hardcoded and filtered
        recursive=True,
    )

    settings = IndexSettings()
    docs = reader.load_data()

    splitter = EpicSplitter(
        min_chunk_size=settings.min_chunk_size,
        chunk_size=settings.chunk_size,
        hard_token_limit=settings.hard_token_limit,
        max_chunks=settings.max_chunks,
        comment_strategy=settings.comment_strategy,
        repo_path=repo_path,
    )

    prepared_nodes = splitter.get_nodes_from_documents(docs, show_progress=True)


@pytest.fixture
def chunk_graph(repo_path: str, chunk_nodes):
    return ChunkGraph(Path(repo_path), chunk_nodes)


@pytest.fixture(scope="function")
def repo_graph(request):
    repo_path = request.param
    return RepoGraph(Path(repo_path))
