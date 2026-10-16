import datetime
import itertools
import logging
import sys

from pfw import terminal



TRACE = 5
_LOGGER_IDS = itertools.count( )
_UNSET = object( )
_GLOBAL_TIMESTAMP = True

logging.addLevelName( TRACE, "TRACE" )



class AnsiFormat:
   PROMT          = terminal.Foreground.MAGENTA
   TRACE          = terminal.Foreground.LIGHTBLACK
   DEBUG          = terminal.Foreground.LIGHTCYAN
   INFO           = terminal.Foreground.LIGHTYELLOW
   ERROR          = terminal.Foreground.RED
   WARNING        = terminal.Foreground.LIGHTBLUE
   CRITICAL       = terminal.Style.BOLD + terminal.Foreground.LIGHTRED
   RESET          = terminal.Background.RESET + terminal.Foreground.RESET + terminal.Style.RESET


Format = AnsiFormat( )



def configure( *, colored = _UNSET, timestamp = _UNSET ):
   """Configure application-wide defaults for console logging."""
   global _GLOBAL_TIMESTAMP

   if colored is not _UNSET and None != colored and not isinstance( colored, bool ):
      raise TypeError( "colored must be True, False, or None" )
   if timestamp is not _UNSET and not isinstance( timestamp, bool ):
      raise TypeError( "timestamp must be a bool" )

   previous = {
      "colored": terminal.get_color_mode( ),
      "timestamp": _GLOBAL_TIMESTAMP
   }

   if colored is not _UNSET:
      terminal.set_color_mode( colored )
   if timestamp is not _UNSET:
      _GLOBAL_TIMESTAMP = timestamp

   return previous



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

      result = header + string

      if record.exc_info:
         if not record.exc_text:
            record.exc_text = self.formatException( record.exc_info )
         result += "\n" + record.exc_text

      if record.stack_info:
         result += "\n" + self.formatStack( record.stack_info )

      return result


class _AnsiHandler( logging.Handler ):
   def emit( self, record ):
      print(
         self.format( record ),
         end = record.pfw_end,
         flush = record.pfw_flush,
         file = record.pfw_file
      )


class ConsoleLogger:
   def __init__( self, **kwargs ):
      self.__is_colored = kwargs.get( "colored", _UNSET )
      self.__inspect: int = kwargs.get( "inspect", 0 )
      self.__timestamp = kwargs.get( "timestamp", _UNSET )
      self.__end: str = kwargs.get( "end", '\n' )
      self.__sep: str = kwargs.get( "sep", '' )
      self.__tabs: int = kwargs.get( "tabs", 0 )
      self.__def_tabs: str = kwargs.get( "def_tabs", "   " )
      self.__flush: bool = kwargs.get( "flush", False )
      self.__file = kwargs.get( "file", None )

      logger_name = __name__ + ".ConsoleLogger." + str( next(_LOGGER_IDS) )
      self.__logger = logging.getLogger( logger_name )
      self.__logger.setLevel( kwargs.get( "level", TRACE ) )
      self.__logger.propagate = False

      handler = _AnsiHandler( )
      handler.setFormatter( _AnsiFormatter( ) )
      self.__logger.addHandler( handler )

   def trace( self, *arguments, **kwargs ):
      kwargs.setdefault( "level", TRACE )
      self.write( Format.TRACE, *arguments, **kwargs )

   def debug( self, *arguments, **kwargs ):
      kwargs.setdefault( "level", logging.DEBUG )
      self.write( Format.DEBUG, *arguments, **kwargs )

   def info( self, *arguments, **kwargs ):
      kwargs.setdefault( "level", logging.INFO )
      self.write( Format.INFO, *arguments, **kwargs )

   def warning( self, *arguments, **kwargs ):
      kwargs.setdefault( "level", logging.WARNING )
      self.write( Format.WARNING, *arguments, **kwargs )

   def error( self, *arguments, **kwargs ):
      kwargs.setdefault( "level", logging.ERROR )
      self.write( Format.ERROR, *arguments, **kwargs )

   def critical( self, *arguments, **kwargs ):
      kwargs.setdefault( "level", logging.CRITICAL )
      self.write( Format.CRITICAL, *arguments, **kwargs )

   def exception( self, *arguments, **kwargs ):
      kwargs.setdefault( "level", logging.ERROR )
      kwargs.setdefault( "exc_info", True )
      self.write( Format.ERROR, *arguments, **kwargs )

   def log( self, level, *arguments, **kwargs ):
      if not isinstance( level, int ):
         raise TypeError( "level must be an integer" )

      kwargs["level"] = level
      self.write( self.__format_for_level(level), *arguments, **kwargs )

   def write( self, ansi_format, *arguments, **kwargs ):
      kw_tabs: int = kwargs.get( "tabs", self.__tabs )
      kw_def_tabs: str = kwargs.get( "def_tabs", self.__def_tabs )
      kw_end: str = kwargs.get( "end", self.__end )
      kw_sep: str = kwargs.get( "sep", self.__sep )
      kw_flush: bool = kwargs.get( "flush", self.__flush )
      kw_level: int = kwargs.get( "level", logging.INFO )
      kw_inspect: int = kwargs.get( "inspect", self.__inspect )
      kw_timestamp = kwargs.get( "timestamp", self.__effective_timestamp( ) )
      kw_colored = kwargs.get( "colored", _UNSET )
      kw_exc_info = kwargs.get( "exc_info", None )
      kw_extra = kwargs.get( "extra", None )
      kw_stack_info: bool = kwargs.get( "stack_info", False )
      kw_stacklevel: int = kwargs.get( "stacklevel", 1 )

      if not self.__logger.isEnabledFor( kw_level ):
         return

      kw_file = kwargs.get( "file", self.__file )
      if None == kw_file:
         kw_file = sys.stderr if logging.WARNING <= kw_level else sys.stdout

      if None == kw_sep:
         kw_sep = ' '
      elif not isinstance( kw_sep, str ):
         raise TypeError( "sep must be None or a string, not " + type( kw_sep ).__name__ )

      is_colored = terminal.is_color_enabled( kw_file, self.__effective_colored(kw_colored) )
      message = kw_sep.join( str(arg) for arg in arguments )

      extra = { } if None == kw_extra else dict( kw_extra )
      extra.update({
         "pfw_ansi_format": ansi_format,
         "pfw_is_colored": is_colored,
         "pfw_tabs": kw_tabs,
         "pfw_def_tabs": kw_def_tabs,
         "pfw_timestamp": kw_timestamp,
         "pfw_inspect": kw_inspect,
         "pfw_end": kw_end,
         "pfw_flush": kw_flush,
         "pfw_file": kw_file
      })

      self.__logger.log(
         kw_level,
         message,
         exc_info = kw_exc_info,
         extra = extra,
         stack_info = kw_stack_info,
         stacklevel = kw_stacklevel + 2
      )

   def __format_for_level( self, level ):
      if logging.CRITICAL <= level:
         return Format.CRITICAL
      if logging.ERROR <= level:
         return Format.ERROR
      if logging.WARNING <= level:
         return Format.WARNING
      if logging.INFO <= level:
         return Format.INFO
      if logging.DEBUG <= level:
         return Format.DEBUG
      return Format.TRACE

   def __effective_colored( self, colored = _UNSET ):
      if colored is not _UNSET:
         return colored
      if self.__is_colored is _UNSET:
         return terminal.get_color_mode( )
      return self.__is_colored

   def __effective_timestamp( self ):
      if self.__timestamp is _UNSET:
         return _GLOBAL_TIMESTAMP
      return self.__timestamp

   def colored( self, value ):
      previous = self.__effective_colored( )
      self.__is_colored = value
      return previous

   def color_mode( self ):
      return self.__effective_colored( )

   def timestamp( self, value: bool ):
      previous = self.__effective_timestamp( )
      self.__timestamp = value
      return previous

   def level( self, value: int ):
      previous = self.__logger.level
      self.__logger.setLevel( value )
      return previous


AnsiDebug = ConsoleLogger
printf = ConsoleLogger( inspect = 0 )
logger = ConsoleLogger( inspect = 1 )


def trace( *arguments, **kwargs ):
   kwargs["stacklevel"] = kwargs.get( "stacklevel", 1 ) + 1
   return logger.trace( *arguments, **kwargs )


def debug( *arguments, **kwargs ):
   kwargs["stacklevel"] = kwargs.get( "stacklevel", 1 ) + 1
   return logger.debug( *arguments, **kwargs )


def info( *arguments, **kwargs ):
   kwargs["stacklevel"] = kwargs.get( "stacklevel", 1 ) + 1
   return logger.info( *arguments, **kwargs )


def warning( *arguments, **kwargs ):
   kwargs["stacklevel"] = kwargs.get( "stacklevel", 1 ) + 1
   return logger.warning( *arguments, **kwargs )


def error( *arguments, **kwargs ):
   kwargs["stacklevel"] = kwargs.get( "stacklevel", 1 ) + 1
   return logger.error( *arguments, **kwargs )


def critical( *arguments, **kwargs ):
   kwargs["stacklevel"] = kwargs.get( "stacklevel", 1 ) + 1
   return logger.critical( *arguments, **kwargs )


def exception( *arguments, **kwargs ):
   kwargs["stacklevel"] = kwargs.get( "stacklevel", 1 ) + 1
   return logger.exception( *arguments, **kwargs )


def log( level, *arguments, **kwargs ):
   kwargs["stacklevel"] = kwargs.get( "stacklevel", 1 ) + 1
   return logger.log( level, *arguments, **kwargs )
