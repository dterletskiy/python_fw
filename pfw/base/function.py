import re
import functools
import operator

import pfw.console



class Holder:
   def __init__( self, function, *parameters, **kwargs ):
      self.__function = function
      self.__parameters = parameters
      self.__kwargs = kwargs

      self.__name = "NoName"
      self.__address = "0x0"
      # pfw.console.debug.trace( f"{function=}" )
      if match := re.match( "function=<function (.+) at 0x([0-9a-f]+)>", f"{function=}" ):
         self.__name = match.group(1)
         self.__address = f"0x{match.group(2)}"
      elif match := re.match( "function=<bound method (.+) of <(.+) object at 0x([0-9a-f]+)>>", f"{function=}" ):
         self.__name = f"{match.group(2)}:{match.group(1)}"
         self.__address = f"0x{match.group(3)}"
      else:
         pfw.console.debug.warning( f"Can't parse function: {function=}" )
   # def __init__

   def __del__( self ):
      pass
   # def __del__

   def __call__( self, *argv, **kwargs ):
      _parameters = argv if 0 < len( argv ) else self.__parameters
      _kwargs = kwargs if 0 < len( kwargs ) else self.__kwargs
      pfw.console.debug.trace( f"calling function '{self.__name}' with parameters '{_parameters}' and '{_kwargs}'" )

      return self.__function( *_parameters, **_kwargs )
   # def __call__

   def info( self, **kwargs ):
      kw_tabs = kwargs.get( "tabs", kwargs.get( "tabulations", 0 ) )
      kw_message = kwargs.get( "message", "" )
      pfw.console.printf.info( f"{kw_message} (type {self.__class__.__name__}):", tabs = ( kw_tabs + 0 ) )

      pfw.console.printf.info( "name:        \'", self.__name, "\'", tabs = ( kw_tabs + 1 ) )
      pfw.console.printf.info( "address:     \'", self.__address, "\'", tabs = ( kw_tabs + 1 ) )
      pfw.console.printf.info( "function:    \'", self.__function, "\'", tabs = ( kw_tabs + 1 ) )
      pfw.console.printf.info( "parameters:  \'", self.__parameters, "\'", tabs = ( kw_tabs + 1 ) )
      pfw.console.printf.info( "kwargs:      \'", self.__kwargs, "\'", tabs = ( kw_tabs + 1 ) )
   # def info

   def name( self ):
      return self.__name
   # def name
# class Holder
