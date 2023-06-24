import os
import re
from enum import Enum

import pfw.console
import pfw.shell



def pack( archive: str, format: str, *argv, **kwargs ):
   if format in tar_format_list:
      return pack_tar( archive, format, *argv, **kwargs )
   elif format in zip_format_list:
      return pack_zip( archive, *argv, **kwargs )
# def pack

def unpack( archive: str, to: str, format: str, *argv, **kwargs ):
   if format in tar_format_list:
      return unpack_tar( archive, to, format, *argv, **kwargs )
   elif format in zip_format_list:
      return unpack_zip( archive, to, *argv, **kwargs )
# def unpack

def detect_type( archive: str, **kwargs ):
   kw_sudo = kwargs.get( "sudo", False )

   result = pfw.shell.execute( f"file {archive}", output = pfw.shell.eOutput.PTY, sudo = kw_sudo )

   match = re.match( rf"^{archive}: (.+?) compressed data", result["output"] )
   if not match:
      return None

   pfw.console.debug.info( f"{match.group(1)}" )
# def detect_type



tar_format_list: list = [ "tar.gz", "tar.bz2", "tar.xz" ]

def format_to_tar_param( format: str ):
   if not isinstance( format, str ):
      return None

   if    "tar.gz" == format:     return "z"
   elif  "tar.bz2" == format:    return "j"
   elif  "tar.xz" == format:     return "J"

   pfw.console.debug.error( f"unsupported archive format for tar: {format}" )
   return None
# def format_to_tar_param

# Examples:
# pfw.linux.archive.pack( "/mnt/archive.tar.gz", "tar.gz", "/mnt/data/" )
# pfw.linux.archive.pack( "/mnt/archive.tar.gz", "tar.gz", "./data/", "./packed/", directory = "/mnt/" )
def pack_tar( archive: str, format: str, *argv, **kwargs ):
   kw_sudo = kwargs.get( "sudo", False )
   kw_ext = kwargs.get( "ext", False )
   kw_directory = kwargs.get( "directory", None )

   _archive = f"{archive}.{str( format )}" if kw_ext else f"{archive}"
   _format = format_to_tar_param( format )

   command = "tar -cv"
   command += f" -{_format}"
   command += f" -f {_archive}"
   command += f" -C {kw_directory}" if kw_directory else ""
   command += " " + " ".join( list( argv ) )

   return pfw.shell.execute( command, output = pfw.shell.eOutput.PTY, sudo = kw_sudo )["code"]
# def pack_tar

def unpack_tar( archive: str, to: str, format: str, **kwargs ):
   kw_sudo = kwargs.get( "sudo", False )

   _format = format_to_tar_param( format )

   command = "tar -xv"
   command += f" -{_format}"
   command += f" -f {archive}"
   command += f" -C {to}"

   return pfw.shell.execute( command, output = pfw.shell.eOutput.PTY, sudo = kw_sudo )["code"]
# def unpack_tar



zip_format_list: list = [ "zip" ]

def pack_zip( archive: str, *argv, **kwargs ):
   kw_sudo = kwargs.get( "sudo", False )
   kw_directory = kwargs.get( "directory", None )

   command = "zip -r"
   command += f" {archive}"
   command += " " + " ".join( list( argv ) )

   return pfw.shell.execute( command, output = pfw.shell.eOutput.PTY, sudo = kw_sudo, cwd = kw_directory )["code"]
# def pack_zip

def unpack_zip( archive: str, to: str, **kwargs ):
   kw_sudo = kwargs.get( "sudo", False )
   kw_directory = kwargs.get( "directory", None )

   command = "unzip"
   command += f" {archive}"
   command += f" -d {to}"

   return pfw.shell.execute( command, output = pfw.shell.eOutput.PTY, sudo = kw_sudo, cwd = kw_directory )["code"]
# def unpack_zip
