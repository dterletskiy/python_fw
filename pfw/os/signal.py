import os
import signal

import pfw.base.struct
import pfw.console




class Handler:
   def __init__( self, function, *args, **kwargs ):
      self.__function = function
      self.__args = args
      self.__kwargs = kwargs
   # def __init__

   def __del__( self ):
      pass
   # def __del__

   def __setattr__( self, attr, value ):
      attr_list = [ i for i in Handler.__dict__.keys( ) ]
      if attr in attr_list:
         self.__dict__[ attr ] = value
         return
      raise AttributeError
   # def __setattr__

   def __str__( self ):
      attr_list = [ i for i in Handler.__dict__.keys( ) if i[:2] != pfw.base.struct.ignore_field
 ]
      vector = [ ]
      for attr in attr_list:
         vector.append( str( attr ) + " = " + str( self.__dict__.get( attr ) ) )
      name = "Handler { " + ", ".join( vector ) + " }"
      return name
   # def __str__

   def info( self, **kwargs ):
      tabulations: int = kwargs.get( "tabulations", 0 )
      pfw.console.debug.info( self.__class__.__name__, ":", tabs = ( tabulations + 0 ) )
      pfw.console.debug.info( "function:     \'", self.__function, "\'", tabs = ( tabulations + 1 ) )
      pfw.console.debug.info( "args:         \'", self.__args, "\'", tabs = ( tabulations + 1 ) )
      pfw.console.debug.info( "kwargs:       \'", self.__kwargs, "\'", tabs = ( tabulations + 1 ) )
   # def info

   def function( self ):
      return self.__function
   # def function

   def args( self ):
      return self.__args
   # def args

   def kwargs( self ):
      return self.__kwargs
   # def kwargs

   __function = None
   __args: list = None
   __kwargs: dict = None
# class Handler

g_signal_handlers: dict = { } # { int: list }

def signals_handler( signal_number, frame ):
   pfw.console.debug.warning( f"signal: {signal_number}" )

   handlers = g_signal_handlers.get( signal_number, None )

   if None == handlers:
      pfw.console.debug.error( f"There is no handlers for signal '{signal_number}'" )
      return

   for handler in reversed( handlers ):
      pfw.console.debug.info( f"processing handler {handler.function( )}" )
      handler.function( )( signal_number, frame, *(handler.args( )), **(handler.kwargs( )) )
# def signals_handler

def add_handler( signal_number, function, *args, **kwargs ):
   pfw.console.debug.info( f"signal: {signal_number} / handler: {function}" )

   if signal_number not in g_signal_handlers:
      function_default = signal.signal( signal_number, signals_handler )
      g_signal_handlers[ signal_number ] = [ ]
      # g_signal_handlers[ signal_number ] = [ function_default ]

   handlers = g_signal_handlers[ signal_number ]
   handlers.append( Handler( function, *args, **kwargs ) )
# def add_handler

def remove_handler( signal_number, function ):
   handlers = g_signal_handlers.get( signal_number, None )

   if None == handlers:
      pfw.console.debug.error( f"There is no handlers for signal '{signal_number}'" )
      return False

   for handler in handlers:
      if handler.function( ) == function:
         handlers.remove( handler )
         return True

   pfw.console.debug.error( f"There is no handler '{function}' for signal '{signal_number}'" )
   return False
# def remove_handler
