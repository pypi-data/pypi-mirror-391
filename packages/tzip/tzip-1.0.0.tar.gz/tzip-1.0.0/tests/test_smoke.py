import sys
import subprocess


def test_importable():
    import tzip  # noqa: F401


def test_sorter_cli_echo(tmp_path):
    # Run the module as a script
    res = subprocess.run(
        [sys.executable, "-m", "tzip.tzip"],
        input=b"q",
        check=True,
    )
