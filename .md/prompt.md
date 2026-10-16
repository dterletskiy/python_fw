# `pfw.prompt`

[← Home](../README.md) · [All modules](modules.md)

`pfw.prompt` combines several interactive input modes. It does not depend on
logging and loads external prompt libraries only when their modes are used.

## Plain Input

```python
from pfw import prompt

name = prompt.prompt("Name: ")
```

Without the `mask` argument, the function uses the built-in `input()`.

## Masked Input

```python
from pfw import prompt

password = prompt.prompt("Password: ", mask="*")
```

This mode requires the optional `pwinput` package. If it is unavailable, the
function raises `ModuleNotFoundError` with an explanatory message.

## Dependent Input Modes

`prompt_dep()` selects its input mechanism through the `type` argument:

| `type` | Mechanism | Dependency |
| --- | --- | --- |
| `"show"` | `input()` | None |
| `"hide"` | `getpass.getpass()` | Standard library |
| `"asterisk"` | Character input displayed as `*` | `getch` |

```python
from pfw import prompt

visible = prompt.prompt_dep("Value: ", type="show")
hidden = prompt.prompt_dep("Secret: ", type="hide")
asterisk = prompt.prompt_dep("PIN: ", type="asterisk")
```

## Prompt Color

The module uses the shared `pfw.terminal` color policy by default. It can be
overridden for an individual call:

```python
answer = prompt.prompt("Continue? ", colored=False)
```

The misspelled historical names `promt` and `promt_dep` have been removed. Use
only `prompt` and `prompt_dep`.
