class _const:
   class ConstError( TypeError ): pass
   def __setattr__(self,name,value):
      if name in self.__dict__:
         raise self.ConstError( "Can't rebind const: '%s'"%name )
      self.__dict__[ name ]=value

import sys
sys.modules[ __name__ ]=_const( )



# Example
# import const
# # and bind an attribute ONCE:
# const.magic = 23
# # but NOT re-bind it:
# const.magic = 88      # raises const.ConstError
# # you may also want to add the obvious __delattr__
