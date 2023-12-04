import sys
import inspect
import getpass
import getch



CSI = '\033['
OSC = '\033]'
BEL = '\007'



def code_to_chars( code ):
   return CSI + str(code) + 'm'

def set_title( title ):
   return OSC + '2;' + title + BEL

def clear_screen( mode = 2 ):
   return CSI + str(mode) + 'J'

def clear_line( mode = 2 ):
   return CSI + str(mode) + 'K'

class AnsiCodes( object ):
   def __init__( self ):
      # link: https://github.com/tartley/colorama/tree/master/colorama
      # the subclasses declare class attributes which are numbers.
      # Upon instantiation we define instance attributes, which are the same
      # as the class attributes but wrapped with the ANSI escape sequence
      for name in dir( self ):
         if not name.startswith('_'):
            value = getattr( self, name )
            setattr( self, name, code_to_chars( value ) )

class AnsiCursor( object ):
   def UP(self, n=1):
      return CSI + str(n) + 'A'
   def DOWN(self, n=1):
      return CSI + str(n) + 'B'
   def FORWARD(self, n=1):
      return CSI + str(n) + 'C'
   def BACK(self, n=1):
      return CSI + str(n) + 'D'
   def POS(self, x=1, y=1):
      return CSI + str(y) + ';' + str(x) + 'H'

class AnsiForeground( AnsiCodes ):
   BLACK          = 30
   RED            = 31
   GREEN          = 32
   YELLOW         = 33
   BLUE           = 34
   MAGENTA        = 35
   CYAN           = 36
   WHITE          = 37
   RESET          = 39
   LIGHTBLACK     = 90
   LIGHTRED       = 91
   LIGHTGREEN     = 92
   LIGHTYELLOW    = 93
   LIGHTBLUE      = 94
   LIGHTMAGENTA   = 95
   LIGHTCYAN      = 96
   LIGHTWHITE     = 97

class AnsiBackground( AnsiCodes ):
   BLACK          = 40
   RED            = 41
   GREEN          = 42
   YELLOW         = 43
   BLUE           = 44
   MAGENTA        = 45
   CYAN           = 46
   WHITE          = 47
   RESET          = 49
   LIGHTBLACK     = 100
   LIGHTRED       = 101
   LIGHTGREEN     = 102
   LIGHTYELLOW    = 103
   LIGHTBLUE      = 104
   LIGHTMAGENTA   = 105
   LIGHTCYAN      = 106
   LIGHTWHITE     = 107


class AnsiStyle( AnsiCodes ):
   BOLD           = 1
   DIM            = 2
   UNDERLINED     = 4
   BLINK          = 5
   REVERSE        = 7 # invert the foreground and background colors
   HIDDEN         = 8 # useful for passwords
   RESET          = 0



Foreground        = AnsiForeground( )
Background        = AnsiBackground( )
Style             = AnsiStyle( )
Cursor            = AnsiCursor( )




class AnsiFormat:
   QUESTION       = Foreground.MAGENTA
   PROMT          = Foreground.MAGENTA
   INTERACTION    = Foreground.MAGENTA
   HEADER         = Foreground.LIGHTMAGENTA
   TRACE          = Foreground.RESET
   INFO           = Foreground.LIGHTYELLOW
   OK             = Foreground.GREEN
   ERROR          = Foreground.RED
   WARNING        = Foreground.LIGHTBLUE
   RESET          = Background.RESET + Foreground.RESET + Style.RESET

Format            = AnsiFormat( )



class AnsiDebug:
   def __init__( self, is_colored: bool, inspect: int ):
      self.__is_colored = is_colored
      self.__inspect = inspect

   def header( self, *arguments, **kwargs ):
      self.write( Format.HEADER, *arguments, **kwargs )

   def question( self, *arguments, **kwargs ):
      self.write( Format.QUESTION, *arguments, **kwargs )

   def promt( self, *arguments, **kwargs ):
      self.write( Format.PROMT, *arguments, **kwargs )

   def trace( self, *arguments, **kwargs ):
      self.write( Format.TRACE, *arguments, **kwargs )

   def info( self, *arguments, **kwargs ):
      self.write( Format.INFO, *arguments, **kwargs )

   def ok( self, *arguments, **kwargs ):
      self.write( Format.OK, *arguments, **kwargs )

   def warning( self, *arguments, **kwargs ):
      self.write( Format.WARNING, *arguments, **kwargs )

   def error( self, *arguments, **kwargs ):
      self.write( Format.ERROR, *arguments, **kwargs )

   def marker( self, *arguments, **kwargs ):
      self.write( Format.ERROR, "-------------------------", *arguments, "-------------------------", **kwargs )

   def write( self, ansi_format, *arguments, **kwargs ):
      kw_tabs: int = kwargs.get( "tabs", 0 )
      kw_inspect: int = kwargs.get( "inspect", self.__inspect )
      kw_end: str = kwargs.get( "end", '\n\r' )
      kw_sep: str = kwargs.get( "sep", '' )
      kw_flush: bool = kwargs.get( "flush", False )
      kw_file = kwargs.get( "file", sys.stdout )

      string: str = ""
      if True == self.__is_colored:
         string: str = ansi_format

      string += kw_tabs * "   "
      for argument in arguments:
         string += str( argument )

      if True == self.__is_colored:
         string += Format.RESET

      header: str = ""
      if 1 == kw_inspect:
         frame = inspect.stack( )[2]
         header = "[" + frame.function + ":" + str(frame.lineno) + "] -> "
      elif 2 == kw_inspect:
         frame = inspect.stack( )[2]
         header = "[" + frame.filename + ":" + frame.function + ":" + str(frame.lineno) + "] -> "

      print( header, string, end = kw_end, sep = kw_sep, flush = kw_flush, file = kw_file )
      # sys.stdout.write( header + string + "\n\r" )
      # sys.stdout.flush( )

   def promt( self, string: str = "Press any key...", **kwargs ):
      kw_type = kwargs.get( "type", "show" )

      def getpassword( string ):
         self.write( string, end = '', flush = True )

         passwor = ''
         while True:
            x = getch.getch( )
            if '\r' == x or '\n' == x:
               break
            print( '*', end = '', flush = True )
            passwor += x

         print( "" )

         return passwor
      # def getpassword

      caller = input
      if "hide" == kw_type:
         caller = getpass.getpass
      elif "asterisk" == kw_type:
         caller = getpassword

      if True == self.__is_colored:
         return caller( Format.PROMT + string + Format.RESET )
      else:
         return caller( string )

   def colored( self, is_colored: bool ):
      _is_colored = self.__is_colored
      self.__is_colored = is_colored
      return _is_colored

   __is_colored: bool = True
   __inspect: int = 0

printf            = AnsiDebug( True, 0 )
debug             = AnsiDebug( True, 1 )


