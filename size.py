from enum import IntEnum

import pfw.console



class Size:
   class eGran( IntEnum ):
      B = 1024 ** 0
      K = 1024 ** 1
      M = 1024 ** 2
      G = 1024 ** 3
      S = 512
   # class eGran

   def __init__( self, value: int, gran: eGran = eGran.B ):
      self.__bytes = value * gran
   # def __init__

   def __del__( self ):
      pass
   # def __del__

   def __setattr__( self, attr, value ):
      attr_list = [ i for i in Size.__dict__.keys( ) ]
      if attr in attr_list:
         self.__dict__[ attr ] = value
         return
      raise AttributeError
   # def __setattr__

   def __str__( self ):
      attr_list = [ i for i in Size.__dict__.keys( ) if i[:2] != pfw.base.class_ignore_field ]
      vector = [ ]
      for attr in attr_list:
         vector.append( str( attr ) + " = " + str( self.__dict__.get( attr ) ) )
      name = "Size { " + ", ".join( vector ) + " }"
      return name
   # def __str__

   def __add__( self, other ):
      return self.__bytes + other.__bytes
   # def __add__

   def __sub__( self, other ):
      result: int = self.__bytes - other.__bytes
      if 0 > result:
         return 0
      return result
   # def __sub__

   def __iadd__( self, other ):
      self.__bytes += other.__bytes
      return self
   # def __add__

   def __isub__( self, other ):
      self.__bytes -= other.__bytes
      if 0 > self.__bytes:
         self.__bytes = 0
      return self
   # def __sub__

   def __gt__( self, other ):
      if self.__bytes > other.__bytes:
         return True
      else:
         return False
   # def __gt__

   def __lt__( self, other ):
      if self.__bytes < other.__bytes:
         return True
      else:
         return False
   # def __lt__

   def __eq__( self, other ):
      if self.__bytes == other.__bytes:
         return True
      else:
         return False
   # def __eq__

   def info( self, tabulations: int = 0 ):
      pfw.console.debug.info( self.__class__.__name__, ":", tabs = ( tabulations + 0 ) )
      pfw.console.debug.info( "bytes:     \'", self.__bytes, "\'", tabs = ( tabulations + 1 ) )
      pfw.console.debug.info( "sectors:   \'", self.sectors( ), "\'", tabs = ( tabulations + 1 ) )
   # def info

   def align( self, gran: eGran = eGran.S ): 
      remainder: int = self.__bytes % gran
      if 0 != remainder:
         self.__bytes += gran - remainder
      return self
   # def align

   def bytes( self ):
      return self.__bytes
   # def start

   def kilobytes( self ):
      return self.__bytes // Size.eGran.K
   # def start

   def megabytes( self ):
      return self.__bytes // Size.eGran.M
   # def start

   def gigabytes( self ):
      return self.__bytes // Size.eGran.G
   # def start

   def sectors( self ):
      return self.__bytes // Size.eGran.S
   # def sectors

   __bytes: int = None
# class Size
