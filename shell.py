import os
import sys
import subprocess
import re

from enum import Enum

import base.base
import base.console



# Example:
# base.shell.run_and_wait_with_status( 'ping', '-c 4', 'python.org' )
def run_and_wait_with_status( command: str, *arguments, **kwargs ):
   test = kwargs.get( "test", False )

   command_line: list = [ command ]
   command_line.extend( arguments )
   base.console.debug.info( command_line )

   if True == test:
      return { "code": 255, "output": "this is test" }

   process = subprocess.Popen( command_line,  stdout=subprocess.PIPE, universal_newlines=True )

   result_output: str = ""
   while True:
      output_line = process.stdout.readline( )
      if output_line:
         result_output += output_line.strip( )
         base.console.debug.trace( "output: '%s'" % output_line.strip( ) )

      return_code = process.poll( )
      if None == return_code:
         continue

      # Process has finished, read rest of the output 
      for output_line in process.stdout.readlines( ):
         if output_line:
            result_output += output_line.strip( )
            base.console.debug.trace( "output: '%s'" % output_line.strip( ) )
      break

   if 0 == return_code:
      base.console.debug.info( "RETURN CODE: ", return_code )
   else:
      base.console.debug.error( "RETURN CODE: ", return_code )
      # base.console.debug.promt( )
   # base.console.debug.info( "COMMAND RESULT: ", process.stdout.strip( ) )

   return { "code": return_code, "output": result_output }
# def run_and_wait_with_status


# Example:
# base.shell.run_and_wait( 'ping', '-c 4', 'python.org' )
def run_and_wait( command: str, *arguments ):
   command_line: list = [ command ]
   command_line.extend( arguments )
   base.console.debug.info( command_line )

   process = subprocess.Popen( command_line, universal_newlines=True )
   process.wait( )
# def run_and_wait


# Example:
# base.shell.run_and_wait( 'ping', '-c 4', 'python.org' )
def run_and_communicate( command: str, *arguments ):
   command_line: list = [ command ]
   command_line.extend( arguments )
   base.console.debug.info( command_line )

   process = subprocess.Popen( command_line,  stdout=subprocess.PIPE, universal_newlines=True )
   process.communicate( )
# def run_and_wait



def run_with_result( command: str, *arguments ):
   command_line: list = [ command ]
   command_line.extend( arguments )
   base.console.debug.info( command_line )

   process = subprocess.run( command_line, stdout=subprocess.PIPE )
   result = process.stdout.decode('utf-8')
   base.console.debug.warning( "result: \'", result, "\'" )
# def run
