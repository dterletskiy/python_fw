import pfw.console



ignore_field = "__"



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
# def class_attributes
