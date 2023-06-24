import shutil
import datetime

import pfw.console





def archive( dir_name: str, format: str = "zip" ):
   output_filename: str = dir_name + "_" + datetime.datetime.now( ).strftime( "%Y-%m-%d_%H-%M-%S" )
   pfw.console.debug.info( "date and time =", output_filename )
   if "all" == format:
      shutil.make_archive( output_filename, "zip", dir_name )
      shutil.make_archive( output_filename, "tar", dir_name )
      shutil.make_archive( output_filename, "gztar", dir_name )
      shutil.make_archive( output_filename, "bztar", dir_name )
      shutil.make_archive( output_filename, "xztar", dir_name )
   else:
      shutil.make_archive( output_filename, format, dir_name )
   return True
# def archive

def extract( archive: str, format: str, to: str ):
   pfw.console.debug.info( "extracting '", archive, "' to '", to, "'" )
   shutil.unpack_archive( archive, to, format )
   return True
# def extract
