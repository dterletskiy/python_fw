import enum
import re

import pfw.base.struct
import pfw.console



class Size:
   class FormatError( TypeError ): pass
   class ParameterError( TypeError ): pass

   class eGran( enum.IntEnum ):
      B = 1024 ** 0
      K = 1024 ** 1
      M = 1024 ** 2
      G = 1024 ** 3
      T = 1024 ** 4
      S = 512
   # class eGran

   # value could have 'int' of 'float' types
   # In last case this means that size has non-integer value of KB, MB, GB and will be converted to integer value of B
   def __init__( self, value, gran: eGran = eGran.B, **kwargs ):
      kw_align = kwargs.get( "align", None )

      self.__bytes = int(value * gran)

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
      attr_list = [ i for i in Size.__dict__.keys( ) if i[:2] != pfw.base.struct.ignore_field]
      vector = [ ]
      for attr in attr_list:
         vector.append( str( attr ) + " = " + str( self.__dict__.get( attr ) ) )
      name = "Size { " + ", ".join( vector ) + " }"
      return name
   # def __str__

   def __add__( self, other ):
      if not isinstance( other, Size ):
         raise Size.ParameterError( "'__add__' operations allowed only with 'Size' types" )
      size_bytes = self.__bytes + other.__bytes
      return Size( size_bytes, Size.eGran.B )
   # def __add__

   def __sub__( self, other ):
      if not isinstance( other, Size ):
         raise Size.ParameterError( "'__sub__' operations allowed only with 'Size' types" )
      size_bytes = self.__bytes - other.__bytes
      if 0 > size_bytes:
         size_bytes = 0
      return Size( size_bytes, Size.eGran.B )
   # def __sub__

   def __iadd__( self, other ):
      if not isinstance( other, Size ):
         raise Size.ParameterError( "'__iadd__' operations allowed only with 'Size' types" )
      self.__bytes += other.__bytes
      return self
   # def __iadd__

   def __isub__( self, other ):
      if not isinstance( other, Size ):
         raise Size.ParameterError( "'__isub__' operations allowed only with 'Size' types" )
      self.__bytes -= other.__bytes
      if 0 > self.__bytes:
         self.__bytes = 0
      return self
   # def __isub__

   def __mul__( self, other ):
      if not isinstance( other, int ):
         raise Size.ParameterError( "'__mul__' operations allowed only with 'int' types" )
      self.__bytes = self.__bytes * other
      return self
   # def __mul__

   def __truediv__( self, other ):
      if not isinstance( other, int ):
         raise Size.ParameterError( "'__truediv__' operations allowed only with 'int' types" )
      self.__bytes = self.__bytes // other
      return self
   # def __truediv__

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

   def info( self, **kwargs ):
      kw_tabulations = kwargs.get( "tabulations", 0 )
      kw_message = kwargs.get( "message", "" )
      pfw.console.debug.info( f"{kw_message} (type {self.__class__.__name__}):", tabs = ( kw_tabulations + 0 ) )

      pfw.console.debug.info( "bytes:     \'", self.__bytes, "\'", tabs = ( kw_tabulations + 1 ) )
      pfw.console.debug.info( "sectors:   \'", self.sectors( )["quotient"], "\'", tabs = ( kw_tabulations + 1 ) )
      pfw.console.debug.info( "kilobytes: \'", self.kilobytes( )["quotient"], "\'", tabs = ( kw_tabulations + 1 ) )
      pfw.console.debug.info( "megabytes: \'", self.megabytes( )["quotient"], "\'", tabs = ( kw_tabulations + 1 ) )
      pfw.console.debug.info( "gigabytes: \'", self.gigabytes( )["quotient"], "\'", tabs = ( kw_tabulations + 1 ) )
   # def info

   def align( self, gran: eGran = eGran.S ): 
      remainder: int = self.__bytes % gran
      if 0 != remainder:
         self.__bytes += gran - remainder
      return self
   # def align

   def size( self, gran: eGran = eGran.B, **kwargs ):
      kw_result = kwargs.get( "result", None )

      quotient = self.__bytes // gran
      remainder = self.__bytes % gran

      if "quotient" == kw_result:
         return quotient
      elif "remainder" == kw_result:
         return remainder

      return { "quotient": quotient, "remainder": remainder }
   # def bytes

   def bytes( self, **kwargs ):
      return self.size( Size.eGran.B, **kwargs )
   # def bytes

   def sectors( self, **kwargs ):
      return self.size( Size.eGran.S, **kwargs )
   # def sectors

   def kilobytes( self, **kwargs ):
      return self.size( Size.eGran.K, **kwargs )
   # def kilobytes

   def megabytes( self, **kwargs ):
      return self.size( Size.eGran.M, **kwargs )
   # def megabytes

   def gigabytes( self, **kwargs ):
      return self.size( Size.eGran.G, **kwargs )
   # def gigabytes

   def count( self, **kwargs ):
      gran = Size.eGran.G
      size_map = self.size( gran )
      if 0 != size_map["remainder"]:
         gran = Size.eGran.M
         size_map = self.size( gran )
      if 0 != size_map["remainder"]:
         gran = Size.eGran.K
         size_map = self.size( gran )
      if 0 != size_map["remainder"]:
         gran = Size.eGran.S
         size_map = self.size( gran )
      if 0 != size_map["remainder"]:
         gran = Size.eGran.B
         size_map = self.size( gran )

      return { "count": size_map["quotient"], "gran": gran }
   # def count

   __bytes: int = None
# class Size

SizeZero       = Size( 0 )
SizeByte       = Size( 1, Size.eGran.B )
SizeKilobyte   = Size( 1, Size.eGran.K )
SizeMegabyte   = Size( 1, Size.eGran.M )
SizeGigabyte   = Size( 1, Size.eGran.G )
SizeSector     = Size( 1, Size.eGran.S )



# Converting test size dimention reprsentation to corresponding Size.eGran value
def text_to_granularity( text: str, **kwargs ):
   text_to_gran = {
      "B": pfw.size.Size.eGran.B,
      "KB": pfw.size.Size.eGran.K,
      "MB": pfw.size.Size.eGran.M,
      "GB": pfw.size.Size.eGran.G,
   }

   kw_dimentions = kwargs.get( "dimentions", text_to_gran )

   if text not in kw_dimentions:
      pfw.console.debug.error( f"'{text}' does not match any dimension pattern" )
      pfw.console.debug.error( f"next dimention patterns are supported: {kw_dimentions.keys( )}" )
      return None

   return kw_dimentions[ text ]
# def text_to_granularity

def string_to_size( string, **kwargs ):
   match = re.match( r'(\d+[.]?\d*)\s*(\w+)', string )
   if not match:
      pfw.console.debug.error( f"format error" )
      return None

   size = float( match.group( 1 ) )
   granularity = text_to_granularity( match.group( 2 ) )

   if not granularity:
      pfw.console.debug.error( f"dimention error" )
      return None

   return Size( size, granularity )

# def string_to_size



def min( *argv ):
   min_value: Size = argv[0]

   for item in argv:
      if None == item:
         continue

      if min_value > item:
         min_value = item

   return min_value
# def min

def max( *argv ):
   max_value: Size = argv[0]

   for item in argv:
      if None == item:
         continue

      if max_value < item:
         max_value = item

   return max_value
# def max

def min_max( *argv ):
   min_value: Size = argv[0]
   max_value: Size = argv[0]

   for item in argv:
      if None == item:
         continue

      if min_value > item:
         min_value = item
      if max_value < item:
         max_value = item

   return [ min_value, max_value ]
# def min_max
