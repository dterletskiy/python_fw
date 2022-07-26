import os
import sys
import subprocess
import enum

import pfw.base
import pfw.console



class eOutput( enum.IntEnum ):
   none     = 0
   collect  = 1
   runtime  = 2
# class eOutput

def output_to_stdout( output: eOutput ):
   mapping: dict = {
      eOutput.none: None,
      eOutput.collect: subprocess.PIPE,
      eOutput.runtime: subprocess.PIPE,
   }
   return mapping[ output ]
# def output_to_stdout



# Example:
# pfw.shell.run_and_wait_with_status( 'ping', '-c 4', 'python.org' )
def run_and_wait_with_status( command: str, *argv, **kwargs ):
   kw_args = kwargs.get( "args", [ ] )
   kw_test = kwargs.get( "test", False )
   kw_env = kwargs.get( "env", None )
   kw_shell = kwargs.get( "shell", False )
   kw_output = kwargs.get( "output", eOutput.runtime )

   arguments: list = list( argv )
   arguments.extend( kw_args )



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

   process = subprocess.Popen(
           command_line
         , stdout = output_to_stdout( kw_output )
         , universal_newlines = True
         , env = kw_env
         , shell = kw_shell
      )

   result_output: str = ""
   if eOutput.none == kw_output:
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
# def run_and_wait_with_status
