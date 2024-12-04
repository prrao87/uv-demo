# Exploring uv - The 10x Python Package Manager

This repository contains a demo of the `uv` package manager on a simple project that uses
a graph database, [Kùzu](https://kuzudb.com) to answer questions about the cast and crew of the
movie Interstellar.

## Setup

You can use the `uv` package manager to install the required dependencies:

```bash
uv init
uv add -r requirements.txt
```

This generates a `pyproject.toml` file and installs the dependencies into a virtual environment in `.venv`.

## Running the demo

```bash
uv run create_graph.py
uv run graph_rag.py
```

