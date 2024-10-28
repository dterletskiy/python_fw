import os

import pfw.console
import pfw.shell



def file_info( file: str ):
   result = pfw.shell.execute( f"file {file}", sudo = sudo, output = pfw.shell.eOutput.PTY )
   if 0 != result["code"]:
      return None
# def file_info

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
   command += f" -t {kw_template}" if kw_template else ""
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
   kw_verbose = kwargs.get( "verbose", False )
   kw_dereference = kwargs.get( "dereference", False )
   kw_no_dereference = kwargs.get( "no_dereference", False )

   if not os.path.isfile( source ):
      pfw.console.debug.error( f"source '{source}' is not a file" )
      return False

   if kw_force:
      pfw.shell.execute( f"mkdir -p {os.path.dirname( destination )}", output = pfw.shell.eOutput.PTY, sudo = kw_sudo )

   command: str = "cp"
   command += " -v" if kw_verbose else ""
   command += " -L" if kw_dereference else ""
   command += " -P" if kw_no_dereference else ""
   command += f" {source}"
   command += f" {destination}"
   return 0 == pfw.shell.execute( command, output = pfw.shell.eOutput.PTY, sudo = kw_sudo )["code"]
# def copy_file

def copy_dir( source: str, destination: str, **kwargs ):
   kw_sudo = kwargs.get( "sudo", False )
   kw_force = kwargs.get( "force", False )
   kw_verbose = kwargs.get( "verbose", False )
   kw_dereference = kwargs.get( "dereference", False )
   kw_no_dereference = kwargs.get( "no_dereference", False )

   if not os.path.isdir( source ):
      pfw.console.debug.error( f"source '{source}' is not a directory" )
      return False

   if kw_force:
      pfw.shell.execute( f"mkdir -p {os.path.dirname( destination )}", output = pfw.shell.eOutput.PTY, sudo = kw_sudo )

   command: str = "cp -r"
   command += " -v" if kw_verbose else ""
   command += " -L" if kw_dereference else ""
   command += " -P" if kw_no_dereference else ""
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

def remove_file( source: str, **kwargs ):
   kw_sudo = kwargs.get( "sudo", False )
   kw_force = kwargs.get( "force", False )
   kw_verbose = kwargs.get( "verbose", False )

   if not os.path.isfile( source ):
      pfw.console.debug.error( f"source '{source}' is not a file" )
      return False

   command: str = "rm"
   command += " -f" if kw_force else ""
   command += " -v" if kw_verbose else ""
   command += f" {source}"
   return 0 == pfw.shell.execute( command, output = pfw.shell.eOutput.PTY, sudo = kw_sudo )["code"]
# def remove_file

def remove_dir( source: str, **kwargs ):
   kw_sudo = kwargs.get( "sudo", False )
   kw_force = kwargs.get( "force", False )
   kw_verbose = kwargs.get( "verbose", False )

   if not os.path.isdir( source ):
      pfw.console.debug.error( f"source '{source}' is not a directory" )
      return False

   command: str = "rm -r"
   command += " -f" if kw_force else ""
   command += " -v" if kw_verbose else ""
   command += f" {source}"
   return 0 == pfw.shell.execute( command, output = pfw.shell.eOutput.PTY, sudo = kw_sudo )["code"]
# def remove_dir

def remove( source: str, **kwargs ):
   if os.path.isfile( source ):
      return remove_file( source, **kwargs )

   if os.path.isdir( source ):
      return remove_dir( source, **kwargs )

   pfw.console.debug.error( f"trying to remove unknown file type: '{source}'" )
   return False
# def remove
