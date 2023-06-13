import os

import pfw.console
import pfw.shell



# env_set            is { str: [ str ] } or { str: str }
# env_overwrite      is { str: [ str ] } or { str: str }
# env_add            is { str: [ str ] } or { str: str }
def build( **kwargs ):
   kw_env_set = kwargs.get( "env_set", None )
   kw_env_overwrite = kwargs.get( "env_overwrite", None )
   kw_env_add = kwargs.get( "env_add", None )

   environment: dict = { }

   if None != kw_env_set:
      for name, values in kw_env_set.items( ):
         if isinstance( values, list ) or isinstance( values, tuple ):
            environment[ name ] = ':'.join( values )
         elif isinstance( values, str ):
            environment[ name ] = values
   else:
      environment = os.environ.copy( )

   if None != kw_env_overwrite:
      for name, values in kw_env_overwrite.items( ):
         if isinstance( values, list ) or isinstance( values, tuple ):
            environment[ name ] = ':'.join( values )
         elif isinstance( values, str ):
            environment[ name ] = values

   if None != kw_env_add:
      for name, values in kw_env_add.items( ):
         v = environment[ name ] if name in environment else ""
         if isinstance( values, list ) or isinstance( values, tuple ):
            environment[ name ] = ':'.join( values )
         elif isinstance( values, str ):
            environment[ name ] = values

         environment[ name ] += "" if 0 == len( environment[ name ] ) else ":"
         environment[ name ] += v

   return environment
# def build
