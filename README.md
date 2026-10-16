# Python Framework (PFW)

PFW is a personal collection of Python utilities for console applications,
automation, and external command execution. The project serves both as a
practical library and as a place to explore Python framework design.

> The project is being modernized incrementally. New code should use the
> focused `pfw.log`, `pfw.terminal`, and `pfw.prompt` modules. `pfw.console`
> remains available as a compatibility layer, while `pfw.shell` is currently a
> legacy API.

## Documentation

- [Getting started](.md/getting-started.md)
- [Architecture and modules](.md/modules.md)
- [`pfw.log` — console logging](.md/log.md)
- [`pfw.terminal` — ANSI and terminal control](.md/terminal.md)
- [`pfw.prompt` — interactive input](.md/prompt.md)
- [`pfw.console` — compatibility facade](.md/console.md)
- [`pfw.shell` — external command execution](.md/shell.md)

## Quick Start

Run code from the repository root so that the `pfw` package is available in
`sys.path`:

```python
from pfw import log

log.configure(colored=None, timestamp=False)

log.debug("Diagnostic details")
log.info("Application started")
log.warning("Configuration is missing")
log.error("The operation failed")
```

`TRACE`, `DEBUG`, and `INFO` messages are written to `stdout` by default.
`WARNING`, `ERROR`, and `CRITICAL` messages are written to `stderr`.
`colored=None` enables automatic color detection based on TTY support,
`NO_COLOR`, and `TERM=dumb`.

An open writable stream can be configured as the application-wide default with
`log.configure(file=stream)`. See [`pfw.log`](.md/log.md#global-configuration)
for lifecycle and override rules.

## Modules

| Module | Purpose | Status |
| --- | --- | --- |
| [`pfw.log`](.md/log.md) | Logging levels, formatting, and stream routing | Primary API |
| [`pfw.terminal`](.md/terminal.md) | ANSI sequences, colors, cursor control, and color policy | Primary API |
| [`pfw.prompt`](.md/prompt.md) | Plain, hidden, and masked input | Primary API |
| [`pfw.console`](.md/console.md) | Re-exports of the former console API | Compatibility |
| [`pfw.shell`](.md/shell.md) | Command construction and external process execution | Legacy, being modernized |

See [Architecture and modules](.md/modules.md) for the dependency layout and
API selection guidelines.

## Examples

Runnable examples are located in `examples/console`:

```bash
python3 -m examples.console.basic_output
python3 -m examples.console.file_logging --output pfw-example.log
python3 -m examples.console.global_configuration
python3 -m examples.console.logger_levels
python3 -m examples.console.terminal_sequences
python3 -m examples.console.interactive_prompts --mode plain
```

The interactive `masked` and `asterisk` modes use the optional `pwinput` and
`getch` dependencies respectively.

## Tests

```bash
python3 -m unittest discover -s test -v
```

The current test suite covers the focused modules and backward compatibility
provided by `pfw.console`.
