#!/usr/bin/env -S uv run python
"""
Transforms Ruff output to a JetBrains compatible format for Jupyter notebook file
watchers.

JetBrains maintains an intermediary representation that differs from the raw notebook
JSON content: each cell source appears as is in order and is marked up with a comment
line that specifies its type (# %% for code and # %%m for Markdown).

This script makes the link between both formats.
"""

import json
import re
import subprocess
import sys
from itertools import accumulate
from pathlib import Path
from typing import TypedDict

import nbformat

LINE_BREAK = re.compile(r"\r\n|\r|\n")


class RuffLocation(TypedDict):
    column: int
    row: int


class RuffLintingError(TypedDict):
    filename: str
    cell: int
    location: RuffLocation
    code: str
    message: str


def transform_ruff_to_jetbrains_compatible_output(
    notebook_path: Path,
    ruff_parsed_output: list[RuffLintingError],
    cell_sources: list[str],
) -> str:
    """
    Transforms Ruff output to a JetBrains compatible format.

    The line numbers must be mapped to be compatible with JetBrain's intermediate
    notebook representation.
    The file watcher expression must be able to extract the file path, the line number,
    and the expression.

    We transform the ruff JSON output into the following JetBrains compatible format:

        {file_path}:{jetbrains_line_number}:{jetbrains_column_number}: Ruff({error_code}): {message}"

    NB: The JetBrains and Ruff column numbers are shifted by 1 in their indexing

    :param notebook_path: Notebook path.
    :param ruff_parsed_output: Parsed ruff linting output.
    :param cell_sources: Cell sources as specified by the Jupyter notebook JSON content.
    :return: JetBrains file watcher compatible output.
    """  # noqa: E501
    jetbrains_cell_line_offsets = compute_jetbrains_cell_offsets(cell_sources)

    transformed_lines = [
        f"{notebook_path}:"
        f"{jetbrains_cell_line_offsets[int(ruff_line['cell']) - 1] + int(ruff_line['location']['row'])}:"  # noqa: E501
        f"{int(ruff_line['location']['column']) - 1}: "
        f"Ruff ({ruff_line['code']}): {ruff_line['message']}"
        for ruff_line in ruff_parsed_output
    ]

    return "\n".join(transformed_lines)


def read_cells(notebook_path: Path) -> list[str]:
    """
    Reads the cells of the notebook using the official parser.

    :param notebook_path: File path of the Jupyter Notebook to be read.
    :return: Source content of the cells.
    """
    with open(notebook_path, encoding="utf-8") as notebook_file:
        notebook_content = nbformat.read(notebook_file, as_version=4)

    return [cell.source for cell in notebook_content.cells]


def compute_jetbrains_cell_offsets(
    cell_sources: list[str],
) -> list[int]:
    """
    Computes the JetBrains line offsets for each cell in the notebook.

    JetBrains works with an intermediary representation that differs from the raw
    notebook JSON content.
    Each cell is marked up with a comment line that specifies its type and ends with a
    blank line.

    NB: The JetBrains representation can be inspected by looking at the VCS diffs.

    Example Format:

    .. code-block::

        # %%
        a = "some code"

        # %% md
        # Some Markdown

    :param cell_sources: List of notebook cell sources.
    :return: Computed cell line offsets for each cell in the JetBrains representation.
    """
    jetbrains_full_cell_line_counts = [
        # + 2 accounts for the cell markup line and the trailing blank line
        len(re.findall(LINE_BREAK, cell_source)) + 2
        for cell_source in cell_sources
    ]

    # initial=1 accounts for the markup line of the first cell
    return list(accumulate(jetbrains_full_cell_line_counts[:-1], initial=1))


def main():
    # Input Validation
    if len(sys.argv) == 1:
        print(
            "\033[91mNo file specified. Make sure you provide the JetBrains $FilePath$",
            "argument in the file watcher configurations\033[0m",
            file=sys.stderr,
        )
        sys.exit(2)
    if len(sys.argv) >= 3:
        print(
            "\033[91mSeveral files specified. Make sure you only provide the JetBrains",
            "$FilePath$ argument in the file watcher run configurations\033[0m",
            file=sys.stderr,
        )
        sys.exit(2)

    notebook_path = Path(sys.argv[1])

    if notebook_path.suffix != ".ipynb":
        print(
            "\033[91mruff-jupyter-jetbrains is designed to be run on",
            "\033[4m.ipynb\033[24m files. Make sure the JetBrains file watcher is",
            "configured for Jupyter files exclusively.\033[0m",
            file=sys.stderr,
        )
        sys.exit(2)

    if not notebook_path.is_file():
        print(
            f"\033[91mFile {notebook_path} does not exist. This is unexpected",
            "if you use ruff-jupyter-jetbrains as a file watcher.\033[0m",
            file=sys.stderr,
        )
        sys.exit(2)

    # Processing
    ruff_output = subprocess.run(
        ["ruff", "check", "--output-format=json", "--quiet", notebook_path],
        capture_output=True,
        text=True,
    )
    ruff_parsed_output = json.loads(ruff_output.stdout)

    cell_sources = read_cells(notebook_path)

    # Transforming
    jetbrains_compatible_output = transform_ruff_to_jetbrains_compatible_output(
        notebook_path, ruff_parsed_output, cell_sources
    )

    # Output
    print(jetbrains_compatible_output, end="")
    print(ruff_output.stderr, end="")
    sys.exit(ruff_output.returncode)


if __name__ == "__main__":
    main()
