import os
import stat
import time
import requests

import pfw.console



class_ignore_field = "__"



# link: https://stackoverflow.com/questions/9058305/getting-attributes-of-a-class
# Example:
#     print( class_attributes( ClassName ) )
def class_attributes( cls ):
   result: dict = { "system": { "methods": [ ], "attributes": [ ] }, "user": { "methods": [ ], "attributes": [ ] } }

   s_type: str = None
   f_type: str = None
   for name in cls.__dict__.keys( ):
      s_type = "user"
      if name[:2] == '__': s_type = "system"

      f_type = "attributes"
      if True == callable( cls.__dict__[ name ] ): f_type = "methods"

      result[ s_type ][ f_type ].append( name )

   return result

def string_to_int( string: str, exit_code: int = 1 ) -> int:
   if str != type( string ):
      pfw.console.debug.error( "value is not a string: ", string )
      if 0 != exit_code: exit( exit_code )
      else: return None

   try:
      number = int( string )
      return number
   except ValueError:
      pfw.console.debug.error( "wrong string value: ", string )
      if 0 != exit_code: exit( exit_code )
      else: return None

def to_string( container, new_line = True ):
   # if True == new_line: print( type( container ) )

   string: str = ""
   if dict == type( container ):
      vector = [ ]
      for key in container:
         vector.append( to_string( key, False ) + " -> " + to_string( container[key], False ) )
      string = "{ " + ", ".join( vector ) + " }"
   elif list == type( container ):
      vector = [ ]
      for item in container:
         vector.append( to_string( item, False ) )
      string = "[ " + ", ".join( vector ) + " ]"
   elif tuple == type( container ):
      vector = [ ]
      for item in container:
         vector.append( to_string( item, False ) )
      string = "( " + ", ".join( vector ) + " )"
   else: string = str( container )

   return string

# https://stackoverflow.com/a/12214880
def ascii_string_to_hex_string( string: str, separator: str = ":" ) -> str:
   return f"{separator}".join( "{:02x}".format( ord(c) ) for c in string )
   # f"{separator}".join( hex( ord(c) )[2:] for c in string )

# Split string by multiple separators
# Example:
#     string_list = multiple_split( string, [ "<", ">", ",", " " ] )
def multiple_split( string: str, separators: list ):
   string_list: list = [ string ]
   for separator in separators:
      new_string_list: list = [ ]
      for item_string in string_list:
         l = item_string.split( separator )
         if 1 == len(l):
            new_string_list.extend( l )
            continue
         for count in range( len(l) ):
            # if 0 == len(l[count]): continue
            new_string_list.append( l[count] )
            if count + 1 < len(l):
               new_string_list.append( separator )
      string_list = new_string_list

   return string_list
# def multiple_split

def download( url: str, to: str ):
   file_name = url.split('/')[-1]

   request = requests.get( url, stream=True, allow_redirects=True )

   with open( os.path.join( to, file_name ), 'wb' ) as file:
      count: int = 0;
      for chunk in request.iter_content( chunk_size = 10 * 1024 * 1024 ):
         file.write( chunk )
         count += 1
         pfw.console.debug.trace( "downloaded: ", 10 * count, "MB" )
# def download
