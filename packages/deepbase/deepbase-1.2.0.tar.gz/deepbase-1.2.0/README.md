# DeepBase

**DeepBase** is a command-line tool that analyzes a project directory, extracts the folder structure and the content of all significant code files, and consolidates them into a single text/markdown file.

This unified "context" is perfect for providing to a Large Language Model (LLM) to enable it to deeply understand the entire codebase.

## Features

- **Project Structure**: Generates a tree view of the folder and file structure.
- **Smart Filtering**: Automatically ignores common unnecessary directories (e.g., `.git`, `venv`, `node_modules`).
- **Configurable**: Customize ignored directories and included extensions via a `.deepbase.toml` file.
- **Extension Selection**: Includes only files with relevant code or configuration extensions.
- **Unified Output**: Combines everything into a single file, easy to copy and paste.
- **PyPI Ready**: Easy to install via `pip`.

## Installation

You can install DeepBase directly from PyPI:

```sh
pip install deepbase

```

## How to Use

Once installed, you will have the `deepbase` command available in your terminal.

**Basic Usage:**

Navigate to your project folder (or a parent folder) and run:

```sh
deepbase .
```
*The dot `.` indicates the current directory.*

This command will create a file called `llm_context.md` in the current directory.

**Specify Directory and Output File:**

```sh
deepbase /path/to/your/project -o project_context.txt
```

### Advanced Configuration

You can customize DeepBase's behavior by creating a `.deepbase.toml` file in the root of the project you are analyzing.

**Example `.deepbase.toml`:**
```toml
# Add more directories to ignore.
# These will be added to the default ones.
ignore_dirs = [
  "my_assets_folder",
  "experimental"
]

# Add more extensions or filenames to include.
significant_extensions = [
  ".cfg",
  "Makefile"
]
```

## License

This project is released under the GPL 3 license. See the `LICENSE` file for details.