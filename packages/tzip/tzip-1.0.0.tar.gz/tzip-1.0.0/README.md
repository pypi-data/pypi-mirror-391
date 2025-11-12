# tzip

`tzip` (short for **TUI zip**) is a lightweight **terminal user interface (TUI)** for exploring and extracting compressed archives.  It is built on top of [Textual](https://textual.textualize.io/), so the interface is snappy and cross-platform, and it supports several popular archive formats including **ZIP**, **7‑Zip** (`.7z`), **RAR** and **tar/tar. * compressions**.

The application provides two main panes: a directory tree on the left and a table view on the right.  You can browse your file system in the tree, select an archive file to open, inspect the contents of that archive, and extract either individual files or the entire archive to a destination directory.  The core functionality is implemented by the `Archiver` classes, which wrap Python’s `zipfile`, `py7zr`, `rarfile` and `tarfile` modules.  Each archiver knows how to list the contents of an archive and extract selected files.

## Features

- **Browse your filesystem.** The left-hand `DirectoryTree` widget shows the current working directory; you can expand directories and select files just like in a GUI file manager.
- **View archive contents.** When you select a supported archive in the directory tree, the right-hand table is populated with the names, sizes and types (file or directory) of the archive entries.  Sizes are rendered in human‑readable units such as KB or MB.
- **Multiple archive formats.**  Out of the box `tzip` supports ZIP files, 7‑Zip archives, RAR archives and tar archives (including `.tar.gz`, `.tgz`, `.tar.bz2`, `.tbz2`, `.tar.xz`, `.txz` and `.tar.zst`).  Each archive type is handled by a dedicated class that can list entries and extract them.
- **Selective extraction.**  You can highlight a single row in the table and press **`e`** to extract just that file/directory.  Alternatively, press **`E`** to extract the entire archive.
- **User‑defined destination.**  When extracting, `tzip` prompts for a destination directory; if you leave the prompt empty the program creates a directory named after the archive inside the current working directory.
- **Status messages and key bindings.**  A status bar informs you about errors or completion messages.  The built‑in key bindings include `q` to quit, `e` to extract selected entries and `E` to extract everything.

## Installation

### Using pip (recommended)

`tzip` is distributed as a Python package on PyPI and depends on Python 3.8 or newer.  To install it along with its dependencies ([Textual](https://pypi.org/project/textual/), `py7zr` and `rarfile`) run:

```bash
pip install tzip
```

Alternatively, if you are working from a local clone of this repository you can install it in editable mode:

```bash
pip install -e .
```

### System requirements

- **Python 3.8+**: See the `requires-python` field in the project metadata.
- **textual**, **py7zr** and **rarfile**: These are installed automatically when you install `tzip` via pip.

On Linux you may also need native tools/libraries for handling RAR archives.  See the [`rarfile` documentation](https://rarfile.readthedocs.io/) for details.

## Usage

Run the application from your terminal by executing the `tzip` script that is installed with the package.  You can also invoke it directly as a module with `python -m tzip.tzip`.  When you start `tzip`, it opens in your current working directory and displays instructions in the toolbar:

```bash
# launch the TUI
$ tzip
```

### Navigating the interface

- **Browse directories:** Use the arrow keys to expand/collapse folders in the directory tree.  Press **Enter** or double‑click on a file to open it; if it’s a supported archive, its contents appear in the table.
- **Select files in the table:** Use the arrow keys to move the cursor up or down.  At present the table supports a single selection.
- **Extract selected entry:** Press **e** to extract the highlighted file/directory.
- **Extract entire archive:** Press **E** to extract everything inside the current archive.
- **Quit:** Press **q** to exit the program.

The extraction actions prompt you for a destination directory; leave the prompt blank to accept the default (which creates a directory named after the archive).

## Development & Contributing

The project uses `setuptools` with [setuptools_scm](https://pypi.org/project/setuptools-scm/) to derive its version from Git tags.  The package metadata in `pyproject.toml` lists the project name, description, license and dependencies.  Feel free to open issues or pull requests on GitHub if you encounter problems or want to propose enhancements.  The `tests/test_smoke.py` file contains a minimal smoke test that ensures the module is importable and the CLI launches.  Additional tests and contributions are welcome.

To set up a development environment:

```bash
# clone the repository and install dev dependencies
pip install -r requirements-dev.txt
# run tests
pytest
```

Before submitting a pull request, ensure that the code passes the test suite and follows [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guidelines.

## License

This project is licensed under the **MIT License**.  See the [`LICENSE`](LICENSE) file for details.
