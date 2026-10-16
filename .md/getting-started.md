# Getting Started

[← Home](../README.md) · [Architecture and modules](modules.md)

## Requirements

- Python 3;
- a terminal with ANSI support for colored output;
- `pwinput` only for masked input;
- `getch` only for input displayed as asterisks.

The repository does not yet provide an installable package. During development,
run Python from the project root or add the project root to `PYTHONPATH`.

```bash
cd /path/to/python_fw
python3 -c 'from pfw import log; log.info("PFW is ready", timestamp=False)'
```

## Basic Configuration

```python
from pfw import log

previous = log.configure(
    colored=None,
    timestamp=False,
    file=None,
)

try:
    log.info("Automatic color without a timestamp")
finally:
    log.configure(**previous)
```

`log.configure()` returns the previous global values. This is useful in tests,
scripts, and other contexts where temporary settings must be restored.

Pass an open text stream as `file` to make it the default destination for all
existing and future loggers. `file=None` restores automatic `stdout`/`stderr`
routing. The caller remains responsible for keeping the configured stream open
and closing it after restoring the previous configuration.

Supported `colored` values:

| Value | Behavior |
| --- | --- |
| `None` | Detect color support from the stream, `NO_COLOR`, and `TERM=dumb` |
| `True` | Always include ANSI sequences |
| `False` | Never include ANSI sequences |

## Choosing an API

Import focused modules in new code:

```python
from pfw import log
from pfw import prompt
from pfw import terminal
```

Use `pfw.console` only while migrating existing code that depends on the former
names. Focused imports reduce coupling: logging does not load prompt
dependencies, and ANSI sequence generation does not depend on logging.

## Next Steps

- [Module architecture](modules.md)
- [Logging](log.md)
- [Interactive input](prompt.md)
- [ANSI and terminal control](terminal.md)
