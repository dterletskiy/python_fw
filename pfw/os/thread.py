import threading



# Thread class wrapper for "threading.Thread" to store target function returned result
class Thread( threading.Thread ):
   def __init__( self, group = None, target = None, name = None, args = ( ), kwargs = { }, Verbose = None ):
      threading.Thread.__init__( self, group, target, name, args, kwargs )
      self.__result = None

   def run( self ):
      if self._target is not None:
         self.__result = self._target( *self._args, **self._kwargs )

   def join( self, *args ):
      threading.Thread.join( self, *args )
      return self.__result

   def result( self ):
      return self.__result

# class Thread