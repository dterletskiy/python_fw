import os

import pfw.console
import pfw.shell



def is_process_running( name: str ):
   result = pfw.shell.execute( f"pgrep -x {name}", output = pfw.shell.eOutput.PTY )
   if 0 == result["code"] and None != result["output"]:
      return int( result["output"] )

   return None
# def is_process_running

def kill_process( name: str ):
   pid = is_process_running( name )
   if None != pid:
      pfw.shell.execute( f"sudo -S kill -9 {str( pid )}", output = pfw.shell.eOutput.PTY )

   return None
# def kill_process

def kill_process_all( name: str ):
   pfw.shell.execute( f"killall {name}", output = pfw.shell.eOutput.PTY )
# def kill_process_all

# env_set is { str: [ str ] }
# env_overwrite is { str: [ str ] }
# env_add is { str: [ str ] }
def build_environment( env_set = None, env_overwrite = None, env_add = None ):
   environment: dict = { }

   if None != env_set:
      for key in env_set:
         if 0 != len( env_set[ key ] ):
            environment[ key ] = ':'.join( str( item ) for item in env_set[ key ] )
   else:
      environment = os.environ.copy( )

   if None != env_overwrite:
      for key in env_overwrite:
         if 0 != len( env_overwrite[ key ] ):
            environment[ key ] = ':'.join( str( item ) for item in env_overwrite[ key ] )

   if None != env_add:
      for key in env_add:
         values = environment.get( key, "" )
         if 0 != len( env_add[ key ] ):
            values = ':'.join( str( item ) for item in env_add[ key ] ) + ":" + values
         environment[ key ] = values

   return environment
# def build_environment
