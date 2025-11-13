# tests/test_main.py

import os
from typer.testing import CliRunner
from deepbase.main import app

# Runner instance to execute Typer app commands
runner = CliRunner()

def test_create_context_successfully(tmp_path):
    """
    Tests the creation of a context file in a successful scenario.
    """
    # 1. Create a mock project structure
    project_dir = tmp_path / "my_test_project"
    project_dir.mkdir()
    (project_dir / "main.py").write_text("print('hello world')")
    (project_dir / "README.md").write_text("# My Project")
    
    # Create a directory to ignore
    ignored_dir = project_dir / "venv"
    ignored_dir.mkdir()
    (ignored_dir / "ignored_file.py").write_text("ignore me")
    
    output_file = tmp_path / "context.md"

    # 2. Execute the CLI command with arguments in the correct order
    result = runner.invoke(app, [str(project_dir), "--output", str(output_file)])

    # 3. Verify the results
    assert result.exit_code == 0
    assert "SUCCESS" in result.stdout
    assert output_file.exists()

    content = output_file.read_text()
    
    # Check that significant files are included
    assert "--- START OF FILE: main.py ---" in content
    assert "print('hello world')" in content
    assert "--- START OF FILE: README.md ---" in content
    
    # Check that ignored directory and files are not present
    assert "venv" not in content
    assert "ignored_file.py" not in content

def test_directory_not_found():
    """
    Tests the behavior when the input directory does not exist.
    """
    result = runner.invoke(app, ["non_existent_dir"])
    assert result.exit_code == 1
    assert "directory does not exist" in result.stdout