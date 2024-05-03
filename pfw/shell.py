import os
import sys
import subprocess
import io
import enum
import select
import signal
import errno
import pty
import tty
import termios
import fcntl
import struct
import shlex

import pfw.console



def has_fileno( stream ):
   """
   Cleanly determine whether ``stream`` has a useful ``.fileno()``.
   .. note::
      This function helps determine if a given file-like object can be used
      with various terminal-oriented modules and functions such as `select`,
      `termios`, and `tty`. For most of those, a fileno is all that is
      required; they'll function even if ``stream.isatty()`` is ``False``.
      :param stream: A file-like object.
      :returns:
        ``True`` if ``stream.fileno()`` returns an integer, ``False`` otherwise
        (this includes when ``stream`` lacks a ``fileno`` method).
   .. versionadded:: 1.0
   """
   try:
      return isinstance( stream.fileno( ), int )
   except ( AttributeError, io.UnsupportedOperation ):
      return False
# def has_fileno

def isatty( stream ) :
   """
   Cleanly determine whether ``stream`` is a TTY.
   Specifically, first try calling ``stream.isatty()``, and if that fails
   (e.g. due to lacking the method entirely) fallback to `os.isatty`.
   .. note::
      Most of the time, we don't actually care about true TTY-ness, but
      merely whether the stream seems to have a fileno (per `has_fileno`).
      However, in some cases (notably the use of `pty.fork` to present a
      local pseudoterminal) we need to tell if a given stream has a valid
      fileno but *isn't* tied to an actual terminal. Thus, this function.
   :param stream: A file-like object.
   :returns:
      A boolean depending on the result of calling ``.isatty()`` and/or
      `os.isatty`.
   .. versionadded:: 1.0
   """
   # If there *is* an .isatty, ask it.
   if hasattr( stream, "isatty" ) and callable( stream.isatty ):
      return stream.isatty( )
   # If there wasn't, see if it has a fileno, and if so, ask os.isatty
   elif has_fileno( stream ):
      return os.isatty( stream.fileno( ) )
   # If we got here, none of the above worked, so it's reasonable to assume
   # the darn thing isn't a real TTY.
   return False
# def isatty

def get_terminal_dimensions( ):
    if isatty( sys.stdout ):
        s = struct.pack( 'HHHH', 0, 0, 0, 0 )
        t = fcntl.ioctl( sys.stdout.fileno( ), termios.TIOCGWINSZ, s )
        winsize = struct.unpack( 'hhhh', t )
        return winsize[1], winsize[0]
    else:
        return None, None
# def get_terminal_dimensions



class eOutput( enum.IntEnum ):
   PIPE  = 0
   PTY   = 1
# class eOutput



COMMAND_LOG_FILE: str = None

def init( log_file: str ):
   pfw.console.debug.info( f"set log file for shell command: {log_file}" )
   global COMMAND_LOG_FILE
   COMMAND_LOG_FILE = log_file
# def init

# Function for executing shell command
#     command - shell command
#     argv - list of command arguments
#     args - list of command arguments
#     env - environment variables (default = current script environment variables)
#     shell - boolean parameter what indicates will this command be executed by 'subprocess' with corresponding shell value
#     output - outpot type PIPE or PTY
#     cwd - chande directory before execution to directory mentioned in this parameter (default = None)
#     collect - store output to returned value or not (default = True)
#     print - print output or not (default = True)
#     executable - specifies a replacement program to execute (default = None)
#     universal_newlines - 
#     expected_return_code - expecter return code for succeed execution (default = 0)
#     chroot - use 'chroot' for execution with path mentioned in current parameter (default = None)
#     chroot_bash - use 'chroot' for execution as shell command with path mentioned in current parameter (default = None)
#     method - method what will be used for execution: 'system' or 'subprocess' (default = subprocess)
#     print_command - print executed command in console (default = True)
#     store_command - store executed command to file (default = None)
#     sudo - execute command with 'sudo' (default = False)
#     test - boolean parameter that indicates that final command must not be executed.
#        As the result will be returned dict { code: 255, output: command }, where command is the final shell command what could be executed.
#     ssh - use 'ssh' to execute command remotely.
#        ssh = {
#           "user": <user name (str)> # required
#           "host": <remote host ip (str)># required
#           "sudo": <use sudo to execute command (bool)> # optional
#           "sudo_pwd": <sudo password (str)> # optional
#        }
def run_and_wait_with_status( command: str, *argv, **kwargs ):
   global COMMAND_LOG_FILE

   kw_args = kwargs.get( "args", [ ] )                                  # [ str ]
   kw_test = kwargs.get( "test", False )                                # bool
   kw_env = kwargs.get( "env", os.environ.copy( ) )                     # { str: str }
   kw_shell = kwargs.get( "shell", True )                               # bool
   kw_output = kwargs.get( "output", eOutput.PIPE )                     # pfw.shell.eOutput
   kw_cwd = kwargs.get( "cwd", None )                                   # str
   kw_collect = kwargs.get( "collect", True )                           # bool
   kw_print = kwargs.get( "print", True )                               # bool
   kw_executable = kwargs.get( "executable", None )                     # str
   kw_universal_newlines = kwargs.get( "universal_newlines", False )    # bool
   kw_expected_return_code = kwargs.get( "expected_return_code", 0 )    # int
   kw_chroot = kwargs.get( "chroot", None )                             # str
   kw_chroot_bash = kwargs.get( "chroot_bash", None )                   # str
   kw_method = kwargs.get( "method", "subprocess" )                     # str
   kw_ssh = kwargs.get( "ssh", None )                                   # { str: str }
   kw_sudo = kwargs.get( "sudo", False )                                # bool
   kw_sudo_pwd = kwargs.get( "sudo_pwd", None )                         # str
   kw_print_command = kwargs.get( "print_command", True )               # bool
   kw_store_command = kwargs.get( "store_command", COMMAND_LOG_FILE )   # str
   kw_processor = kwargs.get( "processor", None )                       # function



   terminal_width, terminal_height = get_terminal_dimensions( )
   kw_env["COLUMNS"] = str( terminal_width )
   kw_env["LINES"] = str( terminal_height )



   def output_to_stdout( output: eOutput ):
      mapping: dict = {
         eOutput.PIPE:     ( subprocess.PIPE, subprocess.PIPE ),
         eOutput.PTY:      pty.openpty( )
      }
      return mapping[ output ]
   # def output_to_stdout

   output_tuple = output_to_stdout( kw_output ) if kw_collect or kw_print else ( None, None )

   if True == kw_shell and None == kw_executable:
      kw_executable = "/bin/bash"



   def command_builder( command, *argv, **kwargs ):
      kw_args = kwargs.get( "args", [ ] )
      kw_sudo = kwargs.get( "sudo", False )
      kw_sudo_pwd = kwargs.get( "sudo_pwd", None )
      kw_chroot = kwargs.get( "chroot", None )
      kw_chroot_bash = kwargs.get( "chroot_bash", None )
      kw_ssh = kwargs.get( "ssh", None )

      def builder( command ):
         parameters: list = [ ]

         if isinstance( command, list ) or isinstance( command, tuple ):
            for item in command:
               parameters += builder( item )

         elif isinstance( command, str ):
            parameters = command.split( )

         else:
            raise TypeError

         return parameters
      # def builder

      command_line_list: list = [ ]
      command_line_list += builder( command )
      command_line_list += builder( list( argv ) )
      command_line_list += builder( kw_args )

      if None != kw_chroot_bash:
         command_line_list = [ "chroot", f"{kw_chroot_bash}", "bash", "-c" ] + ["\""] + command_line_list + ["\""]
      elif None != kw_chroot:
         command_line_list = [ "chroot", f"{kw_chroot}" ] + command_line_list

      if None != kw_ssh:
         user_name = kw_ssh["user"]
         host_name = kw_ssh["host"]
         is_sudo = kw_ssh.get( "sudo", False )
         is_sudo_pwd = kw_ssh.get( "sudo_pwd", None )
         ssh_cmd_line_prefix = [ "ssh", f"{user_name}@{host_name}" ]
         ssh_sudo_cmd_line_prefix = [ ]
         if is_sudo:
            if None != is_sudo_pwd:
               ssh_sudo_cmd_line_prefix += [ "echo", "-e", f"\\\"{is_sudo_pwd}\\\"", "|" ]
            ssh_sudo_cmd_line_prefix += [ "sudo", "-S" ]

         command_line_list = ssh_cmd_line_prefix + ["\""] + ssh_sudo_cmd_line_prefix + command_line_list + ["\""]

      if True == kw_sudo:
         command_line_list = [ "sudo", "-S" ] + command_line_list
         if None != kw_sudo_pwd:
            command_line_list = [ "echo", f"\"{kw_sudo_pwd}\"", "|" ] + command_line_list

      command_line_string: str = f"cd {kw_cwd};" if kw_cwd else f""
      command_line_string += ' '.join( command_line_list )

      return { "list": command_line_list, "string": command_line_string }
   # def command_builder

   command_line = command_builder( command, *argv, **kwargs )

   if True == kw_print_command:
      pfw.console.debug.header( f"command: ", command_line['string'] )
      pfw.console.debug.header( f"command: ", command_line['list'] )

   if True == kw_test:
      return { "code": 255, "output": command_line['string'], "command": command_line['string'] }

   if kw_store_command:
      f = open( kw_store_command, "a" )
      f.write( command_line['string'] + "\n" )
      f.close( )

   if True == kw_sudo and None == kw_sudo_pwd:
      fake_message = "Fake command to execute it with \'root\' to avoid password promt string in next command what will go to result"
      os.system( f"sudo echo {fake_message}" )

   return_code = 200
   result_output = None

   if "system" == kw_method:
      return_code = os.system( command_line['string'] )

   elif "subprocess" == kw_method:

      def signal_winsize_handler( signum, frame ):
         pfw.console.debug.warning( f"processing signal: {signum}" )
         if signal.SIGWINCH == signum:
            pass
      # def signal_winsize_handler

      # signal_winsize_handler_old = signal.signal( signal.SIGWINCH, signal_winsize_handler )

      command = command_line['string'] if kw_shell else command_line['list']
      process = subprocess.Popen(
              command
            , stdin = output_tuple[1]
            , stdout = output_tuple[1]
            , stderr = output_tuple[1]
            , universal_newlines = kw_universal_newlines
            , env = kw_env
            , shell = kw_shell
            , executable = kw_executable
            , cwd = kw_cwd
         )

      result_output = ""
      if False == kw_collect and False == kw_print:
         process.wait( )
      else:
         if isatty( sys.stdin ):
            oldtty = termios.tcgetattr( sys.stdin )
            tty.setraw( sys.stdin.fileno( ) )
            tty.setcbreak( sys.stdin.fileno( ) )

         if eOutput.PTY == kw_output:
            master_fd = output_tuple[0]

            while True:
               try:
                  r, _, e = select.select( [master_fd, sys.stdin], [], [], 0.05 )
               except select.error as e:
                  if e[0] != errno.EINTR: raise

               if master_fd in r:
                  output = os.read( master_fd, 10240 )

                  if True == kw_print:
                     sys.stdout.buffer.write( output.replace( b'\n', b'\r\n' ) )
                     sys.stdout.flush( )
                  if True == kw_collect:
                     # output_decoded = output.strip( ).decode( encoding = 'utf-8', errors = 'ignore' )
                     output_decoded = output.decode( encoding = 'utf-8', errors = 'ignore' )
                     result_output += output_decoded
                     if kw_processor: kw_processor( output_decoded )

               if sys.stdin in r:
                  output = os.read( sys.stdin.fileno( ), 10240 )

                  if len( output ) == 0: # @TDA: ???
                     break

                  if output == b'\x03':
                     raise KeyboardInterrupt( )

                  if True == kw_print:
                     os.write( master_fd, output )

               if None != process.poll( ):
                  break

         elif eOutput.PIPE == kw_output:
            while True:
               try:
                  r, _, e = select.select( [process.stdout.fileno( ), process.stderr.fileno( )], [], [], 0.05 )
               except select.error as e:
                  if e[0] != errno.EINTR: raise

               if process.stdout.fileno( ) in r:
                  output = process.stdout.read1( )

                  if True == kw_print:
                     sys.stdout.buffer.write( output.replace( b'\n', b'\r\n' ) )
                     sys.stdout.flush( )
                  if True == kw_collect:
                     # output_decoded = output.strip( ).decode( encoding = 'utf-8', errors = 'ignore' )
                     output_decoded = output.decode( encoding = 'utf-8', errors = 'ignore' )
                     result_output += output_decoded
                     if kw_processor: kw_processor( output_decoded )

               if process.stderr.fileno( ) in r:
                  output = process.stderr.read1( )

                  if True == kw_print:
                     sys.stderr.buffer.write( output.replace( b'\n', b'\r\n' ) )
                     sys.stderr.flush( )
                  if True == kw_collect:
                     # output_decoded = output.strip( ).decode( encoding = "utf-8" )
                     output_decoded = output.decode( encoding = "utf-8" )
                     result_output += output_decoded
                     if kw_processor: kw_processor( output_decoded )

               if sys.stdin in r:
                  output = os.read( sys.stdin.fileno( ), 10240 )

                  if len( output ) == 0: # @TDA: ???
                     break

                  if output == b'\x03':
                     raise KeyboardInterrupt( )

                  if True == kw_print:
                     process.stdin.write( output )
                     process.stdin.flush( )

               if None != process.poll( ):
                  break


         if isatty( sys.stdin ):
            termios.tcsetattr( sys.stdin, termios.TCSADRAIN, oldtty )

      # signal.signal( signal.SIGWINCH, signal_winsize_handler_old )

      return_code = process.poll( )

   else:
      pfw.console.debug.error( f"Undefined method '{kw_method}'" )


   if kw_expected_return_code == return_code:
      pfw.console.debug.info( "RETURN CODE: %s" % ( return_code ) )
   else:
      pfw.console.debug.error( "RETURN CODE: %s" % ( return_code ) )

   return { "code": return_code, "output": result_output, "command": command_line['string'] }
# def run_and_wait_with_status



def execute( command: str, *argv, **kwargs ):
   return run_and_wait_with_status( command, *argv, **kwargs )
# def execute

def executen( commands: list, **kwargs ):
   for command in commands:
      execute( command, **kwargs )
# def execute








def join_command( command, *argv, **kwargs ):
   kw_args = kwargs.get( "args", [ ] )
   kw_debug = kwargs.get( "debug", False )      # bool

   result = command
   for arg in list(argv) + list(kw_args):
      if None == arg:
         continue
      elif not isinstance( arg, str ):
         pfw.console.debug.error( f"'{arg}' must be a string or None" )
         return None
      elif 0 == len( arg ):
         continue

      result += ' ' + arg

   if kw_debug:
      pfw.console.debug.header( f"command: {result}" )

   return result
# def join_command

def build_command( command, *argv, **kwargs ):
   kw_args = kwargs.get( "args", [ ] )
   kw_debug = kwargs.get( "debug", False )      # bool

   result = command
   # result = result + ' ' + ' '.join( shlex.quote( arg ) for arg in argv )
   # result = result + ' ' + ' '.join( shlex.quote( arg ) for arg in kw_args )
   for arg in list(argv) + list(kw_args):
      if None == arg:
         continue
      elif not isinstance( arg, str ):
         pfw.console.debug.error( f"'{arg}' must be a string or None" )
         return None
      elif 0 == len( arg ):
         continue

      result += ' ' + shlex.quote( arg )

   if kw_debug:
      pfw.console.debug.header( f"command: {result}" )

   return result
# def build_command

# Function for executing shell command
#     command - shell command
#     argv - list of command arguments
#     args - list of command arguments
#     env - environment variables (default = current script environment variables)
#     output - outpot type PIPE or PTY
#     cwd - chande directory before execution to directory mentioned in this parameter (default = None)
#     collect - store output to returned value or not (default = True)
#     print - print output or not (default = True)
#     executable - specifies a replacement program to execute (default = None)
#     universal_newlines - 
#     expected_return_code - expecter return code for succeed execution (default = 0)
#     chroot - use 'chroot' for execution with path mentioned in current parameter (default = None)
#     chroot_bash - use 'chroot' for execution as shell command with path mentioned in current parameter (default = None)
#     method - method what will be used for execution: 'system' or 'subprocess' (default = subprocess)
#     print_command - print executed command in console (default = True)
#     store_command - store executed command to file (default = None)
#     sudo - execute command with 'sudo' (default = False)
#     test - boolean parameter that indicates that final command must not be executed.
#        As the result will be returned dict { code: 255, output: command }, where command is the final shell command what could be executed.
#     ssh - use 'ssh' to execute command remotely. ssh with jumphost is supported.
#        ssh = {
#           "user": <user name (str)> # required
#           "host": <remote host ip (str)> # required
#           "sudo": <use sudo to execute command (bool)> # optional
#           "sudo_pwd": <sudo password (str)> # optional
#           "jump_hosts": [ # optional
#                 {
#                    "user": <jumphost user name (str)> # required
#                    "host": <jumphost remote host ip (str)> # required
#                 }, ...
#              ]
#        }
#     processor - function what will called for each line generated in output in runtime
#     result - If a variable of type dictionary is passed as this argument to the function,
#        then this variable will be modified as a result of the function execution.
#        In particular:
#           - the transferred dictionary will be expanded with the key “output”,
#              the value of which will be a string containing the output of the command (the same as return result["output"])
def run_and_wait_with_status2( command: str, *argv, **kwargs ):
   global COMMAND_LOG_FILE

   kw_args = kwargs.get( "args", [ ] )                                  # [ str ]
   kw_test = kwargs.get( "test", False )                                # bool
   kw_env = kwargs.get( "env", os.environ.copy( ) )                     # { str: str }
   kw_output = kwargs.get( "output", eOutput.PIPE )                     # pfw.shell.eOutput
   kw_cwd = kwargs.get( "cwd", None )                                   # str
   kw_collect = kwargs.get( "collect", True )                           # bool
   kw_print = kwargs.get( "print", True )                               # bool
   kw_executable = kwargs.get( "executable", None )                     # str
   kw_universal_newlines = kwargs.get( "universal_newlines", False )    # bool
   kw_expected_return_code = kwargs.get( "expected_return_code", 0 )    # int
   kw_chroot = kwargs.get( "chroot", None )                             # str
   kw_chroot_bash = kwargs.get( "chroot_bash", None )                   # str
   kw_method = kwargs.get( "method", "subprocess" )                     # str
   kw_ssh = kwargs.get( "ssh", None )                                   # { str: str }
   kw_sudo = kwargs.get( "sudo", False )                                # bool
   kw_sudo_pwd = kwargs.get( "sudo_pwd", None )                         # str
   kw_print_command = kwargs.get( "print_command", True )               # bool
   kw_store_command = kwargs.get( "store_command", COMMAND_LOG_FILE )   # str
   kw_processor = kwargs.get( "processor", None )                       # function( str )
   kw_result = kwargs.get( "result", None )



   terminal_width, terminal_height = get_terminal_dimensions( )
   kw_env["COLUMNS"] = str( terminal_width )
   kw_env["LINES"] = str( terminal_height )



   def output_to_stdout( output: eOutput ):
      mapping: dict = {
         eOutput.PIPE:     ( subprocess.PIPE, subprocess.PIPE ),
         eOutput.PTY:      pty.openpty( )
      }
      return mapping[ output ]
   # def output_to_stdout

   output_tuple = output_to_stdout( kw_output ) if kw_collect or kw_print else ( None, None )

   if not kw_executable:
      kw_executable = "/bin/bash"



   def command_builder( command, *argv, **kwargs ):
      kw_args = kwargs.get( "args", [ ] )
      kw_sudo = kwargs.get( "sudo", False )
      kw_sudo_pwd = kwargs.get( "sudo_pwd", None )
      kw_chroot = kwargs.get( "chroot", None )
      kw_chroot_bash = kwargs.get( "chroot_bash", None )
      kw_ssh = kwargs.get( "ssh", None )

      # command_line = build_command( command, *argv, args = kw_args, debug = True )
      command_line = join_command( command, *argv, args = kw_args, debug = True )
      if None == command_line:
         return None

      if None != kw_chroot_bash:
         command_line = "chroot {} bash -c".format( shlex.quote( command_line ) )
      elif None != kw_chroot:
         command_line = "chroot {}".format( shlex.quote( command_line ) )

      if None != kw_ssh:
         if not isinstance( kw_ssh, dict ):
            pfw.console.debug.error( f"'ssh' argument must be a 'dict'" )
            return None

         user_name = kw_ssh["user"]
         host_name = kw_ssh["host"]
         is_sudo = kw_ssh.get( "sudo", False )
         is_sudo_pwd = kw_ssh.get( "sudo_pwd", None )
         jump_hosts = kw_ssh.get( "jump_hosts", [ ] )

         ssh_cmd_line_prefix = f"ssh"
         if None != jump_hosts and 0 < len( jump_hosts ):
            ssh_cmd_line_prefix += " -J"
            for jump_host in jump_hosts:
               jump_host_user_name = jump_host["user"]
               jump_host_host_name = jump_host["host"]
               ssh_cmd_line_prefix += f" {jump_host_user_name}@{jump_host_host_name},"
            ssh_cmd_line_prefix = ssh_cmd_line_prefix[:-1]
         ssh_cmd_line_prefix += f" {user_name}@{host_name}"

         if is_sudo:
            command_line = f"sudo -S {command_line}"
            if None != is_sudo_pwd:
               command_line = f"echo -e {shlex.quote( is_sudo_pwd )} | {command_line}"

         command_line = build_command( ssh_cmd_line_prefix, command_line, debug = True )
         # command_line = join_command( ssh_cmd_line_prefix, command_line, debug = True )
         if None == command_line:
            return None

      if True == kw_sudo:
         command_line = f"sudo -S {command_line}"
         if None != kw_sudo_pwd:
            command_line = f"echo -e {shlex.quote( kw_sudo_pwd )} | {command_line}"

      command_line: str = f"cd {kw_cwd}; {command_line}" if kw_cwd else command_line

      return command_line
   # def command_builder

   command_line = command_builder( command, *argv, **kwargs )
   if None == command_line:
      return { "code": 254, "output": None, "command": None }

   if True == kw_print_command:
      pfw.console.debug.header( f"command: ", command_line )

   if True == kw_test:
      return { "code": 255, "output": None, "command": command_line }

   if kw_store_command:
      f = open( kw_store_command, "a" )
      f.write( command_line + "\n" )
      f.close( )

   if True == kw_sudo and None == kw_sudo_pwd:
      fake_message = "Fake command to execute it with \'root\' to avoid password promt string in next command what will go to result"
      os.system( f"sudo echo {fake_message}" )

   return_code = 200
   result_output = None

   if "system" == kw_method:
      return_code = os.system( command_line )

   elif "subprocess" == kw_method:

      def signal_winsize_handler( signum, frame ):
         pfw.console.debug.warning( f"processing signal: {signum}" )
         if signal.SIGWINCH == signum:
            pass
      # def signal_winsize_handler

      # signal_winsize_handler_old = signal.signal( signal.SIGWINCH, signal_winsize_handler )

      process = subprocess.Popen(
              command_line
            , stdin = output_tuple[1]
            , stdout = output_tuple[1]
            , stderr = output_tuple[1]
            , universal_newlines = kw_universal_newlines
            , env = kw_env
            , shell = True
            , executable = kw_executable
            , cwd = kw_cwd
         )

      result_output = ""
      if False == kw_collect and False == kw_print:
         process.wait( )
      else:
         if isatty( sys.stdin ):
            oldtty = termios.tcgetattr( sys.stdin )
            tty.setraw( sys.stdin.fileno( ) )
            tty.setcbreak( sys.stdin.fileno( ) )

         if eOutput.PTY == kw_output:
            master_fd = output_tuple[0]

            while True:
               try:
                  r, _, e = select.select( [master_fd, sys.stdin], [], [], 0.05 )
               except select.error as e:
                  if e[0] != errno.EINTR: raise

               if master_fd in r:
                  output = os.read( master_fd, 10240 )

                  if True == kw_print:
                     sys.stdout.buffer.write( output.replace( b'\n', b'\r\n' ) )
                     sys.stdout.flush( )
                  if True == kw_collect:
                     # output_decoded = output.strip( ).decode( encoding = 'utf-8', errors = 'ignore' )
                     output_decoded = output.decode( encoding = 'utf-8', errors = 'ignore' )
                     result_output += output_decoded
                     if isinstance( kw_result, dict ): kwargs["result"]["output"] = result_output
                     if kw_processor: kw_processor( output_decoded )

               if sys.stdin in r:
                  output = os.read( sys.stdin.fileno( ), 10240 )

                  if len( output ) == 0: # @TDA: ???
                     break

                  if output == b'\x03':
                     raise KeyboardInterrupt( )

                  if True == kw_print:
                     os.write( master_fd, output )

               if None != process.poll( ):
                  break

         elif eOutput.PIPE == kw_output:
            while True:
               try:
                  r, _, e = select.select( [process.stdout.fileno( ), process.stderr.fileno( )], [], [], 0.05 )
               except select.error as e:
                  if e[0] != errno.EINTR: raise

               if process.stdout.fileno( ) in r:
                  output = process.stdout.read1( )

                  if True == kw_print:
                     sys.stdout.buffer.write( output.replace( b'\n', b'\r\n' ) )
                     sys.stdout.flush( )
                  if True == kw_collect:
                     # output_decoded = output.strip( ).decode( encoding = 'utf-8', errors = 'ignore' )
                     output_decoded = output.decode( encoding = 'utf-8', errors = 'ignore' )
                     result_output += output_decoded
                     if isinstance( kw_result, dict ): kwargs["result"]["output"] = result_output
                     if kw_processor: kw_processor( output_decoded )

               if process.stderr.fileno( ) in r:
                  output = process.stderr.read1( )

                  if True == kw_print:
                     sys.stderr.buffer.write( output.replace( b'\n', b'\r\n' ) )
                     sys.stderr.flush( )
                  if True == kw_collect:
                     # output_decoded = output.strip( ).decode( encoding = "utf-8" )
                     output_decoded = output.decode( encoding = "utf-8" )
                     result_output += output_decoded
                     if isinstance( kw_result, dict ): kwargs["result"]["output"] = result_output
                     if kw_processor: kw_processor( output_decoded )

               if sys.stdin in r:
                  output = os.read( sys.stdin.fileno( ), 10240 )

                  if len( output ) == 0: # @TDA: ???
                     break

                  if output == b'\x03':
                     raise KeyboardInterrupt( )

                  if True == kw_print:
                     process.stdin.write( output )
                     process.stdin.flush( )

               if None != process.poll( ):
                  break


         if isatty( sys.stdin ):
            termios.tcsetattr( sys.stdin, termios.TCSADRAIN, oldtty )

      # signal.signal( signal.SIGWINCH, signal_winsize_handler_old )

      return_code = process.poll( )

   else:
      pfw.console.debug.error( f"Undefined method '{kw_method}'" )


   if kw_expected_return_code == return_code:
      pfw.console.debug.info( "RETURN CODE: %s" % ( return_code ) )
   else:
      pfw.console.debug.error( "RETURN CODE: %s" % ( return_code ) )

   return { "code": return_code, "output": result_output, "command": command_line }
# def run_and_wait_with_status2

def execute2( command: str, *argv, **kwargs ):
   return run_and_wait_with_status2( command, *argv, **kwargs )
# def execute






class CmdLine:
   def __init__( self, command: str, *argv, **kwargs ):
      self.__command = command
      self.__parameters = [ ]

      self.add_parameters( argv )
   # def __init__

   def __del__( self ):
      pass
   # def __del__

   def __setattr__( self, attr, value ):
      attr_list = [ i for i in self.__class__.__dict__.keys( ) ]
      if attr in attr_list:
         self.__dict__[ attr ] = value
         return
      raise AttributeError
   # def __setattr__

   def __str__( self ):
      attr_list = [ i for i in self.__class__.__dict__.keys( ) if i[:2] != pfw.base.struct.ignore_field ]
      vector = [ f"{str( attr )} = {str( self.__dict__.get( attr ) )}" for attr in attr_list ]
      return self.__class__.__name__ + " { " + ", ".join( vector ) + " }"
   # def __str__

   def info( self, **kwargs ):
      kw_tabulations = kwargs.get( "tabulations", 0 )
      kw_message = kwargs.get( "message", "" )
      pfw.console.debug.info( f"{kw_message} (type {self.__class__.__name__}):", tabs = ( kw_tabulations + 0 ) )

      pfw.console.debug.info( "command          :\'", self.__command, "\'", tabs = ( kw_tabulations + 1 ) )
      pfw.console.debug.info( "values:", tabs = ( kw_tabulations + 1 ) )
      for parameter in self.__parameters:
         pfw.console.debug.info( "  parameter   :\'", parameter, "\'", tabs = ( kw_tabulations + 1 ) )
      pfw.console.debug.info( "as string        :\'", self.as_string( ), "\'", tabs = ( kw_tabulations + 1 ) )
   # def info

   def add_parameter( self, parameter ):
      if isinstance( parameter, str ):
         self.__parameters.append( parameter )
      elif isinstance( parameter, CmdLine ):
         self.__parameters.append( parameter.as_string( ) )
      else:
         pfw.console.debug.error( f"parameter '{parameter}' must be a string or CmdLine" )
   # def add_parameter

   def add_parameters( self, parameters ):
      for parameter in parameters:
         self.add_parameter( parameter )
   # def add_parameters

   def as_string( self ):
      # return shlex.join( [self.__command] + self.__parameters )
      return self.__command + " " + shlex.join( self.__parameters )
   # def as_string

   def execute( self, **kwargs ):
      return execute( self.as_string( ), **kwargs )
   # def execute



   __command: str = None
   __parameters: list = None
# class CmdLine

# # cmd_line_1 = pfw.shell.CmdLine( "grep", "cpu ", "/proc/stat" )
# cmd_line_1 = pfw.shell.CmdLine( "ip", "addr" )
# cmd_line_1.info( )
# # cmd_line_1.execute( )

# cmd_line_2 = pfw.shell.CmdLine( "ssh", "root@192.168.1.2", cmd_line_1 )
# cmd_line_2.info( )
# # cmd_line_2.execute( )

# cmd_line_3 = pfw.shell.CmdLine( "ssh", "testpc7@10.22.64.18", cmd_line_2 )
# cmd_line_3.info( )
# # cmd_line_3.execute( )
