import enum
import datetime
import time

import pfw.console



class Performance:

   def __init__( self, **kwargs ):
      kw_name = kwargs.get( "name", datetime.datetime.now( ).strftime( "%Y-%m-%d_%H-%M-%S" ) )
      kw_ns = kwargs.get( "ns", False )

      self.reset( )
      self.__name = kw_name
      self.__perf_counter = time.perf_counter_ns if kw_ns else time.perf_counter
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
      attr_list = [ i for i in self.__class__.__dict__.keys( ) if i[:2] != pfw.base.struct.ignore_field]
      vector = [ ]
      for attr in attr_list:
         vector.append( str( attr ) + " = " + str( self.__dict__.get( attr ) ) )
      name = self.__class__.__name__ + " { " + ", ".join( vector ) + " }"
      return name
   # def __str__

   def info( self, **kwargs ):
      kw_tabulations = kwargs.get( "tabulations", 0 )
      kw_message = kwargs.get( "message", "" )
      pfw.console.debug.info( f"{kw_message} (type {self.__class__.__name__}):", tabs = ( kw_tabulations + 0 ) )

      pfw.console.debug.info( "name:      \'", self.__name, "\'", tabs = ( kw_tabulations + 1 ) )
      pfw.console.debug.info( "start:     \'", self.__start, "\'", tabs = ( kw_tabulations + 1 ) )
      pfw.console.debug.info( "points:    \'", self.__points, "\'", tabs = ( kw_tabulations + 1 ) )
      pfw.console.debug.info( "duration:  \'", self.durations( ), "\'", tabs = ( kw_tabulations + 1 ) )
   # def info

   def name( self ):
      return self.__name
   # def name

   def reset( self ):
      self.__start = 0
      self.__points = [ ]
      self.__durations = [ ]
      self.__running = False
   # def reset

   def start( self ):
      if self.__running:
         pfw.console.debug.error( "Performance measurement was already started" )
         return

      self.__running = True
      self.__start = self.__perf_counter( )
   # def start

   def point( self ):
      if self.__running:
         self.__points.append( self.__perf_counter( ) )
      else:
         pfw.console.debug.error( "Performance measurement was not started" )
   # def point

   def stop( self ):
      if self.__running:
         self.__points.append( self.__perf_counter( ) )
         self.__running = False
         self.durations( )
      else:
         pfw.console.debug.error( "Performance measurement was not started" )
   # def stop

   def duration( self, index = 0 ):
      if self.__running:
         pfw.console.debug.warning( "Calculating duration while performance measurement is running" )

      if -len( self.__points ) <= index < len( self.__points ):
         return self.__points[ index ] - self.__start

      return None
   # def duration

   def durations( self ):
      if self.__running:
         pfw.console.debug.warning( "Calculating durations while performance measurement is running" )

      self.__durations = [ ]
      for point in self.__points:
         self.__durations.append( point - self.__start )

      return self.__durations
   # def duration


   __name: str = None
   __start = None
   __points: list = None
   __durations: list = None
   __perf_counter = None
   __running: bool  = False
# class Performance
