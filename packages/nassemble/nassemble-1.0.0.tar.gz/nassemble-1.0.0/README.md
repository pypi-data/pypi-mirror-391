# 📦 nassemble

**`nassemble`** is a simple command-line utility that recursively explores a directory and combines all source code and documentation files into a single text file.

This is especially useful for providing context to Large Language Models (LLMs) or for creating a simple, single-file archive of a project's text-based assets.

## Installation

You can install `nassemble` directly from PyPI:

```bash
pip install nassemble
````

## Usage

Using `nassemble` is simple. Just run it from your terminal.

```bash
nassemble [OPTIONS]
```

### Options

* `-p, --path` (str): The path to start exploring. (Default: `.`, the current directory)
* `-o, --output` (str): The name of the combined output file. (Default: `.all_doc_together.txt`)
* `-d, --depth` (int): The maximum recursive depth. (Default: `-1`, for no limit)

### Example

To combine all `.py` and `.md` files in your current project into a file named `context.txt`, you would run:

```bash
nassemble -p . -o context.txt
```

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
