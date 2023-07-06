import os

import pfw.console
import pfw.shell



# Environment structure
# Examples:
#     env = Environment( "name", "value1", "value2", "value3:value4:value5" )
#     env = Environment( "name=value0", "value1", "value2", "value3:value4:value5" )
#     env = Environment( "name=value0" )
#     env = Environment( "name=" )
class Environment:
   def __init__( self, name: str, *argv, **kwargs ):
      kw_delimiter = kwargs.get( "delimiter", ":" )

      self.__values = [ ]
      self.__delimiter = kw_delimiter

      position = name.find( "=" )
      if -1 == position:
         self.__name = name
      else:
         self.__name = name[:position]
         self.push_back( name[ position + 1:len( name ) ] )

      self.push_back( *argv )
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

      pfw.console.debug.info( "name:      \'", self.__name, "\'"        , tabs = ( kw_tabulations + 1 ) )
      pfw.console.debug.info( "delimiter: \'", self.__delimiter, "\'"   , tabs = ( kw_tabulations + 1 ) )
      pfw.console.debug.info( "values:", tabs = ( kw_tabulations + 1 ) )
      for value in self.__values:
         pfw.console.debug.info( "  value:     \'", value, "\'"   , tabs = ( kw_tabulations + 1 ) )
   # def info

   def name( self ):
      return self.__name
   # def name

   def values( self ):
      return self.__values
   # def name

   def value( self, index = None ):
      # return value as string with all values separated by delimiter
      if None == index:
         delimiter = self.__delimiter if self.__delimiter else ""
         return delimiter.join( self.__values )

      if index < 0 or index >= len( self.__values ):
         return None

      # return concrete value
      return self.__values[ index ]
   # def name

   def delimiter( self ):
      return self.__delimiter
   # def delimiter

   def push_back( self, *argv, **kwargs ):
      kw_delimiter = kwargs.get( "delimiter", self.__delimiter )

      values = [ ]
      for value in list( argv ):
         values.extend( value.split( kw_delimiter ) )

      self.__values = self.__values + values
   # def push_back

   def push_front( self, *argv, **kwargs ):
      kw_delimiter = kwargs.get( "delimiter", self.__delimiter )

      values = [ ]
      for value in list( argv ):
         values.extend( value.split( kw_delimiter ) )

      self.__values = values + self.__values
   # def push_front

   def as_string( self ):
      return f"{self.__name}={self.value( )}"
   # def as_string



   __name: str = None
   __values: list = None
   __delimiter: str = None
# class Environment



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
            values = ':'.join( values )

         environment[ name ] = values
   else:
      environment = os.environ.copy( )

   if None != kw_env_overwrite:
      for name, values in kw_env_overwrite.items( ):
         if isinstance( values, list ) or isinstance( values, tuple ):
            values = ':'.join( values )

         environment[ name ] = values

   if None != kw_env_add:
      for name, values in kw_env_add.items( ):
         if isinstance( values, list ) or isinstance( values, tuple ):
            values = ':'.join( values )

         v = environment.get( name, "" )
         environment[ name ] = values
         environment[ name ] += "" if 0 == len( values ) or 0 == len( v ) else ":"
         environment[ name ] += v

   return environment
# def build
