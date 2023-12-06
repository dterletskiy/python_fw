import functools
import operator

import pfw.console



class AddressError( Exception ):
   def __init__( self, message ):
      self.message = message
      super( ).__init__( self.message )

   def __str__( self ):
      pfw.console.debug.error( f"{self.__class__}: {self.message}" )
# class AddressError



# Access nested dictionary items via a list of keys
# https://stackoverflow.com/a/14692747

def get_value_by_list_of_keys( dictionary: dict, keys_list: list, default_value = None, **kwargs ):
   kw_verbose = kwargs.get( "verbose", False )
   kw_exception = kwargs.get( "exception", False )

   if not isinstance( keys_list, list ) and not isinstance( keys_list, tuple ):
      return default_value

   try:
      return functools.reduce( operator.getitem, keys_list, dictionary )
   except:
      message = f"no such keys '{keys_list=}' combination int dict '{dictionary=}'" \
         if kw_verbose else f"no such keys combination int dict"

      if kw_exception:
         raise AddressError( message )
      else:
         pfw.console.debug.warning( message )

      return default_value
# def get_value_by_list_of_keys

def set_value_by_list_of_keys( dictionary: dict, keys_list: list, value, **kwargs ):
   kw_verbose = kwargs.get( "verbose", False )
   kw_exception = kwargs.get( "exception", False )

   if not isinstance( keys_list, list ) and not isinstance( keys_list, tuple ):
      return

   try:
      get_value_by_list_of_keys( dictionary, keys_list[:-1], verbose = False )[ keys_list[-1] ] = value
   except:
      message = f"no such keys '{keys_list=}' combination int dict '{dictionary=}'" \
         if kw_verbose else f"no such keys combination int dict"

      if kw_exception:
         raise AddressError( message )
      else:
         pfw.console.debug.warning( message )
# sef set_value_by_list_of_keys



DEFAULT_DELIMITER: str = "."

def get_value_by_str( dictionary: dict, keys_str: str, default_value = None, **kwargs ):
   kw_delimiter: int = kwargs.get( "delimiter", DEFAULT_DELIMITER )

   if not isinstance( keys_str, str ):
      return None

   keys_list: list = keys_str.split( kw_delimiter )
   return get_value_by_list_of_keys( dictionary, keys_list, default_value, **kwargs )
# def get_value_by_str

def set_value_by_str( dictionary: dict, keys_str: str, value, **kwargs ):
   kw_delimiter: int = kwargs.get( "delimiter", DEFAULT_DELIMITER )

   if not isinstance( keys_str, str ):
      return

   keys_list: list = keys_str.split( kw_delimiter )
   set_value_by_list_of_keys( dictionary, keys_list, value, **kwargs )
# sef set_value_by_str



def get_value( dictionary: dict, keys: str, default_value = None, **kwargs ):
   if isinstance( keys, str ):
      return get_value_by_str( dictionary, keys, default_value, **kwargs )
   elif isinstance( keys, list ) or isinstance( keys, tuple ):
      return get_value_by_list_of_keys( dictionary, keys, default_value, **kwargs )

   return None
# def get_value

def set_value( dictionary: dict, keys: str, value, **kwargs ):
   if isinstance( keys, str ):
      set_value_by_str( dictionary, keys, value, **kwargs )
   elif isinstance( keys, list ) or isinstance( keys, tuple ):
      set_value_by_list_of_keys( dictionary, keys, value, **kwargs )
# def set_value
