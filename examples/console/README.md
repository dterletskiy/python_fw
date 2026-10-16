# Console Module Examples

Console functionality is split across focused modules:

- `pfw.log` — logging levels, formatting, and global configuration;
- `pfw.terminal` — ANSI colors and terminal control;
- `pfw.prompt` — interactive and hidden input;
- `pfw.console` — a compatibility facade for existing code.

Run all commands from the repository root:

```bash
python3 -m examples.console.basic_output
python3 -m examples.console.global_configuration
python3 -m examples.console.logger_levels
python3 -m examples.console.terminal_sequences
```

## Included Examples

- `basic_output.py` — module-level `pfw.log` functions, the `printf` facade,
  standard message levels, the custom `TRACE` level, `stdout`/`stderr` routing,
  separators, indentation, line endings, and timestamps.
- `global_configuration.py` — the global `configure()` function and setting
  precedence between individual calls, `ConsoleLogger` instances, and global
  defaults.
- `logger_levels.py` — standard `logging` level filtering, threshold changes,
  and output redirection to a custom stream.
- `interactive_prompts.py` — plain, hidden, masked, and asterisk input.
- `terminal_sequences.py` — ANSI sequence generation for terminal control. By
  default, sequences are shown through `repr()`; `--apply` runs a safe live
  demonstration.

## Interactive Input

```bash
python3 -m examples.console.interactive_prompts --mode plain
python3 -m examples.console.interactive_prompts --mode hidden
python3 -m examples.console.interactive_prompts --mode masked
python3 -m examples.console.interactive_prompts --mode asterisk
```

The `masked` mode requires `pwinput`, while `asterisk` requires `getch`. These
dependencies are loaded only when their corresponding modes are selected.

## Global Configuration

```python
from pfw import log

log.configure(colored=None, timestamp=False)
log.info("Automatic color without a timestamp")
```

`colored=None` enables automatic color detection based on TTY support,
`NO_COLOR`, and `TERM=dumb`. Explicit `ConsoleLogger` settings override global
defaults, and parameters passed to an individual call have the highest
priority.
