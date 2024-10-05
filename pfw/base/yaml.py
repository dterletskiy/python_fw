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

   def __init__( self, file: str, **kwargs ):
      kw_root_nodes = kwargs.get( "root_nodes", None )
      kw_critical_variables = kwargs.get( "critical_variables", [ ] )
      kw_gen_dir = kwargs.get( "gen_dir", None )
      kw_verbose = kwargs.get( "verbose", False )
      kw_postprocessor = kwargs.get( "postprocessor", None )

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

      yaml_lines = read_file( file )
      yaml_data = yaml.load( yaml_lines, Loader = yaml.SafeLoader )
      # yaml_stream = yaml.compose( yaml_fd )

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

      # Substitute variables' values in the 'variables' node
      self.__process_yaml_data( self.__variables )
      # Substitute the rest of variables' values in the other nodes
      for root_node in self.__root_nodes:
         self.__process_yaml_data( self.__root_nodes[ root_node ] )

      if kw_verbose:
         self.info( )

      if kw_gen_dir:
         timestamp = datetime.datetime.now( ).strftime( "%Y-%m-%d_%H-%M-%S" )
         with open( f"{kw_gen_dir}/merged_{timestamp}.yaml", "w" ) as f:
            f.write( yaml_lines )
         with open( f"{kw_gen_dir}/processed_{timestamp}.yaml", "w" ) as f:
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



   class AV:
      def __init__( self, a, v ):
         self.address = copy.deepcopy( a )
         self.value = copy.deepcopy( v )
      # def __init__

      def __del__( self ):
         pass
      # def __del__

      address: list = [ ]
      value = None
   # class AV

   def __replace( self, value ):
      # pfw.console.debug.trace( f"processing value: '{value}'" ) # @TDA: debug

      if not isinstance( value, str ):
         pfw.console.debug.warning( f"ERROR: '{value}' is not a string, it is {type( value )}" )
         return ( False, value )

      replaced: bool = False
      if findall := re.findall( r'\$\{(.+?)\}', value ):
         # pfw.console.debug.trace( f"findall: '{findall}'" ) # @TDA: debug
         for item in findall:
            variable = self.get_variable( item )
            # pfw.console.debug.trace( f"{item} -> {variable} ({type(variable)})" ) # @TDA: debug
            if isinstance( variable, str ) or isinstance( variable, int ) or isinstance( variable, float ):
               value = value.replace( "${" + item + "}", str(variable) )
            elif isinstance( variable, list ) or isinstance( variable, tuple ) or isinstance( variable, dict ):
               if value == "${" + f"{item}" + "}":
                  value = variable
               else:
                  pfw.console.debug.error( "can substitute only single variable without any other characters by list, tuple or map" )
                  raise YamlFormatError( f"Wrong yaml format error for substitutuion variable '{item}'" )

         if isinstance( value, str ):
            value = self.__replace( value )[1]

         replaced = True

      return ( replaced, value )
   # def __replace

   def __walk( self, iterable, address: list, value_processor = None ):
      # pfw.console.debug.info( f"-> address = {address}" ) # @TDA: debug

      for_adaptation: list = [ ]
      if isinstance( iterable, dict ):
         for key, value in iterable.items( ):
            address.append( key )
            for_adaptation.extend( self.__walk( value, address, value_processor ) )
            del address[-1]
      elif isinstance( iterable, list ) or isinstance( iterable, tuple ):
         for index, item in enumerate( iterable ):
            address.append( index )
            for_adaptation.extend( self.__walk( item, address, value_processor ) )
            del address[-1]
      elif isinstance( iterable, str ):
         ( replaced, new_value ) = value_processor( iterable )
         if replaced:
            # print( f"address = {address}" ) # @TDA: debug
            # print( f"old_value = {iterable}" ) # @TDA: debug
            # print( f"new_value = {new_value}" ) # @TDA: debug
            for_adaptation.append( Processor.AV( address, new_value ) )
      else:
         pass

      # pfw.console.debug.info( f"<- address = {address}" ) # @TDA: debug

      return for_adaptation
   # def __walk

   def __process_yaml_data( self, yaml_data ):
      for item in self.__walk( yaml_data, [ ], self.__replace ):
         pfw.base.dict.set_value_by_list_of_keys( yaml_data, item.address, item.value )
   # def __process_yaml_data



   __variables: dict = { }
   __root_nodes: dict = { }
# class Processor

