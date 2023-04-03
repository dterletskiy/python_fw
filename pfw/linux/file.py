import os

import pfw.console
import pfw.shell



def size( path: str, sudo: bool = False ):
   result = pfw.shell.execute( f"du -hsb {path}", sudo = sudo, output = pfw.shell.eOutput.PTY )
   if 0 != result["code"]:
      return None

   return int( result["output"].split( )[ 0 ] )
# def size

def mktemp( **kwargs ):
   kw_location = kwargs.get( "location", None )
   kw_directory = kwargs.get( "directory", False )
   kw_template = kwargs.get( "template", None )

   command: str = "mktemp"
   command += f" --directory" if kw_directory else ""
   command += f" --tmpdir={kw_location}" if kw_location else ""
   command += f" {kw_template}" if kw_template else ""
   result = pfw.shell.execute( command, output = pfw.shell.eOutput.PTY )

   if 0 != result["code"]:
      pfw.console.debug.error( "Unable to create temporary file/directory" )
      return None

   file = result["output"].split( "\r\n" )[0]
   return file
# def mktemp

def copy_file( source: str, destination: str, **kwargs ):
   kw_sudo = kwargs.get( "sudo", False )
   kw_force = kwargs.get( "force", False )

   if not os.path.isfile( source ):
      pfw.console.debug.error( f"source '{source}' is not a file" )
      return False

   if kw_force:
      pfw.shell.execute( f"mkdir -p {os.path.dirname( destination )}", output = pfw.shell.eOutput.PTY, sudo = kw_sudo )

   command: str = "cp"
   command += f" {source}"
   command += f" {destination}"
   return 0 == pfw.shell.execute( command, output = pfw.shell.eOutput.PTY, sudo = kw_sudo )["code"]
# def copy_file

def copy_dir( source: str, destination: str, **kwargs ):
   kw_sudo = kwargs.get( "sudo", False )
   kw_force = kwargs.get( "force", False )

   if not os.path.isdir( source ):
      pfw.console.debug.error( f"source '{source}' is not a directory" )
      return False

   if kw_force:
      pfw.shell.execute( f"mkdir -p {os.path.dirname( destination )}", output = pfw.shell.eOutput.PTY, sudo = kw_sudo )

   command: str = "cp -R"
   command += f" {source}"
   command += f" {destination}"
   return 0 == pfw.shell.execute( command, output = pfw.shell.eOutput.PTY, sudo = kw_sudo )["code"]
# def copy_dir

def copy( source: str, destination: str, **kwargs ):
   if os.path.isfile( source ):
      return copy_file( source, destination, **kwargs )

   if os.path.isdir( source ):
      return copy_dir( source, destination, **kwargs )

   pfw.console.debug.error( f"trying to copy unknown file type: '{source}'" )
   return False
# def copy
