import functools
import operator

import pfw.base.struct
import pfw.console



class Variable:
   def __init__( self, name: str, value: str, _type: str, **kwargs ):
      self.__name = name
      self.__value = value
      self.__type = _type
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

   def name( self ):
      return self.__name
   # def name

   def value( self ):
      return self.__value
   # def value

   def type( self ):
      return self.__type
   # def type



   __name: str = None
   __value: str = None
   __type: str = None
# class Variable



