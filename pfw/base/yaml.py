#!/usr/bin/python

import copy
import datetime
import re
import os
import enum
import yaml

import pfw.console
import pfw.base.str
import pfw.base.dict



class YamlFormatError( Exception ):
   def __init__( self, message ):
      self.message = message
      super( ).__init__( self.message )

   def __str__( self ):
      pfw.console.debug.error( f"{self.__class__}: {self.message}" )
# class YamlFormatError

class ConfigurationFormatError( Exception ):
   def __init__( self, message ):
      self.message = message
      super( ).__init__( self.message )

   def __str__( self ):
      pfw.console.debug.error( f"{self.__class__}: {self.message}" )
# class ConfigurationFormatError

class ParameterError( Exception ):
   def __init__( self, message ):
      self.message = message
      super( ).__init__( self.message )

   def __str__( self ):
      pfw.console.debug.error( f"{self.__class__}: {self.message}" )
# class ParameterError



class Processor:
   """
   This class is for yaml file processing.
   After yaml file is processed data structure is created.
   Any yaml file node could be accessed using complex dictionary access rules.

   Parameters:
      root_nodes - lits of the root nodes what will be accepted for building data.
         Other root nodes will be ignored.
         If value is 'None' - all root nodes will be accepted except of 'variables'.
         Default value is 'None'.
      critical_variables - list of the variables name what must be defined in the root node 'variables'.
         Default value is empty list.
      gen_dir - directory to store merged and processed yaml filed generated from built structure.
         If value is 'None' - files will not be generated.
         Default value is 'None'.
   """

   def __init__( self, **kwargs ):
      kw_file = kwargs.get( "file", None )
      kw_string = kwargs.get( "string", None )
      kw_root_nodes = kwargs.get( "root_nodes", None )
      kw_critical_variables = kwargs.get( "critical_variables", [ ] )
      kw_gen_dir = kwargs.get( "gen_dir", None )
      kw_verbose = kwargs.get( "verbose", False )
      kw_postprocessor = kwargs.get( "postprocessor", None )

      if None == kw_file and None == kw_string:
         raise ParameterError( "one of the parameters 'file' or 'string' must be defined" )
      if None != kw_file and None != kw_string:
         raise ParameterError( "only one of the parameters 'file' or 'string' must be defined" )

      def read_file( file, spaces: str = "" ):
         pattern: str = r"^(\s*)include:\s*\"(.*)\"\s*$"

         lines: str = ""
         file_dir = os.path.dirname( file )

         yaml_fd = open( file, "r" )

         for line in yaml_fd:
            match = re.match( pattern, line )
            if match:
               import_file_name = match.group( 2 )
               import_file_path = os.path.join( file_dir, import_file_name )
               lines += read_file( import_file_path, match.group( 1 ) )
            else:
               lines += spaces + line

         yaml_fd.close( )
         return lines
      # def read_file

      yaml_lines = read_file( kw_file ) if kw_file else kw_string
      yaml_data = yaml.load( yaml_lines, Loader = yaml.SafeLoader )
      # yaml_stream = yaml.compose( yaml_fd )

      # pattern = r'\$\{(.+?)\}'
      pattern = r'\$\{([^{}]+)\}'
      detected = True
      while True == detected:
         yaml_lines_processed: str = ""
         detected = False
         for yaml_line in yaml_lines.split( "\n" ):
            if findall := re.findall( pattern, yaml_line ):
               detected = True
               for item in findall:
                  value = pfw.base.dict.get_value( yaml_data, f"variables.{item}", None, verbose = True )
                  if None == value:
                     pfw.console.debug.error( yaml_line )
                     raise YamlFormatError( f"no variable name '{item}'" )
                  yaml_line = yaml_line.replace( "${" + item + "}", str(value) )
            yaml_lines_processed += yaml_line + "\n"
         yaml_lines = yaml_lines_processed

      yaml_data = yaml.load( yaml_lines, Loader = yaml.SafeLoader )


      # Read "variables" root node section from yaml file
      self.__variables = yaml_data.get( "variables", { } )
      # Read rest of the root nodes
      if None == kw_root_nodes:
         kw_root_nodes = yaml_data.keys( )
      for root_node in kw_root_nodes:
         if "variables" == root_node:
            continue
         self.__root_nodes[ root_node ] = yaml_data.get( root_node, { } )

      # Override some fields according to "config" file or command line
      if kw_postprocessor: kw_postprocessor( self )

      # Test critical variables
      for critical_variable in kw_critical_variables:
         pfw.console.debug.warning( f"Testing critical variable '{critical_variable}'" )
         if None == self.get_variable( critical_variable ):
            raise ConfigurationFormatError(
                  f"Variable '{critical_variable}' must be defined"
               )

      if kw_verbose:
         self.info( )

      self.__merged_yaml = None
      self.__processed_yaml = None
      if kw_gen_dir:
         pfw.shell.execute( f"mkdir -p {kw_gen_dir}" )
         timestamp = datetime.datetime.now( ).strftime( "%Y-%m-%d_%H-%M-%S-%f" )
         self.__merged_yaml = f"{kw_gen_dir}/merged_{timestamp}.yaml"
         self.__processed_yaml = f"{kw_gen_dir}/processed_{timestamp}.yaml"
         with open( self.__merged_yaml, "w" ) as f:
            f.write( yaml_lines )
         with open( self.__processed_yaml, "w" ) as f:
            data: dict = { "variables": self.__variables }
            data.update( self.__root_nodes )
            yaml.dump( data, f )
   # def __init__

   def __del__( self ):
      pass
   # def __del__

   def info( self, **kwargs ):
      kw_tabs = kwargs.get( "tabs", 0 )
      kw_msg = kwargs.get( "msg", "" )
      pfw.console.debug.info( f"{kw_msg} (type {self.__class__.__name__}):", tabs = ( kw_tabs + 0 ) )
      pfw.console.debug.info( "variables" )
      pfw.console.debug.info( pfw.base.str.to_string( self.__variables ) )
      for root_node_name, root_node_data in self.__root_nodes.items( ):
         pfw.console.debug.info( root_node_name )
         pfw.console.debug.info( pfw.base.str.to_string( root_node_data ) )
   # def info



   def get_variable( self, name, default_value = None ):
      return pfw.base.dict.get_value( self.__variables, name, default_value, verbose = True )
   # def get_variable

   def get_variables( self ):
      return self.__variables
   # def get_variables

   def set_variable( self, name, value ):
      pfw.base.dict.set_value( self.__variables, name, value, verbose = True )
   # def set_variable

   def get_root_node( self, root_node_name: str ):
      return self.__root_nodes[ root_node_name ]
   # def get_root_node

   def merged_yaml( self ):
      return self.__merged_yaml
   # def merged_yaml

   def processed_yaml( self ):
      return self.__processed_yaml
   # def processed_yaml



   __variables: dict = { }
   __root_nodes: dict = { }
# class Processor

