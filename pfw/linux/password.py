import os
import time

import pfw.console
import pfw.shell



def build_hashed_password( password, salt ):
   command = f"perl -e " + "\"print crypt(\"" + password + "\",\"" + salt + "\");\""
   result = pfw.shell.execute( command, print = False )
   if 0 != result["code"]:
      return None

   pfw.console.debug.info( result["output"] )
   return result["output"]
# def build_hashed_password
