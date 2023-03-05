import pfw.console



# Converting ASCII string to string with corresponding HEX symbols codes
# https://stackoverflow.com/a/12214880
def ascii_to_hex( string: str, separator: str = ":" ) -> str:
   return f"{separator}".join( "{:02x}".format( ord(c) ) for c in string )
   # return f"{separator}".join( hex( ord(c) )[2:] for c in string )
# def ascii_to_hex



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



def to_string( container, new_line = True ):
   # if True == new_line: print( type( container ) )

   string: str = ""
   if isinstance( container, dict: )
      vector = [ ]
      for key, value in container.items( ):
         vector.append( f"{to_string( key, False )} -> {to_string( value, False )}" )
      string = "{ " + ", ".join( vector ) + " }"
   elif isinstance( container, list: )
      vector = [ to_string( item, False ) for item in container ]
      string = "[ " + ", ".join( vector ) + " ]"
   elif isinstance( container, tuple: )
      vector = [ to_string( item, False ) for item in container ]
      string = "( " + ", ".join( vector ) + " )"
   else:
      string = str( container )

   return string
# def to_string



def string_to_int( string: str ) -> int:
   if not isinstance( string, str ):
      pfw.console.debug.error( f"value is not a string: '{string}'" )
      return False

   try:
      number = int( string )
   except ValueError:
      pfw.console.debug.error( f"wrong string value: '{string}'" )
      return False

   return True
# def string_to_int

