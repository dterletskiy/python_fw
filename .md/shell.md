# `pfw.shell`

[← Home](../README.md) · [All modules](modules.md)

`pfw.shell` runs external commands synchronously. Use `run()` for an executable
and its arguments; use `run_shell()` when a command needs shell syntax. Both
support PIPE and PTY output, streaming callbacks, timeouts, command logging,
and typed sudo, chroot, and SSH options. This module requires a POSIX system.

## Structured Commands

Pass the executable and every argument as separate strings:

```python
from pfw import shell

result = shell.run([
    "git",
    "status",
    "--short",
])

if result.succeeded:
    print(result.stdout)
```

`run()` accepts a nonempty sequence of strings (or a `Command` instance). For
local execution, it starts the executable directly and passes each remaining
string as one argument. A value such as `"$HOME; *.txt"` remains literal;
there is no variable expansion, wildcard expansion, pipeline, or redirection.
A command string is rejected instead of being split into arguments.

The `Command` helper stores reusable structured arguments:

```python
command = shell.Command("printf", "%s", "hello world")
print(command)  # printf %s 'hello world'
result = command.run()
```

## Explicit Shell Scripts

Use `run_shell()` when pipelines, redirections, substitutions, or other shell
syntax are intentional:

```python
result = shell.run_shell("printf 'alpha\\n' | tr a-z A-Z")
print(result.stdout)
```

`run_shell()` passes the script string to `/bin/bash -c` by default. Override
the executable with the `shell` argument. Do not interpolate untrusted values
into a script: shell syntax would interpret them. Pass such values as separate
arguments to `run()`.

## Results

Both execution functions return an immutable `RunResult`:

| Attribute | Meaning |
| --- | --- |
| `returncode` | Child return code, or `None` for a dry run |
| `stdout` | Collected standard output |
| `stderr` | Collected standard error |
| `output` | Both streams in observed order |
| `command` | Shell-escaped display form of the planned command |
| `expected_returncode` | Return code considered successful |
| `executed` | Whether a process was started |
| `succeeded` | Whether execution matched the expected return code |

The expected return code defaults to `0`. Set `expected_returncode` to another
integer when that code indicates success. Set `check=True` to raise
`subprocess.CalledProcessError` for an unexpected return code. A timeout raises
`subprocess.TimeoutExpired`; a missing executable raises `FileNotFoundError`.
For a dry run, `returncode` is `None`, `executed` and `succeeded` are `False`,
and no process is started, even with `check=True`.

## Output Modes

```python
result = shell.run(
    ["python3", "script.py"],
    output=shell.OutputMode.PIPE,
    collect=True,
    echo=True,
)
```

- `OutputMode.PIPE` is the default; it captures stdout and stderr separately.
  `output` contains their chunks in the order observed by the parent process.
- `OutputMode.PTY` connects the child to a pseudo-terminal. Its merged output
  appears in `stdout` and `output`; `stderr` is empty.
- `collect=True` retains output in the result. With `collect=False`, the
  result's three output strings are empty, but callbacks and echo still work.
- `echo=True` forwards output to the current stdout or stderr stream. PTY
  output goes to stdout.

A processor receives typed chunks while the command is running:

```python
def process(chunk):
    print(chunk.stream.value, repr(chunk.text))

shell.run(["build-tool"], processor=process)
```

Each `OutputChunk` contains `text` and a `stream` value of `STDOUT`, `STDERR`,
or `PTY`. Callbacks receive decoded text as it arrives; a chunk need not be a
complete line. `encoding` defaults to UTF-8 and `errors` to `"replace"`.
With `interactive=True` (the default), PTY mode also forwards keyboard input
when the caller's stdin is a TTY. Set `interactive=False` for unattended PTY
commands.

## Input, Environment, and Working Directory

```python
result = shell.run(
    ["python3", "worker.py"],
    cwd="/workspace",
    env={"MODE": "release"},
    input_data="request\n",
    timeout=30,
)
```

`env` replaces the child's environment; it does not merge with the current
environment. Omit it to inherit a copy of `os.environ`, or merge explicitly:

```python
import os

result = shell.run(["worker"], env={**os.environ, "MODE": "release"})
```

The caller's mapping is not modified. Terminal dimensions are added when a
terminal is available. `cwd` sets the local process working directory.
`input_data` accepts `str`, `bytes`, or `None`; strings use `encoding` and
`errors`, and bytes are sent unchanged. In PIPE mode, stdin is closed when no
input is provided.

## Sudo and Chroot

```python
preview = shell.run(
    ["id"],
    sudo=shell.SudoOptions(non_interactive=True),
    chroot=shell.ChrootOptions("/target"),
    dry_run=True,
)
```

The command is wrapped as `sudo ... -- chroot /target id`. Sudo's default
non-interactive mode uses `-n`. When `SudoOptions(password=...)` is provided,
the password is sent through stdin with `sudo -S`; it is excluded from
`RunResult.command`, `show_command` output, and command logs. Other sensitive
values passed as command arguments are **not** redacted. For interactive sudo
prompts, set `non_interactive=False` and use PTY output.

## SSH and Jump Hosts

```python
ssh = shell.SshOptions(
    host="server.example",
    user="builder",
    port=2222,
    jump_hosts=(
        shell.JumpHost("gateway.example", "user"),
    ),
    options=("-o", "BatchMode=yes"),
    cwd="/remote/workspace",
)

preview = shell.run(["uname", "-a"], ssh=ssh, dry_run=True)
print(preview.command)
```

`sudo` and `chroot` transform the target command before SSH wrapping, so they
run on the remote host when `ssh` is configured. The regular `cwd` argument is
local; use `SshOptions.cwd` for a remote working directory. `SshOptions.options`
contains raw SSH argument tokens, so include flags such as `"-o"` explicitly.
`env` configures the local SSH process; it does not set remote environment
variables. SSH executes a shell-escaped command on the remote host, so the
local direct-execution guarantee does not apply to this adapter.

## Command Logging and Dry Runs

```python
previous = shell.configure(command_log="commands.log")
try:
    preview = shell.run(
        ["deploy", "--target", "staging"],
        dry_run=True,
        show_command=True,
    )
finally:
    shell.configure(**previous)
```

`configure(command_log=...)` sets a process-wide default path and returns the
previous configuration, which can be restored as shown. Commands are appended
to the file, one display string per line; the parent directory must exist.
Per-call `command_log` overrides the default, and `command_log=None` disables
logging for that call. `show_command=True` prints the planned command. A dry
run still prints and logs it when these options are enabled. Shell escaping is
for display; it does not hide ordinary argument values.

## Examples

Runnable examples are available in [`examples/shell`](../examples/shell):

```bash
python3 -m examples.shell.structured_command
python3 -m examples.shell.shell_pipeline
python3 -m examples.shell.streaming_output
python3 -m examples.shell.pty_output
python3 -m examples.shell.dry_run_adapters
python3 -m examples.shell.command_logging --output shell-commands.log
```

The adapter example uses `dry_run=True`, so it does not open an SSH
connection, request elevated privileges, or enter a chroot environment.

## Sequential Commands

```python
results = shell.run_many(
    [
        ["prepare"],
        ["build"],
        ["package"],
    ],
    stop_on_error=True,
)
```

`run_many()` executes structured commands in order and returns a list of
`RunResult` objects. `stop_on_error=True` stops after the first result whose
return code does not match `expected_returncode`. Shared keyword arguments are
passed to every command. If `check=True`, an unexpected return code raises
immediately instead of returning the partial result list.

## Platform and Dependencies

The module uses `pty`, `termios`, and `fcntl`, so it currently supports POSIX
systems. The SSH, sudo, and chroot adapters invoke the corresponding system
executables; they must be available when the command is actually run.
