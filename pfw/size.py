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

   def __init__( self, value: int, gran: eGran = eGran.B, **kwargs ):
      kw_align = kwargs.get( "align", None )

      self.__bytes = value * gran

      if None != kw_align:
         self.align( kw_align )
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
      size_bytes = self.__bytes + other.__bytes
      return Size( size_bytes, Size.eGran.B )
   # def __add__

   def __sub__( self, other ):
      size_bytes = self.__bytes - other.__bytes
      if 0 > size_bytes:
         size_bytes = 0
      return Size( size_bytes, Size.eGran.B )
   # def __sub__

   def __iadd__( self, other ):
      self.__bytes += other.__bytes
      return self
   # def __iadd__

   def __isub__( self, other ):
      self.__bytes -= other.__bytes
      if 0 > self.__bytes:
         self.__bytes = 0
      return self
   # def __isub__

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
      if None == other:
         return False

      if self.__bytes == other.__bytes:
         return True

      return False
   # def __eq__

   def info( self, tabulations: int = 0 ):
      pfw.console.debug.info( self.__class__.__name__, ":", tabs = ( tabulations + 0 ) )
      pfw.console.debug.info( "bytes:     \'", self.__bytes, "\'", tabs = ( tabulations + 1 ) )
      pfw.console.debug.info( "sectors:   \'", self.sectors( ), "\'", tabs = ( tabulations + 1 ) )
      pfw.console.debug.info( "kilobytes: \'", self.kilobytes( ), "\'", tabs = ( tabulations + 1 ) )
      pfw.console.debug.info( "megabytes: \'", self.megabytes( ), "\'", tabs = ( tabulations + 1 ) )
   # def info

   def align( self, gran: eGran = eGran.S ): 
      remainder: int = self.__bytes % gran
      if 0 != remainder:
         self.__bytes += gran - remainder
      return self
   # def align

   def bytes( self ):
      return self.__bytes
   # def bytes

   def kilobytes( self ):
      return self.__bytes // Size.eGran.K
   # def kilobytes

   def megabytes( self ):
      return self.__bytes // Size.eGran.M
   # def megabytes

   def gigabytes( self ):
      return self.__bytes // Size.eGran.G
   # def gigabytes

   def sectors( self ):
      return self.__bytes // Size.eGran.S
   # def sectors

   __bytes: int = None
# class Size

SizeZero       = Size( 0 )
SizeByte       = Size( 1, Size.eGran.B )
SizeKilobyte   = Size( 1, Size.eGran.K )
SizeMegabyte   = Size( 1, Size.eGran.M )
SizeGigabyte   = Size( 1, Size.eGran.G )
SizeSector     = Size( 1, Size.eGran.S )



def min( *argv ):
   min_value: Size = argv[0]
   for item in argv:
      if min_value > item:
         min_value = item

   return min_value
# def min

def max( *argv ):
   max_value: Size = argv[0]
   for item in argv:
      if max_value < item:
         max_value = item

   return max_value
# def max

def min_max( *argv ):
   min_value: Size = argv[0]
   max_value: Size = argv[0]
   for item in argv:
      if min_value > item:
         min_value = item
      if max_value < item:
         max_value = item

   return [ min_value, max_value ]
# def min_max
