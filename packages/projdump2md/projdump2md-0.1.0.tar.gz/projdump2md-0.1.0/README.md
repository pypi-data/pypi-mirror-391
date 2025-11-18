# projdump2md

A simple CLI tool to dump all project files into a single markdown file with folder structure visualization specially for AI/LLM use.

## Installation

### From PyPI

```bash
pip install projdump2md
```

## Usage

### Commandline arguments

#### File Extension Filters

| Option | Description | Example |
|--------|-------------|---------|
| `-i, --include` | File extensions to include | `-i py,js,html` |
| `-e, --exclude` | File extensions to exclude | `-e log,tmp,bak` |
| `--no-default-excludes` | Disable default file exclusions | `--no-default-excludes` |

**Default excluded extensions:** `pyc`, `o`, `bin`, `hex`, `md`, `elf`

#### Folder Filters

| Option | Description | Example |
|--------|-------------|---------|
| `-I, --include-folders` | Folders to include | `-I src,lib` |
| `-E, --exclude-folders` | Folders to exclude | `-E tests,docs` |
| `--no-default-folder-excludes` | Disable default folder exclusions | `--no-default-folder-excludes` |

**Default excluded folders:** `__pycache__`, `node_modules`, `.git`, `.svn`, `.hg`, `venv`, `env`, `.venv`, `dist`, `build`, `.idea`, `.vscode`

#### General Options

| Option | Description | Default |
|--------|-------------|---------|
| `-f, --folder` | Folder path to scan | `.` (current directory) |
| `-o, --output` | Output file name | `project_dump.md` |
| `--version` | Show version | - |
| `-h, --help` | Show help message | - |


### Examples

Dump all Python files from current directory
```
projdump2md -i py
```

Dump multiple file types
```
projdump2md -i py,js,html,css
```

Dump Python and JavaScript, exclude *.log files
```
projdump2md -i py,js -e log
```

Specify a different folder
```
projdump2md -i cpp,h -f /path/to/project
```

Custom output filename
```
projdump2md -i py -o my_project_dump.md
```

Dump all files (no extension filter)
```
projdump2md -f .
```

### Folder Filtering

Only include src and lib folders
```
projdump2md -I src,lib
```

Exclude test and documentation folders
```
projdump2md -E tests,docs,examples
```

Only Python files from src folder
```
projdump2md -i py -I src
```

Include node_modules (override default exclusion)
```
projdump2md --no-default-folder-excludes -I node_modules
```
