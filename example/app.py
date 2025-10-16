#!/usr/bin/python



import os
import sys

pfw_path = None
for arg in sys.argv[1:]:
   if arg.startswith( "--pfw=" ):
      pfw_path = arg.split("=", 1)[1]
      sys.argv.remove( arg )
      break

if not pfw_path:
   print( "ERROR: Define path to 'pfw' as '--pfw=<path>'" )
   exit(1)

if not os.path.exists( pfw_path ):
   print( f"ERROR: {pfw_path} does not exist" )
   exit(1)

print( f"INFO: Path to 'pfw': {pfw_path}" )

sys.path.insert( 0, pfw_path )
try:
   import pfw.console
   print( f"INFO: 'pfw' import success" )
except ImportError:
   print( f"ERROR: 'pfw' import failed" )



import pfw.base.configuration

pfw.configuration.init( verbose = False )

def main( ):
   app.main.main( )

if __name__ == "__main__":
   main( )
