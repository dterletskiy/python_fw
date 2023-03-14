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



def to_string( container, **kwargs ):
   kw_new_line = kwargs.get( "new_line", True )
   kw_tabs = kwargs.get( "tabs", 3 )
   kw_level = kwargs.get( "level", 0 )

   splitter = " ,"

   def tabulations( level ):
      return kw_tabs * level * " "
   # def tabulations

   kwargs["level"] = kw_level + 1

   string: str = ""
   if isinstance( container, dict ):
      string += "\n" + tabulations( kw_level ) + "{\n"
      for key, value in container.items( ):
         string += tabulations( kw_level + 1 ) + f"{to_string( key, **kwargs )} -> {to_string( value, **kwargs )}" + ",\n"
      string += tabulations( kw_level ) + "}"
   elif isinstance( container, list ):
      string += "\n" + tabulations( kw_level ) + "[\n"
      for item in container:
         string += tabulations( kw_level + 1 ) + f"{to_string( item, **kwargs )}" + ",\n"
      string += tabulations( kw_level ) + "]"
   elif isinstance( container, tuple ):
      string += "\n" + tabulations( kw_level ) + "(n"
      for item in container:
         string += tabulations( kw_level + 1 ) + f"{to_string( item, **kwargs )}" + ",\n"
      string += tabulations( kw_level ) + ")"
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

