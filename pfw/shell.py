import os
import sys
import subprocess
import enum
import select
import signal
import errno
import pty
import tty
import termios

import pfw.base
import pfw.console
import pfw.paf.common



class eOutput( enum.IntEnum ):
   PIPE  = 0
   PTY   = 1
# class eOutput

def run_and_wait_with_status( command: str, *argv, **kwargs ):
   kw_args = kwargs.get( "args", [ ] )                                  # [ str ]
   kw_test = kwargs.get( "test", False )                                # bool
   kw_env_set = kwargs.get( "env_set", { } )                            # { str: [ str ] }
   kw_env_overwrite = kwargs.get( "env_overwrite", { } )                # { str: [ str ] }
   kw_env_add = kwargs.get( "env_add", { } )                            # { str: [ str ] }
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



   def build_environment( env_set, env_overwrite, env_add ):
      environment: dict = { }

      if 0 != len( env_set ):
         for key in env_set:
            if 0 != len( env_set[ key ] ):
               environment[ key ] = ':'.join( str( item ) for item in env_set[ key ] )
      else:
         environment = os.environ.copy( )

      for key in env_overwrite:
         if 0 != len( env_overwrite[ key ] ):
            environment[ key ] = ':'.join( str( item ) for item in env_overwrite[ key ] )

      for key in env_add:
         values = environment.get( key, "" )
         if 0 != len( env_add[ key ] ):
            values = ':'.join( str( item ) for item in env_add[ key ] ) + ":" + values
         environment[ key ] = values

      terminal_width, terminal_height = pfw.paf.common.get_terminal_dimensions( )
      environment["COLUMNS"] = str( terminal_width )
      environment["LINES"] = str( terminal_height )

      return environment
   # def build_environment

   environment: dict = build_environment( kw_env_set, kw_env_overwrite, kw_env_add )



   def output_to_stdout( output: eOutput ):
      mapping: dict = {
         eOutput.PIPE:     ( subprocess.PIPE, subprocess.PIPE ),
         eOutput.PTY:      pty.openpty( )
      }
      return mapping[ output ]
   # def output_to_stdout

   output_tuple = output_to_stdout( kw_output )
   if False == kw_collect and False == kw_print:
      output_tuple = ( None, None )

   if True == kw_shell and None == kw_executable:
      kw_executable = "/bin/bash"

   if "system" == kw_method:
      kw_shell = True



   def command_builder( command, args, *argv, **kwargs ):
      kw_string = kwargs.get( "string", False )
      kw_chroot = kwargs.get( "chroot", None )
      kw_chroot_bash = kwargs.get( "chroot_bash", None )

      def builder( command ):
         parameters: list = [ ]

         if list is type( command ):
            for item in command:
               parameters = parameters + builder( item )

         elif str is type( command ):
            parameters = command.split( )

         else:
            raise TypeError

         return parameters
      # def builder

      command_line: list = [ ]
      command_line = command_line + builder( command )
      command_line = command_line + builder( list( argv ) )
      command_line = command_line + builder( args )

      if True == kw_string:
         command_line = ' '.join( command_line )

      if str is type( command_line ):
         if None != kw_chroot_bash:
            command_line = f"sudo chroot {kw_chroot_bash} bash -c \"" + command_line + "\""
         elif None != kw_chroot:
            command_line = f"sudo chroot {kw_chroot} {command_line}"
         pfw.console.debug.header( "command: '", command_line, "'" )
      elif list is type( command_line ):
         if None != kw_chroot_bash:
            command_line = [ "sudo", "chroot", f"{kw_chroot_bash}", "bash", "-c" ] + ["\""] + command_line + ["\""]
         elif None != kw_chroot:
            command_line = [ "sudo", "chroot", f"{kw_chroot}" ] + command_line
         pfw.console.debug.header( "command: ", command_line )

      return command_line
   # def command_builder

   def command_builder_test( command, *argv, **kwargs ):
      kw_args = kwargs.get( "args", [ ] )
      kw_string = kwargs.get( "string", False )

      return command_builder( command, kw_args, *argv, string = kw_string )
   # def command_builder_test

   command_line = command_builder( command, kw_args, *argv, string = kw_shell, chroot_bash = kw_chroot_bash, chroot = kw_chroot )

   if True == kw_test:
      return { "code": 255, "output": "this is test" }



   return_code = "200"
   result_output = None
   if "system" == kw_method:
      return_code = os.system( command_line )

   elif "subprocess" == kw_method:
      def signal_winsize_handler( signum, frame ):
         if signal.SIGWINCH == signum:
            os.kill( sub_process.pid, signal.SIGWINCH )

      old_action = signal.getsignal( signal.SIGWINCH )
      signal.signal( signal.SIGWINCH, signal_winsize_handler )


      process = subprocess.Popen(
              command_line
            , stdin = output_tuple[1]
            , stdout = output_tuple[1]
            , stderr = output_tuple[1]
            , universal_newlines = kw_universal_newlines
            , env = environment
            , shell = kw_shell
            , executable = kw_executable
            , cwd = kw_cwd
         )

      result_output = ""
      if False == kw_collect and False == kw_print:
         process.wait( )
      else:
         if pfw.paf.common.isatty( sys.stdin ):
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
                     result_output += output.strip( ).decode("utf-8")

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
                     result_output += output.strip( ).decode("utf-8")

               if process.stderr.fileno( ) in r:
                  output = process.stderr.read1( )

                  if True == kw_print:
                     sys.stderr.buffer.write( output.replace( b'\n', b'\r\n' ) )
                     sys.stderr.flush( )
                  if True == kw_collect:
                     result_output += output.strip( ).decode("utf-8")

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


         # elif eOutput.PIPE == kw_output:
         #    while True:
         #       output_line = process.stdout.readline( )
         #       if output_line:
         #          if True == kw_print:
         #             pfw.console.debug.trace( "output: '%s'" % output_line.strip( ) )
         #          if True == kw_collect:
         #             result_output += output_line.strip( )

         #       if None == process.poll( ):
         #          continue

         #       # Process has finished, read rest of the output 
         #       for output_line in process.stdout.readlines( ):
         #          if output_line:
         #             if True == kw_print:
         #                pfw.console.debug.trace( "output: '%s'" % output_line.strip( ) )
         #             if True == kw_collect:
         #                result_output += output_line.strip( )
         #       break


         if pfw.paf.common.isatty( sys.stdin ):
            termios.tcsetattr( sys.stdin, termios.TCSADRAIN, oldtty )

      signal.signal( signal.SIGWINCH, old_action )

      return_code = process.poll( )

   else:
      pfw.console.debug.error( f"Undefined method '{kw_method}'" )


   if kw_expected_return_code == return_code:
      pfw.console.debug.info( "RETURN CODE: %s" % ( return_code ) )
   else:
      pfw.console.debug.error( "RETURN CODE: %s" % ( return_code ) )
      # pfw.console.debug.promt( )

   return { "code": return_code, "output": result_output }
# def run_and_wait_with_status



def execute( command: str, *argv, **kwargs ):
   return run_and_wait_with_status( command, *argv, **kwargs )
# def execute

def executen( commands: list, **kwargs ):
   for command in commands:
      execute( command, **kwargs )
# def execute

