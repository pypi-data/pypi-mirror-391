# Half-Hour (`hh`)

A minimal command-line note-taking tool for quick logging and reviewing of time-stamped entries.

## Overview

The `hh` package provides three simple functions to manage a plain-text note file configured via `hh.yaml`:

- `hha`: **Add** a new note line.
- `hhl`: **List** the most recent notes.
- `hhd`: **Delete** the most recent lines.

All notes are appended to a single text file specified in the configuration.

## Configuration

Create a `hh.yaml` file in the same directory as `__init__.py` with the following content:

```yaml
notefile: /path/to/your/notes.txt
```

Replace `/path/to/your/notes.txt` with the absolute or relative path to your desired note file.

## Usage

### Add a note (`hha`)

```python
from hh import hha

hha("14:30", "Started working on README")
# Equivalent to: hha("14:30 Started working on README")
```

> **Note**: All arguments are joined into a single line and appended to the note file.

### List recent notes (`hhl`)

```python
from hh import hhl

hhl()      # Show last 10 lines
hhl(5)     # Show last 5 lines
```

### Delete recent notes (`hhd`)

```python
from hh import hhd

hhd(3)     # Delete the last 3 lines
```

> ⚠️ Deletion is permanent and cannot be undone.

## Requirements

- Python 3.6+
- `PyYAML` library (`pip install PyYAML`)

## License

[MIT](LICENSE) (assuming standard open-source practice; adjust as needed).