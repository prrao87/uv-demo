# Exploring `uv`: The 10x Python Package Manager

This repository contains code to demonstrate the basic features and ease of use of the
[`uv` package manager](https://docs.astral.sh/uv/).

We will demonstrate how simple it is to set up and run `uv` by building a project that ingests data
about the cast and crew of the movie Interstellar into a graph database, [Kùzu](https://kuzudb.com),
and then answer questions about the movie using a graph retrieval augmented generation
(Graph RAG) pipeline.

## Setup

The Python version we will use is 3.12. You can install `uv` using the following commands, depending
on your operating system:

```bash
# On macOS via Homebrew
brew install uv

# On Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## Initialize the project

```bash
uv init
```

This creates a new `pyproject.toml` file in the root of the project.

If using a `requirements.txt` file, you can add all of its dependencies to the existing
`pyproject.toml` file:

```bash
uv add -r requirements.txt
```

Alternatively, you can add new dependencies manually as needed:

```bash
# Example of installing a new package
uv add requests
```

The dependencies in `pyproject.toml` file and its associated lock file `uv.lock` are installed
in a local virtual environment, in the directory `.venv`. To share the dependencies in a
platform-agnostic manner with your collaborators, you can simply commit the `uv.lock` file and
`pyproject.toml` to your repository, and this will allow them to reproduce the same environment 
on their own machines by running:

```bash
uv sync
```

> [!NOTE]
> If you are relying on `uv` to manage your Python version, **you do not need to worry about virtual
> environments** at all! You can simply run `uv run <script>` and `uv` will use the Python version
> specified in your `pyproject.toml` file, and set up and manage the virtual environment for you.

## Running the demo

You can execute the `hello.py` script by running the following command:

```bash
uv run hello.py
```

This is very similar to running `python hello.py` or `python3 hello.py` in the terminal, but under the hood,
`uv` is performing a whole host of steps, including the following:

1. Installs Python if it's not already installed
2. Creates and activates the virtual environment
3. Installs the dependencies
4. Runs the code

This is a very simple example, but hopefully, it demonstrates how `uv` can make it so much easier to
manage multiple Python versions, local virtual environments and all your project's dependencies.
Have fun using uv, and spread the word!
