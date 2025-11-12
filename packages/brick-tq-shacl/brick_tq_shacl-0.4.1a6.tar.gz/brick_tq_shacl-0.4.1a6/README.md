# Brick topQuadrant SHACL wrapper

## Installation

`brick-tq-shacl` depends on the published `pytqshacl` package from PyPI. The
`cli` extra is enabled automatically so the `pytqshacl` command-line interface
is available without any additional setup. A simple `pip install brick-tq-shacl`
pulls in everything that is required.

For development, clone the repository as usual:

```shell
git clone https://github.com/gtfierro/brick-tq-shacl.git
```

When you need a newer upstream `pytqshacl`, bump the dependency version in
`pyproject.toml` and refresh the lockfiles (`uv lock`, `poetry lock`).

## Contributing

1. Clone the repo.
2. Run `uv sync` (or `uv sync --extra withjre` if you need the managed JRE) to
   install dependencies.
3. Before opening a PR, run the smoke scripts (`uv run python brick.py ...`,
   `uv run python s223.py`, etc.) and add any relevant validation output to the
   PR description per the repository guidelines.
