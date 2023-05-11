import os
import copy
import re
import random
import tempfile

import pfw.base.struct
import pfw.console
import pfw.shell
import pfw.size
import pfw.file
import pfw.linux.file
import pfw.linux.fs



ALIGN_SIZE: pfw.size.Size.eGran = pfw.size.Size.eGran.M



class Partition:
   class FormatError( TypeError ): pass
   class MountError( TypeError ): pass
   class ParameterError( TypeError ): pass

   def __init__( self, **kwargs ):
      kw_size = kwargs.get( "size", None )
      kw_start = kwargs.get( "start", None )
      kw_end = kwargs.get( "end", None )
      kw_fs = kwargs.get( "fs", None )
      kw_label = kwargs.get( "label", None )
      kw_bootable = kwargs.get( "bootable", False )
      kw_clone_from = kwargs.get( "clone_from", None )

      kw_clone_from_size = None
      if kw_clone_from:
         if os.path.exists( kw_clone_from ):
            kw_clone_from_size = pfw.size.Size( pfw.file.file_size( kw_clone_from ), pfw.size.Size.eGran.B, align = ALIGN_SIZE )
         else:
            pfw.console.debug.warning( f"'clone_from' file does not exist: '{kw_clone_from}'" )

      kw_start_end_size = None
      if kw_start and kw_end:
         kw_start_end_size = kw_end - kw_start + pfw.size.SizeMegabyte

      partition_size = None
      if kw_start_end_size and kw_clone_from_size:
         if kw_start_end_size < kw_clone_from_size:
            pfw.console.debug.error( "size mismatch between clone size file and end-start positions" )
         partition_size = pfw.size.max( kw_start_end_size, kw_clone_from_size )
      elif kw_start_end_size:
         partition_size = kw_start_end_size
      elif kw_clone_from_size:
         partition_size = kw_clone_from_size
      elif kw_size:
         partition_size = kw_size
      else:
         raise ParameterError

      self.__size = partition_size
      self.__start = kw_start
      self.__end = kw_end
      self.__bootable = kw_bootable
      self.__clone_from = kw_clone_from
      if not kw_clone_from:
         self.__fs = kw_fs
         self.__label = kw_label
   # def __init__

   def __del__( self ):
      pass
   # def __del__

   def __setattr__( self, attr, value ):
      attr_list = [ i for i in self.__class__.__dict__.keys( ) ]
      if attr in attr_list:
         self.__dict__[ attr ] = value
         return
      raise AttributeError
   # def __setattr__

   def __str__( self ):
      attr_list = [ i for i in self.__class__.__dict__.keys( ) if i[:2] != pfw.base.struct.ignore_field ]
      vector = [ f"{str( attr )} = {str( self.__dict__.get( attr ) )}" for attr in attr_list ]
      return self.__class__.__name__ + " { " + ", ".join( vector ) + " }"
   # def __str__

   def info( self, **kwargs ):
      kw_tabulations = kwargs.get( "tabulations", 0 )
      kw_message = kwargs.get( "message", "" )
      pfw.console.debug.info( f"{kw_message} (type {self.__class__.__name__}):", tabs = ( kw_tabulations + 0 ) )

      if self.__size:   self.__size.info( message = "size", tabulations = kw_tabulations + 1 )
      else:             pfw.console.debug.info( "size: None", tabs = ( kw_tabulations + 1 ) )

      if self.__start:  self.__start.info( message = "start", tabulations = kw_tabulations + 1 )
      else:             pfw.console.debug.info( "start: None", tabs = ( kw_tabulations + 1 ) )

      if self.__end:    self.__end.info( message = "end", tabulations = kw_tabulations + 1 )
      else:             pfw.console.debug.info( "end: None", tabs = ( kw_tabulations + 1 ) )

      if self.__fs:     self.__fs.info( message = "filesystem", tabulations = kw_tabulations + 1 )
      else:             pfw.console.debug.info( "filesystem: None", tabs = ( kw_tabulations + 1 ) )

      pfw.console.debug.info( f"label: '{self.__label}'", tabs = ( kw_tabulations + 1 ) )
   # def info



   def size( self ):
      return self.__size
   # def size

   def start( self ):
      return self.__start
   # def start

   def end( self ):
      return self.__end
   # def end

   def fs( self ):
      return self.__fs
   # def fs

   def label( self ):
      return self.__label
   # def label

   def bootable( self ):
      return self.__bootable
   # def bootable

   def reset_bootable( self ):
      self.__bootable = False
   # def bootable

   def clone_from( self ):
      return self.__clone_from
   # def clone_from



   __size: pfw.size.Size = None
   __start: pfw.size.Size = None
   __end: pfw.size.Size = None
   __fs: pfw.linux.fs.FileSystem = None
   __label: str = None
   __bootable: bool = False
   __clone_from: str = None
# class Partition



class Device:
   class FormatError( TypeError ): pass
   class MountError( TypeError ): pass

   def __init__( self, **kwargs ):
      kw_partitions = kwargs.get( "partitions", [ ] )

      self.__partitions = [ ]
      bootable_index: int = None
      ( start, end ) = ( pfw.size.SizeZero, self.__reserved_start_size - pfw.size.SizeSector )
      for index, partition in enumerate( kw_partitions ):
         if partition.start( ) and partition.end( ):
            start = partition.start( )
            end = partition.end( )
         else:
            start = end + pfw.size.SizeSector
            end = end + partition.size( )

         if partition.bootable( ):
            if bootable_index:
               pfw.console.debug.warning(
                     f"partition '{index}' marked as bootable but bootable partition already exists with number '{bootable_index}'"
                  )
               partition.reset_bootable( )
            else:
               bootable_index = index

         self.__partitions.append(
            Partition(
               start = start,
               end = end,
               size = partition.size( ),
               fs = partition.fs( ),
               label = partition.label( ),
               bootable = partition.bootable( ),
               clone_from = partition.clone_from( )
            )
         )
   # def __init__

   def __del__( self ):
      pass
   # def __del__

   def __setattr__( self, attr, value ):
      attr_list = [ i for i in self.__class__.__dict__.keys( ) ]
      if attr in attr_list:
         self.__dict__[ attr ] = value
         return
      raise AttributeError
   # def __setattr__

   def __str__( self ):
      attr_list = [ i for i in self.__class__.__dict__.keys( ) if i[:2] != pfw.base.struct.ignore_field ]
      vector = [ f"{str( attr )} = {str( self.__dict__.get( attr ) )}" for attr in attr_list ]
      return self.__class__.__name__ + " { " + ", ".join( vector ) + " }"
   # def __str__

   def info( self, **kwargs ):
      kw_tabulations = kwargs.get( "tabulations", 0 )
      kw_message = kwargs.get( "message", "" )
      pfw.console.debug.info( f"{kw_message} (type {self.__class__.__name__}):", tabs = ( kw_tabulations + 0 ) )

      for index, partition in enumerate( self.__partitions ):
         partition.info( message = f"partition {index}", tabulations = kw_tabulations + 1 )
   # def info



   def partitions( self ):
      return self.__partitions
   # def partitions

   def size( self ):
      size = self.__reserved_start_size + self.__reserved_end_size
      for partition in self.__partitions:
         size += partition.size( )

      return size
   # def size



   __partitions: list = None
   __reserved_start_size = pfw.size.SizeMegabyte # first 2048 reserved sectors
   __reserved_end_size = pfw.size.SizeMegabyte # last 2048 reserved sectors
# class Device



def create( file: str, size: pfw.size.Size, **kwargs ):
   kw_force = kwargs.get( "force", False )

   if file and os.path.exists( file ) and False == kw_force:
      pfw.console.debug.warning( f"file '{file}' already exists and 'force' flag set to 'false' => existing file will be used" )
      return file

   file = file if file else tempfile.mkstemp( suffix = ".img" )[1]

   size_count = size.count( )
   command = f"dd if=/dev/zero of={file} bs={str( int( size_count['gran'] ) )} count={str( size_count['count'] )}"
   if 0 != pfw.shell.execute( command )["code"]:
      return None

   return file
# def create

def format( file_name: str, file_system: pfw.linux.fs.FileSystem, **kwargs ):
   kw_label = kwargs.get( "label", None )

   if None == file_system:
      pfw.console.debug.error( "filesystem is not defined" )
      return False

   if False == os.path.exists( file_name) :
      pfw.console.debug.error( "'%s' does not exist" % file_name )
      return False

   return file_system.format( file_name, label = kw_label )
# def format

def mount( image_file: str, **kwargs ):
   kw_mount_point = kwargs.get( "mount_point", tempfile.mkdtemp( prefix = "mp_" ) )
   kw_fs = kwargs.get( "fs", None )

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

def umount( file: str, **kwargs ):
   if None == file:
      pfw.console.debug.warning( "Mountpoint (or image file) is not defined" )
      return False

   result_code = pfw.shell.execute( f"umount {file}", sudo = True, output = pfw.shell.eOutput.PTY )["code"]
   if 0 != result_code:
      pfw.console.debug.error( "umount file '%s' error: '%s'" % ( file, result_code ) )
      return False

   return True
# def umount

def mounted_to( file: str, **kwargs ):
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

def attach( file: str, **kwargs ):
   result = pfw.shell.execute( f"losetup --find --show --partscan {file}", sudo = True, output = pfw.shell.eOutput.PTY )
   if 0 != result["code"]:
      pfw.console.debug.error( "attach file '%s' error: '%s'" % ( file, result["code"] ) )
      return None

   loop_device = result["output"].split( "\r\n" )[0]
   pfw.console.debug.info( "file '%s' attached to '%s'" % ( file, loop_device ) )
   return loop_device
# def attach

def detach( loop_device: str, **kwargs ):
   result_code = pfw.shell.execute( f"losetup --detach {loop_device}", sudo = True, output = pfw.shell.eOutput.PTY )["code"]
   if 0 != result_code:
      pfw.console.debug.error( "detach device '%s' error: '%s'" % ( loop_device, result_code ) )
      return False

   pfw.console.debug.info( "device '%s' detached" % ( loop_device ) )
   return True
# def detach

def attached_to( file: str, **kwargs ):
   result = pfw.shell.execute( f"losetup --list | grep {file}", sudo = True, output = pfw.shell.eOutput.PTY )

   if 0 != result["code"]:
      return None

   match = re.match( rf"^(\S+)\s+\d+\s+\d+\s+\d+\s+\d+\s+{file}\s+.+$", result["output"] )
   if match:
      loop_device = match.group( 1 )
      pfw.console.debug.info( f"image '{file}' attached to '{loop_device}'" )
      return loop_device

   return None
# def mounted_to

def map( file: str, **kwargs ):
   kw_mount_point = kwargs.get( "mount_point", tempfile.mkdtemp( prefix = "loop_" ) )
   kw_processor = kwargs.get( "processor", None )

   description = info( file )
   if isinstance( description, Device ):
      pfw.console.debug.info( f"image has {len( description.partitions( ) )} partitions" )

      loop_device = attach( file )
      for index in range( 1, 1 + len( description.partitions( ) ) ):
         mp = mount( f"{loop_device}p{index}", mount_point = f"{kw_mount_point}/{index}" )
         pfw.console.debug.info( f"{loop_device}p{index} -> {mp}" )

      if kw_processor:
         kw_processor( mount_point = kw_mount_point )

      for index in range( 1, 1 + len( description.partitions( ) ) ):
         # umount( f"{loop_device}p{index}" )
         umount( f"{kw_mount_point}/{index}" )
      detach( loop_device )

   elif isinstance( description, Partition ):
      pfw.console.debug.info( f"image has 1 partition" )

      mount( file, mount_point = kw_mount_point )

      if kw_processor:
         kw_processor( mount_point = kw_mount_point )

      umount( kw_mount_point )
   else:
      pfw.console.debug.error( "not an image file" )
# def map

def info( image_file: str, **kwargs ):
   result = pfw.shell.execute( f"parted {image_file} unit b print", sudo = True, output = pfw.shell.eOutput.PTY )

   # https://unix.stackexchange.com/a/438308
   result = pfw.shell.execute( f"parted -m {image_file} unit b print", sudo = True, output = pfw.shell.eOutput.PTY )

   if 0 != result["code"]:
      pfw.console.debug.error( f"parted '{image_file}' information error" )
      return None

   parted_output = result["output"].split( "\r\n" )

   pattern: dict = {
      "error": r"^Error:\s+(.*)$",
      "warning": r"^WARNING:\s+(.*)$",
      "size": r"^(\d+)\.?(\d*)(.+)$"
   }

   # Check about warning result command execution
   match = re.match( pattern["warning"], parted_output[0] )
   if match:
      pfw.console.debug.warning( f"image file '{image_file}' information warning: {match.group( 1 )}" )
      parted_output = parted_output[1:]

   # Check about error result command execution
   match = re.match( pattern["error"], parted_output[0] )
   if match:
      pfw.console.debug.error( f"image file '{image_file}' information error: {match.group( 1 )}" )
      return None


   def text_to_size( text: str ):
      text_to_gran = {
         "B": pfw.size.Size.eGran.B,
         "KiB": pfw.size.Size.eGran.K,
         "MiB": pfw.size.Size.eGran.M,
         "GiB": pfw.size.Size.eGran.G,
         "TiB": pfw.size.Size.eGran.T,
      }

      match = re.match( pattern["size"], text )
      if match:
         return pfw.size.Size( float( f"{match.group(1)}.{match.group(2)}" ), text_to_gran[ match.group(3) ] )

      return None
   # def text_to_size

   parted_partitions = parted_output[2:]
   partitions: list = [ ]
   for parted_partition in parted_partitions:
      if 0 == len( parted_partition ):
         continue

      parted_partition_items = parted_partition.split(":")
      partitions.append(
         Partition(
            start = text_to_size( parted_partition_items[1] ),
            end = text_to_size( parted_partition_items[2] ),
            size = text_to_size( parted_partition_items[3] ),
            fs = pfw.linux.fs.builder( parted_partition_items[4] ),
            label = parted_partition_items[5]
         )
      )

   image = None

   # Parse image info about type and common size
   parted_image = parted_output[1].split(":")
   if( "loop" == parted_image[5] ):
      if( 1 != len( partitions ) ):
         pfw.console.debug.error( f"Image type defined as 'partition' but it contains {len( partitions )} aprtitions inside" )
      image = partitions[0]
   elif( "msdos" == parted_image[5] or "gpt" == parted_image[5] ):
      image = Device( partitions = partitions )
   else:
      pfw.console.debug.error( f"Undefined image type {image_file}" )

   return image
# def info

def init_device( file: str, device: Device, **kwargs ):
   file_size = pfw.file.file_size( file )
   if None == file_size:
      return False
   file_size = pfw.size.Size( pfw.file.file_size( file ), pfw.size.Size.eGran.B )

   if device.size( ) > file_size:
      pfw.console.debug.error( "oversize" )
      return False

   loop_device = attached_to( file )
   must_be_detached: bool = False
   if None == loop_device:
      loop_device = attach( file )
      must_be_detached = True
      if None == loop_device:
         return False

   def mkpart( loop_device: str, partition: Partition ):
      label: str = partition.label( ) if partition.label( ) else "none"
      fs: str = partition.fs( ).name( ) if partition.fs( ) else ""
      start: int = partition.start( ).sectors( result = 'quotient' )
      end: int = partition.end( ).sectors( result = 'quotient' )

      pfw.shell.execute( f"parted {loop_device} -s mkpart {label} {fs} {start}s {end}s", sudo = True )
   # def mkpart

   pfw.shell.execute( f"parted {loop_device} -s mklabel gpt", sudo = True )
   for index, partition in enumerate( device.partitions( ) ):
      mkpart( loop_device, partition )

      if partition.bootable( ):
         pfw.shell.execute( f"parted {loop_device} set {index + 1} boot on", sudo = True )

      # pfw.shell.execute( f"parted {loop_device} print {index + 1}", sudo = True )
      pfw.shell.execute( f"parted {loop_device} -s print unit s", sudo = True )
      # pfw.shell.execute( f"partprobe {loop_device}", sudo = True )

      if partition.clone_from( ):
         pfw.shell.execute( f"dd if={partition.clone_from( )} of={loop_device}p{index + 1} bs=1M status=none", sudo = True )
      elif partition.fs( ):
         format( f"{loop_device}p{index + 1}", partition.fs( ), label = partition.label( ) )

   if must_be_detached:
      detach( loop_device )

   return True
# def init_device





# Examples:

# image_file = "/mnt/img/tmp/tmp.img"

# pfw.linux.image.create( image_file, pfw.size.SizeGigabyte )
# attached_to = pfw.linux.image.attach( image_file )
# attached_to_test = pfw.linux.image.attached_to( image_file )
# if attached_to != attached_to_test:
#    pfw.console.debug.error( f"{attached_to} != {attached_to_test}" )
# attached_to = pfw.linux.image.detach( attached_to )

# image = pfw.linux.image.info( image_file )
# image.info( )
# pfw.linux.image.init_device( "/mnt/img/tmp/main.img", image )
