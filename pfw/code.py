import os
import sys
from enum import Enum

import pfw.base
import pfw.console
import pfw.shell
import pfw.size



class Version:
   def __init__( self, major: int, minor: int, patch: int = None ):
      self.__major = major
      self.__minor = minor
      self.__patch = patch
   # def __init__

   def __del__( self ):
      pass
   # def __del__

   def __setattr__( self, attr, value ):
      attr_list = [ i for i in Version.__dict__.keys( ) ]
      if attr in attr_list:
         self.__dict__[ attr ] = value
         return
      raise AttributeError
   # def __setattr__

   def __str__( self ):
      attr_list = [ i for i in Version.__dict__.keys( ) if i[:2] != pfw.base.class_ignore_field ]
      vector = [ ]
      for attr in attr_list:
         vector.append( str( attr ) + " = " + str( self.__dict__.get( attr ) ) )
      name = "Version { " + ", ".join( vector ) + " }"
      return name
   # def __str__

   def info( self, **kwargs ):
      tabulations: int = kwargs.get( "tabulations", 0 )
      pfw.console.debug.info( self.__class__.__name__, ":", tabs = ( tabulations + 0 ) )
      pfw.console.debug.info( "major:  \'", self.__major, "\'", tabs = ( tabulations + 1 ) )
      pfw.console.debug.info( "minor:  \'", self.__minor, "\'", tabs = ( tabulations + 1 ) )
      pfw.console.debug.info( "patch:  \'", self.__patch, "\'", tabs = ( tabulations + 1 ) )
   # def info

   def major( self ):
      return self.__major
   # def major

   def minor( self ):
      return self.__minor
   # def minor

   def patch( self ):
      return self.__patch
   # def type

   def string( self, separator: str = "." ):
      return str(self.__major) + separator + str(self.__minor) + separator + str(self.__patch)
   # def string



   __major: int = None
   __minor: int = None
   __patch: int = None
# class Version



types_map: dict = {
      "string"    : "std::string",
      "vector"    : "std::vector",
      "list"      : "std::list",
      "set"       : "std::set",
      "map"       : "std::map",
      "deqeue"    : "std::deqeue",

      "size_t"    : "std::size_t",

      "int8_t"    : "std::int8_t",
      "int16_t"   : "std::int16_t",
      "int32_t"   : "std::int32_t",
      "int64_t"   : "std::int64_t",

      "uint8_t"   : "std::uint8_t",
      "uint16_t"  : "std::uint16_t",
      "uint32_t"  : "std::uint32_t",
      "uint64_t"  : "std::uint64_t",
   }

def type_builder( _type: str ):
   type_list = pfw.base.multiple_split( str(_type), [ "<", ">", ",", " " ] )

   new_type: str = ""
   for type_item in type_list:
      for key in types_map:
         if key == type_item:
            type_item = types_map[key]
            break
      new_type += type_item

   return new_type
# def type_builder



class Parameter:
   def __init__( self, type: str, name: str, value: str = None ):
      self.__type = type_builder( type )
      self.__name = name
      self.__value = value
   # def __init__

   def __del__( self ):
      pass
   # def __del__

   def __setattr__( self, attr, value ):
      attr_list = [ i for i in Parameter.__dict__.keys( ) ]
      if attr in attr_list:
         self.__dict__[ attr ] = value
         return
      raise AttributeError
   # def __setattr__

   def __str__( self ):
      attr_list = [ i for i in Parameter.__dict__.keys( ) if i[:2] != pfw.base.class_ignore_field ]
      vector = [ ]
      for attr in attr_list:
         vector.append( str( attr ) + " = " + str( self.__dict__.get( attr ) ) )
      name = "Parameter { " + ", ".join( vector ) + " }"
      return name
   # def __str__

   def info( self, **kwargs ):
      tabulations: int = kwargs.get( "tabulations", 0 )
      pfw.console.debug.info( self.__class__.__name__, ":", tabs = ( tabulations + 0 ) )
      pfw.console.debug.info( "type:   \'", self.__type, "\'", tabs = ( tabulations + 1 ) )
      pfw.console.debug.info( "name:   \'", self.__name, "\'", tabs = ( tabulations + 1 ) )
      pfw.console.debug.info( "value:  \'", self.__value, "\'", tabs = ( tabulations + 1 ) )
   # def info

   def type( self ):
      return self.__type
   # def type

   def name( self ):
      return self.__name
   # def type

   def value( self ):
      return self.__value
   # def type



   __type: str = None
   __name: str = None
   __value: str = None
# class Parameter



class Function:
   class eType( Enum ):
      def __str__( self ):
         return str( self.value )

      DEFAULT = "DEFAULT"
      REQUEST = "REQUEST"
      RESPONSE = "RESPONSE"
   # class eType

   def __init__( self, return_type: str = None, name: str = None, type: eType = eType.DEFAULT ):
      self.__return_type = type_builder( return_type )
      self.__name = name
      self.__type = type_builder( type )
      self.__arguments = [ ]
   # def __init__

   def __del__( self ):
      pass
   # def __del__

   def __setattr__( self, attr, value ):
      attr_list = [ i for i in Function.__dict__.keys( ) ]
      if attr in attr_list:
         self.__dict__[ attr ] = value
         return
      raise AttributeError
   # def __setattr__

   def __str__( self ):
      attr_list = [ i for i in Function.__dict__.keys( ) if i[:2] != pfw.base.class_ignore_field ]
      vector = [ ]
      for attr in attr_list:
         vector.append( str( attr ) + " = " + str( self.__dict__.get( attr ) ) )
      name = "Function { " + ", ".join( vector ) + " }"
      return name
   # def __str__

   def info( self, **kwargs ):
      tabulations: int = kwargs.get( "tabulations", 0 )
      pfw.console.debug.info( self.__class__.__name__, ":", tabs = ( tabulations + 0 ) )
      pfw.console.debug.info( "type:         \'", self.__type, "\'", tabs = ( tabulations + 1 ) )
      pfw.console.debug.info( "return_type:  \'", self.__return_type, "\'", tabs = ( tabulations + 1 ) )
      pfw.console.debug.info( "name:         \'", self.__name, "\'", tabs = ( tabulations + 1 ) )
      for argument in self.__arguments: argument.info( tabulations = tabulations + 1 )
   # def info

   def set_type( self, type: str ):
      self.__type = type_builder( type )
   # def set_type

   def set_return_type( self, return_type: str ):
      self.__return_type = type_builder( return_type )
   # def set_return_type

   def set_name( self, name: str ):
      self.__name = name
   # def set_name

   def set_arguments( self, arguments: list ):
      self.__arguments = arguments if None != arguments else [ ]
   # def set_arguments

   def add_argument( self, argument: Parameter ):
      self.__arguments.append( argument )
   # def add_argument

   def type( self ):
      return self.__type
   # def type

   def return_type( self ):
      return self.__return_type
   # def return_type

   def name( self ):
      return self.__name
   # def name

   def arguments( self ):
      return self.__arguments
   # def arguments



   __type: eType = None
   __return_type: str = None
   __name: str = None
   __arguments: list = [ ]
# class Function



class Struct:
   def __init__( self, name: str = None ):
      self.__name = name
      self.__fields = [ ]
      self.__methods = [ ]
   # def __init__

   def __del__( self ):
      pass
   # def __del__

   def __setattr__( self, attr, value ):
      attr_list = [ i for i in Struct.__dict__.keys( ) ]
      if attr in attr_list:
         self.__dict__[ attr ] = value
         return
      raise AttributeError
   # def __setattr__

   def __str__( self ):
      attr_list = [ i for i in Struct.__dict__.keys( ) if i[:2] != pfw.base.class_ignore_field ]
      vector = [ ]
      for attr in attr_list:
         vector.append( str( attr ) + " = " + str( self.__dict__.get( attr ) ) )
      return "Struct { " + ", ".join( vector ) + " }"
   # def __str__

   def info( self, **kwargs ):
      tabulations: int = kwargs.get( "tabulations", 0 )
      pfw.console.debug.info( self.__class__.__name__, ":", tabs = ( tabulations + 0 ) )
      pfw.console.debug.info( "name:      \'", self.__name, "\'", tabs = ( tabulations + 1 ) )
      for field in self.__fields: field.info( tabulations = tabulations + 1 )
      for method in self.__methods: method.info( tabulations = tabulations + 1 )
   # def info

   def set_name( self, name: str ):
      self.__name = name
   # def set_name

   def name( self ):
      return self.__name
   # def name

   def add_field( self, field: Parameter ):
      self.__fields.append( field )
   # def add_field

   def fields( self ):
      return self.__fields
   # def fields

   def add_method( self, method: Function ):
      self.__methods.append( method )
   # def add_method

   def methods( self ):
      return self.__methods
   # def methods



   __name: str = None
   __fields: list = [ ]
   __methods: list = [ ]
# class Struct
