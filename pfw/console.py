import sys
import os
import getpass
import datetime
import itertools
import logging



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
_LOGGER_IDS       = itertools.count( )



class _AnsiFormatter( logging.Formatter ):
   def format( self, record ):
      string: str = ""
      string += record.pfw_ansi_format if record.pfw_is_colored else ""
      string += record.pfw_tabs * record.pfw_def_tabs
      string += record.getMessage( )
      string += Format.RESET if record.pfw_is_colored else ""

      header: str = ""
      if record.pfw_timestamp:
         timestamp = datetime.datetime.fromtimestamp( record.created ).strftime( "%Y.%m.%d %H.%M.%S.%f" )
         header += timestamp + ": "

      if 1 == record.pfw_inspect:
         header += "[" + record.funcName + ":" + str(record.lineno) + "] -> "
      elif 2 == record.pfw_inspect:
         header += "[" + record.pathname + ":" + record.funcName + ":" + str(record.lineno) + "] -> "

      return header + string
   # def format
# class _AnsiFormatter


class _AnsiHandler( logging.Handler ):
   def emit( self, record ):
      print(
         self.format( record ),
         end = record.pfw_end,
         flush = record.pfw_flush,
         file = record.pfw_file
      )
   # def emit
# class _AnsiHandler


class AnsiDebug:
   def __init__( self, **kwargs ):
      self.__is_colored = kwargs.get( "colored", None )
      self.__inspect: int = kwargs.get( "inspect", 0 )
      self.__timestamp: bool = kwargs.get( "timestamp", True )
      self.__end: str = kwargs.get( "end", '\n' )
      self.__sep: str = kwargs.get( "sep", '' )
      self.__tabs: int = kwargs.get( "tabs", 0 )
      self.__def_tabs: str = kwargs.get( "def_tabs", "   " )
      self.__flush: bool = kwargs.get( "flush", False )
      self.__file = kwargs.get( "file", None )

      logger_name = __name__ + ".AnsiDebug." + str( next(_LOGGER_IDS) )
      self.__logger = logging.getLogger( logger_name )
      self.__logger.setLevel( kwargs.get( "level", logging.DEBUG ) )
      self.__logger.propagate = False

      handler = _AnsiHandler( )
      handler.setFormatter( _AnsiFormatter( ) )
      self.__logger.addHandler( handler )
   # def __init__

   def header( self, *arguments, **kwargs ):
      kwargs.setdefault( "level", logging.INFO )
      self.write( Format.HEADER, *arguments, **kwargs )
   # def header

   def question( self, *arguments, **kwargs ):
      kwargs.setdefault( "level", logging.INFO )
      self.write( Format.QUESTION, *arguments, **kwargs )
   # def question

   def trace( self, *arguments, **kwargs ):
      kwargs.setdefault( "level", logging.DEBUG )
      self.write( Format.TRACE, *arguments, **kwargs )
   # def trace

   def info( self, *arguments, **kwargs ):
      kwargs.setdefault( "level", logging.INFO )
      self.write( Format.INFO, *arguments, **kwargs )
   # def info

   def ok( self, *arguments, **kwargs ):
      kwargs.setdefault( "level", logging.INFO )
      self.write( Format.OK, *arguments, **kwargs )
   # def ok

   def warning( self, *arguments, **kwargs ):
      kwargs.setdefault( "level", logging.WARNING )
      self.write( Format.WARNING, *arguments, **kwargs )
   # def warning

   def error( self, *arguments, **kwargs ):
      kwargs.setdefault( "level", logging.ERROR )
      self.write( Format.ERROR, *arguments, **kwargs )
   # def error

   def marker( self, *arguments, **kwargs ):
      kwargs.setdefault( "level", logging.ERROR )
      self.write( Format.ERROR, "-------------------------", *arguments, "-------------------------", **kwargs )
   # def marker

   def write( self, ansi_format, *arguments, **kwargs ):
      kw_tabs: int = kwargs.get( "tabs", self.__tabs )
      kw_def_tabs: str = kwargs.get( "def_tabs", self.__def_tabs )
      kw_end: str = kwargs.get( "end", self.__end )
      kw_sep: str = kwargs.get( "sep", self.__sep )
      kw_flush: bool = kwargs.get( "flush", self.__flush )
      kw_level: int = kwargs.get( "level", logging.INFO )
      kw_inspect: int = kwargs.get( "inspect", self.__inspect )
      kw_timestamp = kwargs.get( "timestamp", self.__timestamp )

      if not self.__logger.isEnabledFor( kw_level ):
         return

      kw_file = kwargs.get( "file", self.__file )
      if None == kw_file:
         kw_file = sys.stderr if logging.WARNING <= kw_level else sys.stdout

      if None == kw_sep:
         kw_sep = ' '
      elif not isinstance( kw_sep, str ):
         raise TypeError( "sep must be None or a string, not " + type( kw_sep ).__name__ )

      is_colored = self.__is_color_enabled( kw_file )
      message = kw_sep.join( str(arg) for arg in arguments )

      self.__logger.log(
         kw_level,
         message,
         extra = {
            "pfw_ansi_format": ansi_format,
            "pfw_is_colored": is_colored,
            "pfw_tabs": kw_tabs,
            "pfw_def_tabs": kw_def_tabs,
            "pfw_timestamp": kw_timestamp,
            "pfw_inspect": kw_inspect,
            "pfw_end": kw_end,
            "pfw_flush": kw_flush,
            "pfw_file": kw_file
         },
         stacklevel = 3
      )
   # def write

   def prompt( self, string: str = "Press any key...", **kwargs ):
      kw_mask = kwargs.get( "mask", None )

      message = Format.PROMT + string + Format.RESET if self.__is_color_enabled( sys.stdout ) else string

      if None != kw_mask:
         try:
            import pwinput
         except ModuleNotFoundError as error:
            raise ModuleNotFoundError(
               "Masked prompts require the optional 'pwinput' package."
            ) from error

         return pwinput.pwinput( prompt = message, mask = kw_mask )
      else:
         return input( message )
   # def prompt

   def promt( self, string: str = "Press any key...", **kwargs ):
      return self.prompt( string, **kwargs )
   # def promt

   def promt_dep( self, string: str = "Press any key...", **kwargs ):
      kw_type = kwargs.get( "type", "show" )

      def getpassword( string ):
         try:
            import getch
         except ModuleNotFoundError as error:
            raise ModuleNotFoundError(
               "Asterisk prompts require the optional 'getch' package."
            ) from error

         print( string, end = '', flush = True )

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

      message = Format.PROMT + string + Format.RESET if self.__is_color_enabled( sys.stdout ) else string

      return caller( message )
   # def promt_dep

   def __is_color_enabled( self, file ):
      if None != self.__is_colored:
         return bool( self.__is_colored )

      if "NO_COLOR" in os.environ or "dumb" == os.environ.get( "TERM", "" ).lower( ):
         return False

      try:
         return bool( file.isatty( ) )
      except ( AttributeError, OSError, ValueError ):
         return False
   # def __is_color_enabled

   def colored( self, value ):
      _is_colored = self.__is_colored
      self.__is_colored = value
      return _is_colored
   # def colored

   def timestamp( self, value: bool ):
      _timestamp = self.__timestamp
      self.__timestamp = value
      return _timestamp
   # def timestamp

   def level( self, value: int ):
      _level = self.__logger.level
      self.__logger.setLevel( value )
      return _level
   # def level

# class AnsiDebug

printf            = AnsiDebug( inspect = 0 )
debug             = AnsiDebug( inspect = 1 )


