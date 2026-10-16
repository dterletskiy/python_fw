# `pfw.terminal`

[← Home](../README.md) · [All modules](modules.md)

`pfw.terminal` generates ANSI escape sequences and determines whether color
should be enabled for a given stream.

## Control Sequences

```python
from pfw import terminal

terminal.set_title("My application")
terminal.clear_screen()
terminal.clear_line()

terminal.Cursor.UP(2)
terminal.Cursor.DOWN(2)
terminal.Cursor.FORWARD(4)
terminal.Cursor.BACK(4)
terminal.Cursor.POS(10, 5)
```

These functions return strings; they do not write to the terminal themselves.

```python
import sys

from pfw import terminal

sys.stdout.write(terminal.clear_line())
sys.stdout.flush()
```

## Palettes

The module provides ready-to-use namespaces:

- `terminal.Foreground` — normal and bright text colors;
- `terminal.Background` — normal and bright background colors;
- `terminal.Style` — bold, dim, italic, underline, and reset;
- `terminal.Cursor` — cursor movement and positioning.

```python
from pfw import terminal

message = (
    terminal.Style.BOLD
    + terminal.Foreground.RED
    + "Error"
    + terminal.Style.RESET
    + terminal.Foreground.RESET
)
```

## Color Policy

```python
import sys

from pfw import terminal

previous = terminal.set_color_mode(None)
enabled = terminal.is_color_enabled(sys.stdout)
terminal.set_color_mode(previous)
```

Automatic mode (`None`) performs the following checks:

1. `NO_COLOR` disables color;
2. `TERM=dumb` disables color;
3. the stream must return `True` from `isatty()`.

Explicit `True` and `False` values take priority over automatic detection. The
shared setting is also used by `pfw.log` and `pfw.prompt`.
