import functools
import operator



# Access nested dictionary items via a list of keys
# https://stackoverflow.com/a/14692747

def get_value_by_list_of_keys( dictionary: dict, keys_list: list ):
   if not isinstance( keys_list, list ) and not isinstance( keys_list, tuple ):
      return None

   return functools.reduce( operator.getitem, keys_list, dictionary )
# def get_value_by_list_of_keys

def set_value_by_list_of_keys( dictionary: dict, keys_list: list, value ):
   if not isinstance( keys_list, list ) and not isinstance( keys_list, tuple ):
      return

   get_value_by_list_of_keys( dictionary, keys_list[:-1] )[ keys_list[-1] ] = value
# sef set_value_by_list_of_keys





def get_value_by_str( dictionary: dict, keys_str: str ):
   if not isinstance( keys_str, str ):
      return None

   keys_list: list = keys_str.split( "." )
   return get_value_by_list( dictionary, keys_list )
# def get_value_by_str

def set_value_by_str( dictionary: dict, keys_str: str, value ):
   if not isinstance( keys_str, str ):
      return

   keys_list: list = keys_str.split( "." )
   get_value_by_list( dictionary, keys_list[:-1] )[ keys_list[-1] ] = value
# sef set_value_by_str

def get_value( dictionary: dict, keys: str ):
   if isinstance( keys, str ):
      return get_value_by_str( dictionary, keys )
   elif isinstance( keys, list ) or isinstance( keys, tuple ):
      return get_value_by_list( dictionary, keys )

   return None
# def get_value

def set_value( dictionary: dict, keys: str, value ):
   if isinstance( keys, str ):
      set_value_by_str( dictionary, keys, value )
   elif isinstance( keys, list ) or isinstance( keys, tuple ):
      set_value_by_list( dictionary, keys, value )
# def set_value
