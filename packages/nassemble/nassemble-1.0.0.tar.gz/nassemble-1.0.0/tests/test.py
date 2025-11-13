#
### Import Modules. ###
#
from typing import Any
#
import pytest
import tempfile
from pathlib import Path
#
from nassemble.main import explore_dir

#
### We can override the default extensions for testing. ###
#
TEST_EXTENSIONS: list[str] = [".txt", ".py", ".md"]

#
### Define some file contents. ###
#
CONTENT_PY: str = """
def hello_world():
    print("This is a python file with more than 50 characters to ensure it gets included.")
"""

CONTENT_MD: str = """
# Project Guide
This is the project guide, also with more than 50 characters.
We want to make sure this file is captured by the tool.
"""

CONTENT_SHORT: str = "This file is too short."

CONTENT_BIN: str = "This is binary data that should be ignored."


#
@pytest.fixture(autouse=True)
def override_settings(monkeypatch: Any):

    """Override global settings for all tests."""

    monkeypatch.setattr("nassemble.main.file_extensions_to_read", TEST_EXTENSIONS)
    monkeypatch.setattr("nassemble.main.keywords_to_skip", ["skip_me", ".git"])


#
def test_explore_dir_scenarios() -> None:

    """
    Test the explore_dir function by creating a temporary directory structure.
    """

    #
    with tempfile.TemporaryDirectory() as tmpdir:

        #
        base_path = Path(tmpdir)

        #
        ### 1. Create files that SHOULD be included. ###
        #
        (base_path / "src").mkdir()
        (base_path / "src" / "app.py").write_text(CONTENT_PY)
        (base_path / "docs").mkdir()
        (base_path / "docs" / "guide.md").write_text(CONTENT_MD)

        #
        ### 2. Create files that SHOULD BE SKIPPED. ###
        #
        ## (short file) ##
        #
        (base_path / "src" / "short.txt").write_text(CONTENT_SHORT)
        #
        ## (wrong extension) ##
        #
        (base_path / "data.bin").write_text(CONTENT_BIN)
        #
        ## (keyword skip) ##
        #
        (base_path / "skip_me_folder").mkdir()
        (base_path / "skip_me_folder" / "secret.txt").write_text(CONTENT_MD)
        #
        ## (hidden folder) ##
        #
        (base_path / ".git").mkdir()
        (base_path / ".git" / "config").write_text("git config stuff")


        #
        ### Run the function. ###
        #
        result_txt = explore_dir(dirpath=str(base_path), txt="", remaining_depth=-1)

        #
        ### 3. Assert the results. ###
        #
        ## Check that the good content is present. ##
        #
        assert CONTENT_PY in result_txt
        assert "FILE: " in result_txt
        assert str(base_path / "src" / "app.py") in result_txt

        assert CONTENT_MD in result_txt
        assert str(base_path / "docs" / "guide.md") in result_txt

        #
        ## Check that the skipped content is NOT present. ##
        #
        assert CONTENT_SHORT not in result_txt
        assert CONTENT_BIN not in result_txt
        assert "secret.txt" not in result_txt
        assert "git config stuff" not in result_txt
