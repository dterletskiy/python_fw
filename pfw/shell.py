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
   kw_args = kwargs.get( "args", [ ] )
   kw_test = kwargs.get( "test", False )
   kw_env = kwargs.get( "env", os.environ.copy( ) )
   kw_shell = kwargs.get( "shell", True )
   kw_output = kwargs.get( "output", eOutput.PIPE )
   kw_cwd = kwargs.get( "cwd", None )
   kw_collect = kwargs.get( "collect", True )
   kw_print = kwargs.get( "print", True )
   kw_executable = kwargs.get( "executable", None )
   kw_universal_newlines = kwargs.get( "universal_newlines", False )
   kw_expected_return_code = kwargs.get( "expected_return_code", 0 )



   terminal_width, terminal_height = pfw.paf.common.get_terminal_dimensions( )
   kw_env["COLUMNS"] = str( terminal_width )
   kw_env["LINES"] = str( terminal_height )



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




   def command_builder( command, args, *argv, **kwargs ):
      kw_string = kwargs.get( "string", False )

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
         pfw.console.debug.header( "command: '", command_line, "'" )
      elif list is type( command_line ):
         pfw.console.debug.header( "command: ", command_line )

      return command_line
   # def command_builder

   def command_builder_test( command, *argv, **kwargs ):
      kw_args = kwargs.get( "args", [ ] )
      kw_string = kwargs.get( "string", False )

      return command_builder( command, kw_args, *argv, string = kw_string )
   # def command_builder_test

   command_line = command_builder( command, kw_args, *argv, string = kw_shell )

   if True == kw_test:
      return { "code": 255, "output": "this is test" }



   def signal_winsize_handler( signum, frame ):
      if signum == signal.SIGWINCH:
         os.kill( sub_process.pid, signal.SIGWINCH )

   old_action = signal.getsignal( signal.SIGWINCH )
   signal.signal( signal.SIGWINCH, signal_winsize_handler )


   process = subprocess.Popen(
           command_line
         , stdin = output_tuple[1]
         , stdout = output_tuple[1]
         , stderr = output_tuple[1]
         , universal_newlines = kw_universal_newlines
         , env = kw_env
         , shell = kw_shell
         , executable = kw_executable
         , cwd = kw_cwd
      )

   result_output: str = ""
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

   return_code: str = process.poll( )


   if kw_expected_return_code == return_code:
      pfw.console.debug.info( "RETURN CODE: %s" % ( return_code ) )
   else:
      pfw.console.debug.error( "RETURN CODE: %s" % ( return_code ) )
      # pfw.console.debug.promt( )
   # pfw.console.debug.info( "COMMAND RESULT: ", process.stdout.strip( ) )

   return { "code": return_code, "output": result_output }
# def run_and_wait_with_status





# class eOutput_old( enum.IntEnum ):
#    none     = 0
#    collect  = 1
#    runtime  = 2
# # class eOutput_old

# def run_and_wait_with_status_old( command: str, *arguments, **kwargs ):
#    kw_test = kwargs.get( "test", False )
#    kw_env = kwargs.get( "env", None )
#    kw_shell = kwargs.get( "shell", False )
#    kw_output = kwargs.get( "output", eOutput_old.runtime )



#    command_line = None
#    if True == kw_shell:
#       command_line = command
#       for argument in arguments:
#          command_line += " " + argument
#    else:
#       command_line: list = [ command ]
#       command_line.extend( arguments )
#    pfw.console.debug.info( command_line )

#    if True == kw_test:
#       return { "code": 255, "output": "this is test" }


#    def output_to_stdout( output: eOutput_old ):
#       mapping: dict = {
#          eOutput_old.none: None,
#          eOutput_old.collect: subprocess.PIPE,
#          eOutput_old.runtime: subprocess.PIPE,
#       }
#       return mapping[ output ]
#    # def output_to_stdout

#    process = subprocess.Popen(
#            command_line
#          , stdout = output_to_stdout( kw_output )
#          , universal_newlines = True
#          , env = kw_env
#          , shell = kw_shell
#       )

#    result_output: str = ""
#    if eOutput_old.none == kw_output:
#       process.wait( )
#    else:
#       while True:
#          output_line = process.stdout.readline( )
#          if output_line:
#             result_output += output_line.strip( )
#             pfw.console.debug.trace( "output: '%s'" % output_line.strip( ) )

#          if None == process.poll( ):
#             continue

#          # Process has finished, read rest of the output 
#          for output_line in process.stdout.readlines( ):
#             if output_line:
#                result_output += output_line.strip( )
#                pfw.console.debug.trace( "output: '%s'" % output_line.strip( ) )
#          break

#    return_code: str = process.poll( )
#    if 0 == return_code:
#       pfw.console.debug.info( "RETURN CODE: %s" % ( return_code ) )
#    else:
#       pfw.console.debug.error( "RETURN CODE: %s" % ( return_code ) )
#       # pfw.console.debug.promt( )
#    # pfw.console.debug.info( "COMMAND RESULT: ", process.stdout.strip( ) )

#    return { "code": return_code, "output": result_output }
# # def run_and_wait_with_status






class eOutput_old( enum.IntEnum ):
   none     = 0
   collect  = 1
   runtime  = 2
# class eOutput_old

# Example:
# pfw.shell.run_and_wait_with_status_old( 'ping', '-c 4', 'python.org' )
def run_and_wait_with_status_old( command: str, *arguments, **kwargs ):
   kw_test = kwargs.get( "test", False )
   kw_env = kwargs.get( "env", None )
   kw_shell = kwargs.get( "shell", False )
   kw_output = kwargs.get( "output", eOutput_old.runtime )



   command_line = None
   if True == kw_shell:
      command_line = command
      for argument in arguments:
         command_line += " " + argument
   else:
      command_line: list = [ command ]
      command_line.extend( arguments )
   pfw.console.debug.info( command_line )

   if True == kw_test:
      return { "code": 255, "output": "this is test" }

   def output_to_stdout_old( output: eOutput_old ):
      mapping: dict = {
         eOutput_old.none: None,
         eOutput_old.collect: subprocess.PIPE,
         eOutput_old.runtime: subprocess.PIPE,
      }
      return mapping[ output ]
   # def output_to_stdout_old

   process = subprocess.Popen(
           command_line
         , stdout = output_to_stdout_old( kw_output )
         , universal_newlines = True
         , env = kw_env
         , shell = kw_shell
      )

   result_output: str = ""
   if eOutput_old.none == kw_output:
      process.wait( )
   else:
      while True:
         output_line = process.stdout.readline( )
         if output_line:
            result_output += output_line.strip( )
            pfw.console.debug.trace( "output: '%s'" % output_line.strip( ) )

         if None == process.poll( ):
            continue

         # Process has finished, read rest of the output 
         for output_line in process.stdout.readlines( ):
            if output_line:
               result_output += output_line.strip( )
               pfw.console.debug.trace( "output: '%s'" % output_line.strip( ) )
         break

   return_code: str = process.poll( )
   if 0 == return_code:
      pfw.console.debug.info( "RETURN CODE: %s" % ( return_code ) )
   else:
      pfw.console.debug.error( "RETURN CODE: %s" % ( return_code ) )
      # pfw.console.debug.promt( )
   # pfw.console.debug.info( "COMMAND RESULT: ", process.stdout.strip( ) )

   return { "code": return_code, "output": result_output }
# def run_and_wait_with_status_old
