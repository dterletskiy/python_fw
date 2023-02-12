import os
import copy
import re
import random
import tempfile

import pfw.base
import pfw.console
import pfw.shell
import pfw.size
import pfw.linux.file





FILE_SYSTEMS: dict = {
   "ext" : {
      "ext2" : { "fstype": "ext2" },
      "ext3" : { "fstype": "ext3" },
      "ext4" : { "fstype": "ext4" }
   },
   "fat" : {
      "fat12" : { "fstype": "vfat -F 12" },
      "fat16" : { "fstype": "vfat -F 16" },
      "fat32" : { "fstype": "vfat -F 32" }
   },
}

def create( file: str, size: pfw.size.Size ):
   file = file if file else tempfile.mkstemp( suffix = ".img" )[1]

   size_count = size.count( )
   command = f"dd if=/dev/zero of={file} bs={str( int( size_count['gran'] ) )} count={str( size_count['count'] )}"
   if 0 != pfw.shell.execute( command )["code"]:
      return None

   return file
# def create

def format( file_name: str, file_system: str ):
   if None == file_system:
      pfw.console.debug.error( "filesystem is not defined" )
      return False

   if False == os.path.exists( file_name) :
      pfw.console.debug.error( "'%s' does not exist" % file_name )
      return False

   command: str = f"mkfs -V "

   result: bool = False
   for family in FILE_SYSTEMS:
      if file_system in FILE_SYSTEMS[ family ].keys( ):
         option = FILE_SYSTEMS[ family ][ file_system ][ "fstype" ]
         command = command + f" -t {option}"
         result = True

   if False == result:
      pfw.console.debug.error( "Undefined file system type: '%s'" % file_system )
      return False

   command = command + f" {file_name}"

   return 0 == pfw.shell.execute( command, sudo = True, output = pfw.shell.eOutput.PTY )["code"]
# def format

def mount( image_file: str, **kwargs ):
   kw_mount_point = kwargs.get( "mount_point", None )
   kw_fs = kwargs.get( "fs", None )

   kw_mount_point = kw_mount_point if kw_mount_point else tempfile.mkdtemp( prefix = "mp_" )

   if not os.path.exists( kw_mount_point ):
      result_code = pfw.shell.execute( f"mkdir -p {kw_mount_point}", sudo = True, output = pfw.shell.eOutput.PTY )["code"]
      if 0 != result_code:
         pfw.console.debug.error( "create directory '%s' error: %d" % ( kw_mount_point, result_code ) )
         return None

   command: str = f"mount"
   command += f" -t {kw_fs}" if kw_fs else ""
   command += f" {image_file} {kw_mount_point}"
   command += f" -o loop"
   result_code = pfw.shell.execute( command, sudo = True, output = pfw.shell.eOutput.PTY )["code"]
   if 0 != result_code:
      pfw.console.debug.error( "mount image file '%s' to directory '%s' error: '%s'" % ( image_file, kw_mount_point, result_code ) )
      return None

   return kw_mount_point
# def mount

def umount( file: str ):
   if None == file:
      pfw.console.debug.warning( "Mountpoint (or image file) is not defined" )
      return False

   result_code = pfw.shell.execute( f"umount {file}", sudo = True, output = pfw.shell.eOutput.PTY )["code"]
   if 0 != result_code:
      pfw.console.debug.error( "umount file '%s' error: '%s'" % ( file, result_code ) )
      return False

   return True
# def umount

def mounted_to( file: str ):
   # @TDA: To implement lates in general implementation.
   # Fake command to execute it with 'root' to avoid password promt string in next command what will go to result
   pfw.shell.execute( f"pwd", sudo = True, output = pfw.shell.eOutput.PTY, print = False, collect = False )

   result = pfw.shell.execute( f"mount | grep {file}", sudo = True, output = pfw.shell.eOutput.PTY )

   if 0 != result["code"]:
      return None

   match = re.match( rf"^{file} on (.+) type (.+)$", result["output"] )
   if match:
      mount_point = match.group( 1 )
      pfw.console.debug.info( f"image '{file}' mounted to '{mount_point}'" )
      return mount_point

   return None
# def mounted_to

def attach( file: str ):
   result = pfw.shell.execute( f"losetup --find --show --partscan {file}", sudo = True, output = pfw.shell.eOutput.PTY )
   if 0 != result["code"]:
      pfw.console.debug.error( "attach file '%s' error: '%s'" % ( file, result["code"] ) )
      return None

   attached_to = result["output"].split( "\r\n" )[0]
   pfw.console.debug.info( "file '%s' attached to '%s'" % ( file, attached_to ) )
   return attached_to
# def attach

def detach( device: str ):
   result_code = pfw.shell.execute( f"losetup --detach {device}", sudo = True, output = pfw.shell.eOutput.PTY )["code"]
   if 0 != result_code:
      pfw.console.debug.error( "detach device '%s' error: '%s'" % ( device, result_code ) )
      return False

   pfw.console.debug.info( "device '%s' detached" % ( device ) )
   return True
# def detach

def attached_to( file: str ):
   # @TDA: To implement lates in general implementation.
   # Fake command to execute it with 'root' to avoid password promt string in next command what will go to result
   pfw.shell.execute( f"pwd", sudo = True, output = pfw.shell.eOutput.PTY, print = False, collect = False )

   result = pfw.shell.execute( f"losetup --list | grep {file}", sudo = True, output = pfw.shell.eOutput.PTY )

   if 0 != result["code"]:
      return None

   match = re.match( rf"^(\S+)\s+\d+\s+\d+\s+\d+\s+\d+\s+{file}\s+.+$", result["output"] )
   if match:
      attach_point = match.group( 1 )
      pfw.console.debug.info( f"image '{file}' attached to '{attach_point}'" )
      return attach_point

   return None
# def mounted_to

def info( image_file: str ):
   # @TDA: To implement lates in general implementation.
   # Fake command to execute it with 'root' to avoid password promt string in next command what will go to result
   pfw.shell.execute( f"pwd", sudo = True, output = pfw.shell.eOutput.PTY, print = False, collect = False )

   result = pfw.shell.execute( f"parted {image_file} UNIT b print", sudo = True, output = pfw.shell.eOutput.PTY )

   # https://unix.stackexchange.com/a/438308
   result = pfw.shell.execute( f"parted -m {image_file} print", sudo = True, output = pfw.shell.eOutput.PTY )

   if 0 != result["code"]:
      pfw.console.debug.error( f"parted '{image_file}' information error" )
      return None

   pattern: dict = {
      "error": r"^Error:\s+(.*)$",
      "size": r"^(\d+)\.?(\d*)(.+)$"
   }

   parted_output = result["output"].split( "\r\n" )

   # Check about error result command execution
   match = re.match( pattern["error"], parted_output[0] )
   if match:
      pfw.console.debug.error( f"image file '{image_file}' information error: {match.group( 1 )}" )
      return None

   def text_to_size( text: str ):
      text_to_gran = {
         "B": pfw.size.Size.eGran.B,
         "kB": pfw.size.Size.eGran.K,
         "MB": pfw.size.Size.eGran.M,
         "GB": pfw.size.Size.eGran.G,
      }

      match = re.match( pattern["size"], text )
      if match:
         return pfw.size.Size( float( f"{match.group(1)}.{match.group(2)}" ), text_to_gran[ match.group(3) ] )

      return None
   # def text_to_size

   parted_partitions = parted_output
   parted_partitions = parted_partitions[2:]
   partitions: list = [ ]
   for parted_partition in parted_partitions:
      parted_partition_items = parted_partition.split(":")
      partitions.append(
         Partition.Description(
            start = text_to_size( parted_partition_items[1] ),
            end = text_to_size( parted_partition_items[2] ),
            size = text_to_size( parted_partition_items[3] ),
            fs = parted_partition_items[4],
            label = parted_partition_items[5]
         )
      )

   image = None

   # Parse image info about type and common size
   parted_image = parted_output[1].split(":")
   if( "loop" == parted_image[5] ):
      if( 1 != len( partitions ) ):
         pfw.console.debug.error( f"Image type defined as 'partition' but it contains {len( partitions )} aprtitions inside" )
      image = Partition( )
   elif( "msdos" == parted_image[5] or "gpt" == parted_image[5] ):
      # return Drive( ) # @TDA: should be implemented
      image = Drive( )
   else:
      pfw.console.debug.error( f"Undefined image type {image_file}" )

   pfw.console.debug.ok( "-------------------------------------------------------------------" )
   for partition in partitions:
      partition.info( )
   pfw.console.debug.ok( "-------------------------------------------------------------------" )

   return [ partitions, image ]
# def info
