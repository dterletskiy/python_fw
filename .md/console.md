# `pfw.console`

[← Home](../README.md) · [All modules](modules.md)

`pfw.console` is a compatibility facade for code written before the console
subsystem was decomposed. It re-exports APIs from `pfw.log`, `pfw.terminal`, and
`pfw.prompt`.

## Available API

- `AnsiDebug` — a compatible subclass of `pfw.log.ConsoleLogger`;
- `log` and `debug` — the same instance with caller metadata;
- `printf` — an instance without caller metadata;
- `configure`, `TRACE`, `Format`, and `ConsoleLogger` from `pfw.log`;
- `prompt()` and `prompt_dep()` from `pfw.prompt`;
- palettes, cursor helpers, and control functions from `pfw.terminal`.

```python
from pfw import console

console.configure(colored=None, timestamp=False)
console.debug.info("The compatibility API still works")
console.printf.warning("Warning")

answer = console.prompt("Value: ")
```

Because `configure` is re-exported directly, `console.configure(file=stream)`
also sets the application-wide default logging stream. New code should prefer
the equivalent `pfw.log.configure()` call.

## Migration

Existing code:

```python
from pfw import console

console.printf.info("Done")
console.clear_line()
value = console.prompt("Value: ")
```

Recommended replacement:

```python
from pfw import log
from pfw import prompt
from pfw import terminal

log.printf.info("Done")
terminal.clear_line()
value = prompt.prompt("Value: ")
```

Direct imports make component dependencies explicit and allow the compatibility
layer to be removed in the future without changing the focused modules.

The historical `promt` and `promt_dep` names, along with the visual `header`,
`question`, `ok`, and `marker` methods, are no longer part of the API.
