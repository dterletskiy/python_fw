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

   if True == kw_test:
      return { "code": 255, "output": command_line['string'] }

   if kw_store_command:
      f = open( kw_store_command, "a" )
      f.write( command_line['string'] + "\n" )
      f.close( )

   if True == kw_sudo and None == kw_sudo_pwd:
      fake_message = "Fake command to execute it with \'root\' to avoid password promt string in next command what will go to result"
      os.system( f"sudo echo {fake_message}" )

   return_code = "200"
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

   return { "code": return_code, "output": result_output }
# def run_and_wait_with_status



def execute( command: str, *argv, **kwargs ):
   return run_and_wait_with_status( command, *argv, **kwargs )
# def execute

def executen( commands: list, **kwargs ):
   for command in commands:
      execute( command, **kwargs )
# def execute

