import os
import shutil
import errno
import stat
import time
import filetype
import enum

import pfw.console
import pfw.shell



# https://github.com/h2non/filetype.py
# https://github.com/ahupp/python-magic
# https://docs.python.org/3/library/imghdr.html
def universal_info( file ): # @TDA: to do
   if False == os.path.exists( file ):
      pfw.console.debug.error( "File does not exist: '%s'" % file )
      return

   kind = filetype.guess( file )
   if kind is None:
      pfw.console.debug.error( "Cannot guess file type: '%s'" % file )
   else:
      pfw.console.debug.warning( "'%s'" % ( file ) )
      pfw.console.debug.warning( "   extension: '%s'" % kind.extension )
      pfw.console.debug.warning( "   MIME type: '%s'" % kind.mime )
# def universal_info

def file_time( file ):
   try:
      st = os.stat( file )
   except IOError:
      return None
   else:
      return st[ stat.ST_MTIME ]
      # return time.asctime( time.localtime(st[stat.ST_MTIME]) )
# def file_time

def copy_recursively( _source_folder: str, _destination_folder: str ):
   pfw.console.debug.trace( "Copying directory content from '", _source_folder, "' to '", _destination_folder, "'" )
   for file_name in os.listdir( _source_folder ):
      source = os.path.join( _source_folder, file_name )
      destination = os.path.join( _destination_folder, file_name )

      try:
         shutil.copytree( source, destination )
      except OSError as err:
         # error caused if the source was not a directory
         if err.errno == errno.ENOTDIR:
            shutil.copy2( source, destination )
         else:
            pfw.console.debug.error( "%s" % err )
# def copy_recursively



# Example:
#     clean_dir( "/home/Source", [ ".git", "git.py", "base.py", "console.py", "__pycache__" ] )
def clean_dir( _dir: str, _exceptions: list = [ ] ):
   pfw.console.debug.trace( "Cleaning directory: ", _dir )
   for file_name in os.listdir( _dir ):
      skip: bool = False
      for exception_file in _exceptions:
         if file_name == exception_file:
            pfw.console.debug.warning( "skipping: ", file_name )
            skip = True
            continue
      if True == skip:
         continue

      file_path = os.path.join( _dir, file_name )
      try:
         if os.path.isfile( file_path ) or os.path.islink( file_path ):
            pfw.console.debug.trace( "deleting file: ", file_path )
            os.unlink( file_path )
         elif os.path.isdir( file_path ):
            pfw.console.debug.trace( "deleting directory: ", file_path )
            shutil.rmtree( file_path )
      except Exception as e:
         pfw.console.debug.error( 'Failed to delete %s. Reason: %s' % ( file_path, e ) )
# def clean_dir

def current_dir( ):
   return os.path.abspath( os.getcwd( ) )
# def current_dir

def current_script_dir( ):
   return os.path.dirname( os.path.abspath( __file__ ) )
# def current_script_dir

def change_dir( destination: str ):
   os.chdir( destination )
# def change_dir

def dir_size( path = '.' ):
   if not os.path.isdir( path ):
      return None

   total = 0
   with os.scandir( path ) as it:
      for entry in it:
         if entry.is_file( ):
            total += entry.stat( ).st_size
         elif entry.is_dir( ):
            total += dir_size( entry.path )
   return total
# def dir_size

def file_size( path: str ):
   if not os.path.isfile( path ):
      return None

   return os.stat( path ).st_size
   # return os.path.getsize( path )
# def file_size

def size( path = '.' ):
   if os.path.isfile( path ):
      return file_size( path )
   elif os.path.isdir( path ):
      return dir_size( path )
# def size
