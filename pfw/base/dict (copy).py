


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

