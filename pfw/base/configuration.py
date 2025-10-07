import os
import sys
import copy
import re
import getopt
import argparse



class ConfigurationData:
   def __init__( self, name: str, required: bool, destination: str ):
      self.__name = copy.deepcopy( name )
      self.__required = copy.deepcopy( required )
      self.__description = copy.deepcopy( destination )
      self.__values = [ ]
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
      attr_list = [ i for i in self.__class__.__dict__.keys( ) if i[:2] != __ ]
      vector = [ f"{str( attr )} = {str( self.__dict__.get( attr ) )}" for attr in attr_list ]
      return self.__class__.__name__ + " { " + ", ".join( vector ) + " }"
   # def __str__

   def __gt__( self, other ):
      return self.__name > other.__name
   # def __gt__

   def __lt__( self, other ):
      return self.__name < other.__name
   # def __lt__

   def __eq__( self, other ):
      return self.__name == other.__name if None != other else False
   # def __eq__

   def info( self, **kwargs ):
      print( self.__class__.__name__, ":" )
      print( "name:         \'", self.__name, "\'" )
      print( "values:       \'", self.__values, "\'" )
      print( "required:     \'", self.__required, "\'" )
      print( "description:  \'", self.__description, "\'" )
   # def info



   # Get name of variable
   def get_name( self ):
      return self.__name
   # def get_name

   # Get index-th value of variable
   def get_value( self, index: int = 0 ):
      return self.__values[ index ] if index < len( self.__values ) else None
   # def get_value

   # Get all values of variable
   def get_values( self ):
      return self.__values
   # def get_values

   def set_value( self, value ):
      self.set_value_single( value )
   # def set_value

   def set_value_single( self, value ):
      self.__values.append( value )
   # def set_value_single

   # Set single value or list of values of variable
   # In fact this operation adds new value/values to existing value list of variable
   def set_value_ext( self, value ):
      if None == value:
         return

      values_to_add: list = [ ]
      if isinstance( value, list ) or isinstance( value, tuple ):
         values_to_add = value
      elif isinstance( value, dict ) or isinstance( value, set ):
         return
      else:
         values_to_add = [ value ]

      self.__values.extend( values_to_add )
   # def set_value_ext

   # Clear all values and new one
   def reset_value( self, value = None ):
      self.__values.clear( )
      self.set_value( value )
   # def reset_value

   # Clear all values of variable
   def reset_value( self, name: str, value = None ):
      self.__values.clear( )

      if None == value:
         self.__values.append( value )
   # def reset_value

   # Test if value/values exists in list of values of variable
   def test_value( self, value ):
      if None == value:
         return False

      values_to_test: list = [ ]
      if isinstance( value, list ) or isinstance( value, tuple ):
         values_to_test = value
      elif isinstance( value, dict ):
         return
      else:
         values_to_test = [ value ]

      for value_to_test in values_to_test:
         if not ( value_to_test in self.__values ):
            return False

      return True
   # def test_value

   def get_required( self ):
      return self.__required
   # def get_required

   def get_description( self ):
      return self.__description
   # def get_description

   def is_satisfy( self ):
      result: bool = 0 < len( self.__values ) if True == self.__required else True

      if False == result:
         print( "configuration variable '%s' is not defined in command line paramenters and configuration file" % ( self.__name ) )
         print( "configuration variable '%s': '%s'" % ( self.__name, self.__description ) )

      return result
   # def is_satisfy



   __name: str = None
   __values: list = [ ]
   __required: bool = False
   __description: str = None
# class ConfigurationData



class ConfigurationContainer:
   def __init__( self, data_list: list = [ ], **kwargs ):
      self.__map = { }
      for data in data_list:
         self.__map[ data.get_name( ) ] = copy.deepcopy( data )
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
      attr_list = [ i for i in self.__class__.__dict__.keys( ) if i[:2] != __ ]
      vector = [ f"{str( attr )} = {str( self.__dict__.get( attr ) )}" for attr in attr_list ]
      return self.__class__.__name__ + " { " + ", ".join( vector ) + " }"
   # def __str__

   def info( self, **kwargs ):
      print( self.__class__.__name__, ":" )
      for name, data in self.__map.items( ):
         data.info( )
         print( );
   # def info



   def set_data( self, data: ConfigurationData ):
      if data.get_name( ) in self.__map.keys( ):
         print( f"update (rewrite) existing data with name '{data.get_name( )}'" )
      self.__map[ data.get_name( ) ] = data
   # def set_data

   def get_data( self, name: str ):
      return self.__map.get( name, None )
   # def get_data

   def get_names( self ):
      return self.__map.keys( )
   # def get_names

   def test( self, name: str ):
      return None != self.get_data( name )
   # def test

   def delete_data( self, name: str ):
      if name in self.__map.keys( ):
         del self.__map[ name ]
   # def delete_data

   def set_value( self, name: str, value ):
      if name not in self.__map.keys( ):
         self.__map[ name ] = ConfigurationData( name, False, "" )

      self.__map[ name ].set_value( value )
   # def set_value

   def reset_value( self, name: str, value ):
      if name not in self.__map.keys( ):
         self.__map[ name ] = ConfigurationData( name, False, "" )

      self.__map[ name ].reset_value( value )
   # def set_value

   def get_values( self, name: str ):
      if name not in self.__map.keys( ):
         return None
      return self.__map[ name ].get_values( )
   # def get_values

   def get_value( self, name: str, index: int = 0 ):
      if name not in self.__map.keys( ):
         return None
      return self.__map[ name ].get_value( )
   # def get_value

   def get_description( self, name: str ):
      data = self.get_data( name )
      return data.get_description( ) if None != data else None
   # def get_description

   def get_required( self, name: str ):
      data = self.get_data( name )
      return data.get_required( ) if None != data else None
   # def get_required

   def is_complete( self ):
      for name, data in self.__map.items( ):
         if False == data.is_satisfy( ):
            return False

      return True
   # def is_complete



   __map: dict = { }
# class ConfigurationContainer



def add_config( app_data, name, value ):
   app_data.set_value( name, value )
# def add_config



def process_cmdline( app_data, argv ):
   print( "Number of arguments:", len(argv) )
   print( "Argument List:", str(argv) )

   parser = argparse.ArgumentParser( description = 'App description' )

   parser.add_argument( "--version", action = "version", version = '%(prog)s 2.0' )

   parser.add_argument( "--config", dest = "config", type = str, action = "append", required = False, help = app_data.get_description( "config" ) )
   parser.add_argument( "--yaml_config", dest = "yaml_config", type = str, action = "store", required = False, help = app_data.get_description( "yaml_config" ) )

   parser.add_argument( "--include", dest = "include", type = str, action = "append", required = False, help = app_data.get_description( "include" ) )
   parser.add_argument( "--pfw", dest = "pfw", type = str, action = "append", required = False, help = app_data.get_description( "pfw" ) )

   parser.add_argument( "--component", dest = "component", type = str, action = "store", required = False, default = "*", help = app_data.get_description( "component" ) )
   parser.add_argument( "--action", dest = "action", type = str, action = "store", required = False, default = "*", help = app_data.get_description( "action" ) )
   parser.add_argument( "--target", dest = "target", type = str, action = "append", required = False, help = app_data.get_description( "target" ) )
   parser.add_argument( "--container", dest = "container", type = str, action = "store", required = False, help = app_data.get_description( "container" ) )

   parser.add_argument( "--test", dest = "test", action = "store_true", help = app_data.get_description( "test" ) )

   # parser.print_help( )
   try:
      argument = parser.parse_args( )
   except argparse.ArgumentError:
      print( 'Catching an ArgumentError' )

   for key, value in argument.__dict__.items( ):
      if None == value:
         continue

      if isinstance( value, list ) or isinstance( value, tuple ):
         for item in value:
            app_data.set_value( key, item )
      else:
         app_data.set_value( key, value )
# def process_cmdline



pattern_include: str = r"^%include:\s*\"(.*)\"\s*$"
pattern_comment: str = r"^\s*#.*$"
pattern_parameter: str = r"^\s*(.*)\s*:\s*(.*)\s*$"

def preprocess_config_file( file ):
   lines: list = [ ]
   file_dir = os.path.dirname( file )

   fd = open( file, "r" )

   for line in fd:
      if match := re.match( pattern_include, line ):
         import_file_name = match.group( 1 )
         import_file_path = os.path.join( file_dir, import_file_name )
         lines.extend( preprocess_config_file( import_file_path ) )
      elif match := re.match( pattern_comment, line ):
         pass
      else:
         lines.append( line )

   fd.close( )
   return lines
# def preprocess_config_file

def process_config_file( app_data ):
   config_files = app_data.get_values( "config" )
   print( f"Processing config files: {config_files}" )
   for config_file in config_files:
      print( f"Processing config file: '{config_file}'" )
      for line in preprocess_config_file( config_file ):
         if match := re.match( pattern_comment, line ):
            pass
         elif match := re.match( pattern_parameter, line ):
            app_data.set_value( match.group( 1 ), match.group( 2 ) )
      print( f"Processed config file: '{config_file}'" )
   print( f"Processed config files: {config_files}" )
# def process_config_file



def process_configuration( app_data, argv, **kwargs ):
   kw_process_cmdline = kwargs.get( "process_cmdline", process_cmdline )
   kw_process_config_file = kwargs.get( "process_config_file", process_config_file )

   if kw_process_cmdline: 
      kw_process_cmdline( app_data, argv )
   if kw_process_config_file:
      kw_process_config_file( app_data )

   current_application_path = os.path.dirname( os.path.realpath( sys.argv[0] ) )
   app_data.set_value( "application", current_application_path )

   used_pfw_path = app_data.get_value( "pfw" )
   if not used_pfw_path:
      used_pfw_path = "submodules/dterletskiy/python_fw"
   if not os.path.isabs( used_pfw_path ):
      used_pfw_path = os.path.join( current_application_path, used_pfw_path )
   app_data.reset_value( "pfw", used_pfw_path )

   if False == app_data.is_complete( ):
      sys.exit( 1 )

   for path in reversed( app_data.get_values( "include" ) ):
      sys.path.insert( 0, path )

   sys.path.insert( 0, app_data.get_value( "pfw" ) )
# def process_configuration



config: ConfigurationContainer = ConfigurationContainer(
      [
         ConfigurationData( "config"            , True  , "Path to configuration file" ),
         ConfigurationData( "yaml_config"       , True  , "Path to yaml project configuration file" ),
         ConfigurationData( "include"           , False , "Additional directory to search import packages" ),
         ConfigurationData( "pfw"               , False , "Python Framework directory location" ),
         ConfigurationData( "component"         , False , "Component name" ),
         ConfigurationData( "action"            , False , "Action name" ),
         ConfigurationData( "container"         , False , "Indicates is this script must be run in container" ),
         ConfigurationData( "test"              , False , "Run in test mode" ),
      ]
   )



# Returns list on parameters names
def names( ):
   return config.get_names( )
# def names

# Returns all values what were set for parameter with mentioned name
def values( name: str ):
   return config.get_values( name )
# def values

# Returns value with mentione index what was set for parameter with mentioned name
def value( name: str, index: int = 0 ):
   return config.get_value( name, index )
# def value



def init( argv = sys.argv[1:], **kwargs ):
   MIN_PYTHON = (3, 9)
   if sys.version_info < MIN_PYTHON:
      print( "Python minimal required version is %s.%s" % MIN_PYTHON )
      print( "Current version is %s.%s" % ( sys.version_info.major, sys.version_info.minor ) )
      sys.exit( 255 )

   process_configuration( config, sys.argv[1:], **kwargs )

   kw_verbose = kwargs.get( "verbose", False )
   if kw_verbose:
      info( )
# def init

def info( ):
   print( )
   config.info( )
# def info
