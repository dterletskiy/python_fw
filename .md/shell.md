# `pfw.shell`

[← Home](../README.md) · [All modules](modules.md)

`pfw.shell` is a legacy module for command construction and synchronous
external process execution. It supports regular pipes and pseudo-terminals
(PTY), output collection, working directories, environments, `sudo`, `chroot`,
and SSH wrappers.

> This API is still being modernized. Check the returned result mapping in
> critical code and do not rely on implementation details.

## Basic Execution

```python
from pfw import shell

result = shell.execute(
    "printf",
    "hello",
    print=False,
    print_command=False,
)

if result["code"] == 0:
    print(result["output"])
```

`execute()` delegates to `run_and_wait_with_status()` and returns a mapping:

| Key | Contents |
| --- | --- |
| `code` | Process return code |
| `output` | Collected output or `None` |
| `command` | The generated command string |

## Main Parameters

| Parameter | Purpose |
| --- | --- |
| `args` | Additional argument list |
| `env` | Child process environment |
| `cwd` | Working directory |
| `output` | `shell.eOutput.PIPE` or `shell.eOutput.PTY` |
| `collect` | Collect output in the result |
| `print` | Print output while executing |
| `expected_return_code` | Expected successful return code |
| `test` | Build the command without normal execution |
| `processor` | Callback for output chunks |
| `print_command` | Print the generated command |

Advanced modes also accept `sudo`, `sudo_pwd`, `chroot`, `chroot_bash`, `ssh`,
`executable`, and `store_command`.

## Command Construction

```python
from pfw import shell

raw = shell.join_command("echo", "hello world")
quoted = shell.build_command("echo", "hello world")
```

- `join_command()` concatenates non-empty strings without shell escaping;
- `build_command()` escapes arguments through `shlex.quote()`.

`CmdLine` is available for composite commands:

```python
from pfw import shell

command = shell.CmdLine("printf", "%s", "hello")
print(command.as_string())
result = command.execute(print=False)
```

## Security

The legacy API constructs command strings, and its main execution path may use
shell interpretation by default. Do not add untrusted user input to a command.
At minimum, use `build_command()` for arguments. For new security-sensitive
code, prefer calling `subprocess.run()` directly with an argument list and
`shell=False`.

## Additional APIs

The module also contains `execute2()` and `run_and_wait_with_status2()`. This is
a second legacy execution path with support for updating a mutable `result`
mapping; treat it as unstable until modernization is complete.
