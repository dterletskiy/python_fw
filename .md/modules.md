# Architecture and Modules

[← Home](../README.md) · [Getting started](getting-started.md)

PFW separates console features by responsibility. Logging can therefore be
used without prompt dependencies, while ANSI sequences can be generated
without creating a logger.

```text
pfw.terminal
   ↑       ↑
pfw.log  pfw.prompt
   ↑       ↑
   pfw.console  (compatibility facade)

pfw.shell  (commands and external processes)
```

## Primary Modules

### `pfw.log`

A `logging.Logger`-based console logger. It provides standard logging levels,
the additional `TRACE = 5` level, ANSI formatting, timestamps, caller metadata,
and application-wide configuration.

[Full `pfw.log` documentation](log.md)

### `pfw.terminal`

Low-level ANSI sequences, foreground/background/style palettes, cursor
movement, screen clearing, and a shared color policy.

[Full `pfw.terminal` documentation](terminal.md)

### `pfw.prompt`

Interactive input through plain input, hidden passwords, external masks, and
asterisk display. Optional packages are loaded lazily only for the selected
mode.

[Full `pfw.prompt` documentation](prompt.md)

## Compatibility

### `pfw.console`

A thin facade that re-exports logging, terminal, and prompt APIs. It supports
incremental migration of existing consumers. New code should import focused
modules directly.

[Full `pfw.console` documentation](console.md)

## Command Execution

### `pfw.shell`

A structured command runner with PIPE and PTY streaming, explicit shell mode,
timeouts, callbacks, command logging, and typed sudo/chroot/SSH adapters.

[Full `pfw.shell` documentation](shell.md)

## Recommendations

1. Use `pfw.log` instead of `pfw.console` for new logging code.
2. Import `pfw.prompt` only in interactive application layers.
3. Generate control sequences through `pfw.terminal`, but consider the target
   stream capabilities before writing them.
4. Use `pfw.shell.run()` with an argument sequence for untrusted values. Reserve
   `run_shell()` for scripts that intentionally require shell syntax.
