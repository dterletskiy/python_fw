"""Safe command execution with streaming PIPE and PTY output."""

import codecs
import dataclasses
import enum
import fcntl
import io
import os
import pathlib
import pty
import select
import selectors
import shlex
import signal
import struct
import subprocess
import sys
import termios
import threading
import time
import tty
from collections.abc import Callable, Mapping, Sequence

from pfw import log


_UNSET = object( )
_COMMAND_LOG = None


class OutputMode( enum.Enum ):
   PIPE = "pipe"
   PTY = "pty"


class OutputStream( enum.Enum ):
   STDOUT = "stdout"
   STDERR = "stderr"
   PTY = "pty"


@dataclasses.dataclass( frozen = True )
class OutputChunk:
   stream: OutputStream
   text: str


@dataclasses.dataclass( frozen = True )
class JumpHost:
   host: str
   user: str | None = None

   def __post_init__( self ):
      if not isinstance( self.host, str ) or not self.host:
         raise ValueError( "jump host must not be empty" )
      if self.user is not None and ( not isinstance(self.user, str) or not self.user ):
         raise ValueError( "jump host user must be a non-empty string or None" )

   def destination( self ):
      return _destination( self.host, self.user )


@dataclasses.dataclass( frozen = True )
class SshOptions:
   host: str
   user: str | None = None
   port: int | None = None
   jump_hosts: tuple[JumpHost, ...] = ( )
   options: tuple[str, ...] = ( )
   cwd: str | os.PathLike | None = None

   def __post_init__( self ):
      if not isinstance( self.host, str ) or not self.host:
         raise ValueError( "ssh host must not be empty" )
      if self.user is not None and ( not isinstance(self.user, str) or not self.user ):
         raise ValueError( "ssh user must be a non-empty string or None" )
      if self.port is not None and self.port <= 0:
         raise ValueError( "ssh port must be greater than zero" )
      if any( not isinstance(host, JumpHost) for host in self.jump_hosts ):
         raise TypeError( "ssh jump_hosts must contain JumpHost instances" )
      if any( not isinstance(option, str) for option in self.options ):
         raise TypeError( "ssh options must contain strings" )

   def destination( self ):
      return _destination( self.host, self.user )


@dataclasses.dataclass( frozen = True )
class SudoOptions:
   password: str | None = dataclasses.field( default = None, repr = False )
   non_interactive: bool = True

   def __post_init__( self ):
      if self.password is not None and not isinstance( self.password, str ):
         raise TypeError( "sudo password must be a string or None" )
      if not isinstance( self.non_interactive, bool ):
         raise TypeError( "sudo non_interactive must be a bool" )


@dataclasses.dataclass( frozen = True )
class ChrootOptions:
   root: str | os.PathLike

   def __post_init__( self ):
      try:
         root = os.fspath( self.root )
      except TypeError as error:
         raise TypeError( "chroot root must be path-like" ) from error
      if not root:
         raise ValueError( "chroot root must not be empty" )


@dataclasses.dataclass( frozen = True )
class Command:
   argv: tuple[str, ...]

   def __init__( self, executable: str, *arguments: str ):
      object.__setattr__( self, "argv", _normalize_argv(( executable, *arguments )) )

   def __str__( self ):
      return shlex.join( self.argv )

   def run( self, **kwargs ):
      return run( self.argv, **kwargs )


@dataclasses.dataclass( frozen = True )
class RunResult:
   returncode: int | None
   stdout: str
   stderr: str
   output: str
   command: str
   expected_returncode: int
   executed: bool = True

   @property
   def succeeded( self ):
      return self.executed and self.returncode == self.expected_returncode


@dataclasses.dataclass( frozen = True )
class _CommandPlan:
   argv: tuple[str, ...]
   display: str
   stdin_prefix: bytes


class _OutputCollector:
   def __init__( self, *, collect, echo, processor, encoding, errors ):
      self.__collect = collect
      self.__echo = echo
      self.__processor = processor
      self.__decoders = {
         stream: codecs.getincrementaldecoder( encoding )( errors = errors )
         for stream in OutputStream
      }
      self.__stdout = [ ]
      self.__stderr = [ ]
      self.__output = [ ]

   def feed( self, stream, data, *, final = False ):
      text = self.__decoders[stream].decode( data, final = final )
      if not text:
         return

      if self.__collect:
         self.__output.append( text )
         if OutputStream.STDERR == stream:
            self.__stderr.append( text )
         else:
            self.__stdout.append( text )

      if self.__echo:
         destination = sys.stderr if OutputStream.STDERR == stream else sys.stdout
         destination.write( text )
         destination.flush( )

      if self.__processor is not None:
         self.__processor( OutputChunk(stream, text) )

   def finish( self, stream ):
      self.feed( stream, b"", final = True )

   def result( self ):
      return "".join( self.__stdout ), "".join( self.__stderr ), "".join( self.__output )


def configure( *, command_log = _UNSET ):
   """Configure the application-wide command log path."""
   global _COMMAND_LOG

   if command_log is not _UNSET and command_log is not None:
      command_log = pathlib.Path( command_log )

   previous = { "command_log": _COMMAND_LOG }
   if command_log is not _UNSET:
      _COMMAND_LOG = command_log
   return previous


def has_fileno( stream ):
   """Return whether a stream exposes a usable integer file descriptor."""
   try:
      return isinstance( stream.fileno( ), int )
   except ( AttributeError, io.UnsupportedOperation, OSError, ValueError ):
      return False


def isatty( stream ):
   """Return whether a stream is attached to a terminal."""
   try:
      return bool( stream.isatty( ) )
   except ( AttributeError, io.UnsupportedOperation, OSError, ValueError ):
      if not has_fileno( stream ):
         return False
      try:
         return os.isatty( stream.fileno( ) )
      except OSError:
         return False


def get_terminal_dimensions( stream = None ):
   """Return terminal columns and rows, or ``(None, None)``."""
   stream = sys.stdout if stream is None else stream
   if not isatty( stream ):
      return None, None
   try:
      dimensions = os.get_terminal_size( stream.fileno( ) )
   except OSError:
      return None, None
   return dimensions.columns, dimensions.lines


def run(
   command,
   *,
   cwd = None,
   env: Mapping[str, str] | None = None,
   output = OutputMode.PIPE,
   collect = True,
   echo = False,
   processor: Callable[[OutputChunk], None] | None = None,
   input_data: str | bytes | None = None,
   encoding = "utf-8",
   errors = "replace",
   timeout: float | None = None,
   expected_returncode = 0,
   check = False,
   dry_run = False,
   show_command = False,
   command_log = _UNSET,
   sudo: SudoOptions | None = None,
   chroot: ChrootOptions | None = None,
   ssh: SshOptions | None = None,
   interactive = True,
):
   """Execute a structured command without shell interpretation."""
   argv = command.argv if isinstance( command, Command ) else _normalize_argv( command )
   return _run(
      argv,
      cwd = cwd,
      env = env,
      output = output,
      collect = collect,
      echo = echo,
      processor = processor,
      input_data = input_data,
      encoding = encoding,
      errors = errors,
      timeout = timeout,
      expected_returncode = expected_returncode,
      check = check,
      dry_run = dry_run,
      show_command = show_command,
      command_log = command_log,
      sudo = sudo,
      chroot = chroot,
      ssh = ssh,
      interactive = interactive,
   )


def run_shell( script, *, shell = "/bin/bash", **kwargs ):
   """Execute an explicit shell script."""
   if not isinstance( script, str ):
      raise TypeError( "script must be a string" )
   if not script:
      raise ValueError( "script must not be empty" )
   return _run( ( os.fspath(shell), "-c", script ), **kwargs )


def run_many( commands, *, stop_on_error = False, **kwargs ):
   """Execute structured commands sequentially."""
   results = [ ]
   for command in commands:
      result = run( command, **kwargs )
      results.append( result )
      if stop_on_error and not result.succeeded:
         break
   return results


def _run(
   argv,
   *,
   cwd = None,
   env = None,
   output = OutputMode.PIPE,
   collect = True,
   echo = False,
   processor = None,
   input_data = None,
   encoding = "utf-8",
   errors = "replace",
   timeout = None,
   expected_returncode = 0,
   check = False,
   dry_run = False,
   show_command = False,
   command_log = _UNSET,
   sudo = None,
   chroot = None,
   ssh = None,
   interactive = True,
):
   output = _normalize_output_mode( output )
   environment = _prepare_environment( env )
   plan = _build_plan( argv, sudo = sudo, chroot = chroot, ssh = ssh, encoding = encoding )
   payload = plan.stdin_prefix + _encode_input( input_data, encoding, errors )

   if show_command:
      log.printf.info( "$", plan.display, sep = " ", timestamp = False )
   _store_command( plan.display, command_log )

   if dry_run:
      return RunResult(
         returncode = None,
         stdout = "",
         stderr = "",
         output = "",
         command = plan.display,
         expected_returncode = expected_returncode,
         executed = False,
      )

   collector = _OutputCollector(
      collect = collect,
      echo = echo,
      processor = processor,
      encoding = encoding,
      errors = errors,
   )

   if OutputMode.PTY == output:
      returncode = _run_pty(
         plan,
         collector,
         payload = payload,
         cwd = cwd,
         env = environment,
         timeout = timeout,
         interactive = interactive,
      )
   else:
      returncode = _run_pipe(
         plan,
         collector,
         payload = payload,
         cwd = cwd,
         env = environment,
         timeout = timeout,
      )

   stdout, stderr, combined = collector.result( )
   result = RunResult(
      returncode = returncode,
      stdout = stdout,
      stderr = stderr,
      output = combined,
      command = plan.display,
      expected_returncode = expected_returncode,
   )

   if check and not result.succeeded:
      raise subprocess.CalledProcessError(
         returncode,
         plan.argv,
         output = stdout,
         stderr = stderr,
      )
   return result


def _build_plan( argv, *, sudo, chroot, ssh, encoding ):
   argv = list( _normalize_argv(argv) )
   stdin_prefix = b""

   if chroot is not None:
      if not isinstance( chroot, ChrootOptions ):
         raise TypeError( "chroot must be ChrootOptions or None" )
      argv = [ "chroot", os.fspath(chroot.root), *argv ]

   if sudo is not None:
      if not isinstance( sudo, SudoOptions ):
         raise TypeError( "sudo must be SudoOptions or None" )
      sudo_argv = [ "sudo" ]
      if sudo.password is not None:
         sudo_argv.extend(( "-S", "-p", "" ))
         stdin_prefix = ( sudo.password + "\n" ).encode( encoding )
      elif sudo.non_interactive:
         sudo_argv.append( "-n" )
      sudo_argv.append( "--" )
      argv = [ *sudo_argv, *argv ]

   if ssh is not None:
      if not isinstance( ssh, SshOptions ):
         raise TypeError( "ssh must be SshOptions or None" )
      remote_command = shlex.join( argv )
      if ssh.cwd is not None:
         remote_command = "cd " + shlex.quote(os.fspath(ssh.cwd)) + " && " + remote_command

      ssh_argv = [ "ssh" ]
      if ssh.port is not None:
         ssh_argv.extend(( "-p", str(ssh.port) ))
      if ssh.jump_hosts:
         ssh_argv.extend(( "-J", ",".join(host.destination( ) for host in ssh.jump_hosts) ))
      ssh_argv.extend( ssh.options )
      ssh_argv.extend(( ssh.destination( ), remote_command ))
      argv = ssh_argv

   normalized = tuple( argv )
   return _CommandPlan(
      argv = normalized,
      display = shlex.join( normalized ),
      stdin_prefix = stdin_prefix,
   )


def _run_pipe( plan, collector, *, payload, cwd, env, timeout ):
   process = subprocess.Popen(
      plan.argv,
      stdin = subprocess.PIPE if payload else subprocess.DEVNULL,
      stdout = subprocess.PIPE,
      stderr = subprocess.PIPE,
      cwd = cwd,
      env = env,
      start_new_session = True,
   )
   writer = _start_stdin_writer( process, payload )
   selector = selectors.DefaultSelector( )
   started = time.monotonic( )

   try:
      selector.register( process.stdout, selectors.EVENT_READ, OutputStream.STDOUT )
      selector.register( process.stderr, selectors.EVENT_READ, OutputStream.STDERR )

      while selector.get_map( ):
         _check_timeout( process, timeout, started, plan.argv )
         for key, _ in selector.select( 0.05 ):
            data = os.read( key.fileobj.fileno( ), 65536 )
            if data:
               collector.feed( key.data, data )
               continue
            selector.unregister( key.fileobj )
            key.fileobj.close( )
            collector.finish( key.data )

      remaining = None if timeout is None else max( 0, timeout - (time.monotonic( ) - started) )
      try:
         return process.wait( timeout = remaining )
      except subprocess.TimeoutExpired:
         _terminate( process )
         raise subprocess.TimeoutExpired( plan.argv, timeout ) from None
   except BaseException:
      _terminate( process )
      raise
   finally:
      selector.close( )
      for stream in ( process.stdout, process.stderr ):
         if stream is not None and not stream.closed:
            stream.close( )
      if writer is not None:
         writer.join( timeout = 1 )


def _run_pty( plan, collector, *, payload, cwd, env, timeout, interactive ):
   master_fd, slave_fd = pty.openpty( )
   process = None
   terminal_state = None
   terminal_fd = None
   input_fd = None
   started = time.monotonic( )

   try:
      _copy_terminal_size( slave_fd )
      process = subprocess.Popen(
         plan.argv,
         stdin = slave_fd,
         stdout = slave_fd,
         stderr = slave_fd,
         cwd = cwd,
         env = env,
      )
      os.close( slave_fd )
      slave_fd = None

      if payload:
         os.write( master_fd, payload )

      if interactive and isatty( sys.stdin ):
         terminal_fd = sys.stdin.fileno( )
         input_fd = terminal_fd
         terminal_state = termios.tcgetattr( terminal_fd )
         tty.setraw( terminal_fd )

      while True:
         _check_timeout( process, timeout, started, plan.argv )
         readers = [ master_fd ]
         if input_fd is not None:
            readers.append( input_fd )
         ready, _, _ = select.select( readers, [ ], [ ], 0.05 )

         if master_fd in ready:
            try:
               data = os.read( master_fd, 65536 )
            except OSError as error:
               if error.errno == 5:
                  data = b""
               else:
                  raise
            if data:
               collector.feed( OutputStream.PTY, data )
            elif process.poll( ) is not None:
               break

         if input_fd is not None and input_fd in ready:
            data = os.read( input_fd, 65536 )
            if not data:
               input_fd = None
            elif b"\x03" == data:
               raise KeyboardInterrupt
            else:
               os.write( master_fd, data )

         if process.poll( ) is not None and master_fd not in ready:
            try:
               data = os.read( master_fd, 65536 )
            except OSError as error:
               if error.errno == 5:
                  data = b""
               else:
                  raise
            if data:
               collector.feed( OutputStream.PTY, data )
            else:
               break

      collector.finish( OutputStream.PTY )
      return process.wait( )
   except BaseException:
      if process is not None:
         _terminate( process )
      raise
   finally:
      if terminal_state is not None:
         termios.tcsetattr( terminal_fd, termios.TCSADRAIN, terminal_state )
      if slave_fd is not None:
         os.close( slave_fd )
      os.close( master_fd )

def _normalize_argv( command ):
   if isinstance( command, ( str, bytes ) ) or not isinstance( command, Sequence ):
      raise TypeError( "command must be a sequence of strings" )
   if not command:
      raise ValueError( "command must not be empty" )

   argv = tuple( command )
   if any( not isinstance(argument, str) for argument in argv ):
      raise TypeError( "every command argument must be a string" )
   if not argv[0]:
      raise ValueError( "command executable must not be empty" )
   if any( "\x00" in argument for argument in argv ):
      raise ValueError( "command arguments must not contain null bytes" )
   return argv


def _normalize_output_mode( output ):
   if isinstance( output, OutputMode ):
      return output
   try:
      return OutputMode( output )
   except ( TypeError, ValueError ) as error:
      raise ValueError( "output must be OutputMode.PIPE or OutputMode.PTY" ) from error


def _prepare_environment( env ):
   environment = os.environ.copy( ) if env is None else dict( env )
   columns, lines = get_terminal_dimensions( )
   if columns is not None:
      environment["COLUMNS"] = str( columns )
   if lines is not None:
      environment["LINES"] = str( lines )
   return environment


def _encode_input( input_data, encoding, errors ):
   if input_data is None:
      return b""
   if isinstance( input_data, bytes ):
      return input_data
   if isinstance( input_data, str ):
      return input_data.encode( encoding, errors )
   raise TypeError( "input_data must be str, bytes, or None" )


def _start_stdin_writer( process, payload ):
   if not payload:
      return None

   def write( ):
      try:
         process.stdin.write( payload )
         process.stdin.flush( )
      except ( BrokenPipeError, OSError ):
         pass
      finally:
         process.stdin.close( )

   writer = threading.Thread( target = write, daemon = True )
   writer.start( )
   return writer


def _check_timeout( process, timeout, started, command ):
   if timeout is None or time.monotonic( ) - started <= timeout:
      return
   _terminate( process )
   raise subprocess.TimeoutExpired( command, timeout )


def _terminate( process ):
   if process.poll( ) is not None:
      return
   try:
      os.killpg( process.pid, signal.SIGTERM )
   except ( OSError, ProcessLookupError ):
      process.terminate( )
   try:
      process.wait( timeout = 1 )
   except subprocess.TimeoutExpired:
      try:
         os.killpg( process.pid, signal.SIGKILL )
      except ( OSError, ProcessLookupError ):
         process.kill( )
      process.wait( )


def _copy_terminal_size( destination_fd ):
   columns, lines = get_terminal_dimensions( )
   if columns is None or lines is None:
      return
   try:
      size = struct.pack( "HHHH", lines, columns, 0, 0 )
      fcntl.ioctl( destination_fd, termios.TIOCSWINSZ, size )
   except OSError:
      pass


def _store_command( command, command_log ):
   path = _COMMAND_LOG if command_log is _UNSET else command_log
   if path is None:
      return
   path = pathlib.Path( path )
   with path.open( "a", encoding = "utf-8" ) as stream:
      stream.write( command + "\n" )


def _destination( host, user ):
   if not host:
      raise ValueError( "host must not be empty" )
   return host if user is None else user + "@" + host
