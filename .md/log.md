# `pfw.log`

[← Home](../README.md) · [All modules](modules.md)

`pfw.log` provides a console logger built on the standard `logging.Logger`.
It preserves the framework's compact API while using standard level filtering
and the global `logging.disable()` mechanism.

## Levels

| Method | Value | Default stream |
| --- | ---: | --- |
| `trace()` | `5` | `stdout` |
| `debug()` | `logging.DEBUG` (`10`) | `stdout` |
| `info()` | `logging.INFO` (`20`) | `stdout` |
| `warning()` | `logging.WARNING` (`30`) | `stderr` |
| `error()` | `logging.ERROR` (`40`) | `stderr` |
| `critical()` | `logging.CRITICAL` (`50`) | `stderr` |

The `TRACE` level is registered globally through `logging.addLevelName()` and
is filtered separately from `DEBUG`.

```python
import logging

from pfw import log

logger = log.ConsoleLogger(
    level=logging.INFO,
    colored=None,
    timestamp=False,
)

logger.debug("This message is filtered out")
logger.info("This message is visible")
logger.error("This message is written to stderr")
```

## Global Facades

The module creates two ready-to-use logger instances:

- `log.printf` — output without caller metadata;
- `log.logger` — output with the calling function and line number.

The `trace`, `debug`, `info`, `warning`, `error`, `critical`, `exception`, and
`log` functions delegate to `log.logger` and adjust `stacklevel`. Caller
metadata therefore points to user code rather than the internal facade.

```python
from pfw import log

log.info("Message with caller metadata")
log.printf.info("Plain output", timestamp=False)
log.log(log.TRACE, "Custom level")
```

## Global Configuration

```python
previous = log.configure(colored=None, timestamp=False, file=None)
```

- `colored=None` — automatic mode;
- `colored=True` — force ANSI output;
- `colored=False` — disable ANSI output;
- `timestamp=True/False` — configure the global timestamp default;
- `file=<stream>` — send all messages to an open writable stream by default;
- `file=None` — restore automatic `stdout`/`stderr` routing.

The global file applies immediately to existing and future loggers that do not
have an instance-level file. The caller owns the stream and must keep it open
while it is configured. An instance or individual call can pass its own stream;
passing `file=None` at either level bypasses the global file and restores
severity-based `stdout`/`stderr` routing for that logger or call.

```python
from pfw import log

with open("application.log", "a", encoding="utf-8") as stream:
    previous = log.configure(
        file=stream,
        colored=False,
        timestamp=True,
    )
    try:
        log.info("Application started")
        log.error("Operation failed")
    finally:
        log.configure(**previous)
```

Configuration precedence, from highest to lowest:

1. parameters passed to an individual call;
2. `ConsoleLogger` instance parameters;
3. values set through `log.configure()`.

`configure()` returns the previous `colored`, `timestamp`, and `file` values,
so the complete global state can be restored with `log.configure(**previous)`.

## `ConsoleLogger` Parameters

The constructor and individual calls support the following options:

| Parameter | Purpose |
| --- | --- |
| `colored` | ANSI color mode |
| `timestamp` | Include date and time |
| `inspect` | `0` — none, `1` — function and line, `2` — path, function, and line |
| `level` | Minimum logging level |
| `file` | Explicit stream instead of automatic `stdout`/`stderr` routing |
| `sep` | Separator between arguments |
| `end` | Message terminator |
| `tabs` | Number of indentation units |
| `def_tabs` | One indentation unit |
| `flush` | Flush the stream immediately |

```python
from pfw import log

logger = log.ConsoleLogger(
    colored=False,
    timestamp=False,
    sep=" | ",
    tabs=1,
    def_tabs="..",
)

logger.info("alpha", "beta")  # ..alpha | beta
```

## Exceptions

Call `exception()` from an exception handler to include a traceback:

```python
from pfw import log

try:
    int("not-a-number")
except ValueError:
    log.exception("Could not convert the value")
```

## Related Pages

- [Global color policy](terminal.md)
- [Compatibility facade](console.md)
