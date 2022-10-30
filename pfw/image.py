import os
import copy
import re
import random

import pfw.base
import pfw.console
import pfw.shell
import pfw.size





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
( "ext2", "ext3", "ext4", "fat12", "fat16", "fat32" )

def create( file: str, size: pfw.size.Size ):
   size_count = size.count( )
   command = f"dd if=/dev/zero of={file} bs={str( int( size_count['gran'] ) )} count={str( size_count['count'] )}"
   return 0 == pfw.shell.run_and_wait_with_status( command )["code"]
# def create

def format( file_name: str, file_system: str ):
   if None == file_system:
      pfw.console.debug.error( "filesystem is not defined" )
      return False

   if False == os.path.exists( file_name) :
      pfw.console.debug.error( "'%s' does not exist" % file_name )
      return False

   command: str = f"sudo -S mkfs -V "

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

   return 0 == pfw.shell.run_and_wait_with_status( command, output = pfw.shell.eOutput.PTY )["code"]
# def format

def mount( file: str, mount_point: str, fs: str = None ):
   if None == mount_point:
      pfw.console.debug.warning( "Mountpoint is not defined" )
      return False

   result_code = pfw.shell.run_and_wait_with_status( f"sudo -S mkdir -p {mount_point}", output = pfw.shell.eOutput.PTY )["code"]
   if 0 != result_code:
      pfw.console.debug.error( "create directory '%s' error: %d" % ( mount_point, result_code ) )
      return False

   command: str = f"sudo -S mount"
   if None != fs:
      command += f" -t {fs}"
   command += f" {file} {mount_point}"
   command += f" -o loop"

   result_code = pfw.shell.run_and_wait_with_status( command, output = pfw.shell.eOutput.PTY )["code"]
   if 0 != result_code:
      pfw.console.debug.error( "mount file '%s' to directory '%s' error: '%s'" % ( file, mount_point, result_code ) )
      return False

   return True
# def mount

def umount( file: str ):
   if None == file:
      pfw.console.debug.warning( "Mountpoint (or image file) is not defined" )
      return False

   command: str = f"sudo -S umount {file}"

   result_code = pfw.shell.run_and_wait_with_status( command, output = pfw.shell.eOutput.PTY )["code"]
   if 0 != result_code:
      pfw.console.debug.error( "umount file '%s' error: '%s'" % ( file, result_code ) )
      return False

   return True
# def umount

def gen_mount_point( dir_name: str, prefix: str = "mp" ):
   mount_point = None
   while None == mount_point or True == os.path.exists( mount_point ):
      number: int = random.randint( 0, 99999 )
      mount_point = os.path.join( dir_name, prefix + f"{prefix}{number:05d}" )

   return mount_point
# def gen_mount_point

def attach( file: str ):
   command: str = f"sudo -S losetup --find --show --partscan {file}"

   result = pfw.shell.run_and_wait_with_status( command, output = pfw.shell.eOutput.PTY )
   if 0 != result["code"]:
      pfw.console.debug.error( "attach file '%s' error: '%s'" % ( file, result["code"] ) )
      return None

   pfw.console.debug.info( "file '%s' attached to '%s'" % ( file, result["output"] ) )
   return result["output"]
# def attach

def detach( device: str ):
   command: str = f"sudo -S losetup --detach {device}"

   result_code = pfw.shell.run_and_wait_with_status( command, output = pfw.shell.eOutput.PTY )["code"]
   if 0 != result_code:
      pfw.console.debug.error( "detach device '%s' error: '%s'" % ( device, result_code ) )
      return False

   pfw.console.debug.info( "device '%s' detached" % ( device ) )
   return True
# def detach

def info( image_file: str ):
   command = f"sudo -S parted {image_file} UNIT b print"
   result = pfw.shell.run_and_wait_with_status( command, output = pfw.shell.eOutput.PTY )

   # https://unix.stackexchange.com/a/438308
   command = f"sudo -S parted -m {image_file} print"
   result = pfw.shell.run_and_wait_with_status( command, output = pfw.shell.eOutput.PTY )

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

   # Parse image info about type and common size
   parted_image = parted_output[1].split(":")
   if( "loop" == parted_image[5] ):
      if( 1 != len( partitions ) ):
         pfw.console.debug.error( f"Image type defined as 'partition' but it contains {len( partitions )} inside" )
         return None
      # return Partition( ) # @TDA: should be implemented
      return None
   elif( "msdos" == parted_image[5] or "gpt" == parted_image[5] ):
      # return Drive( ) # @TDA: should be implemented
      return None
   else:
      pfw.console.debug.error( f"Undefined image type {image_file}" )
      return None

   pfw.console.debug.ok( "-------------------------------------------------------------------" )
   for partition in partitions:
      partition.info( )
   pfw.console.debug.ok( "-------------------------------------------------------------------" )


# def info



ALIGN_SIZE: pfw.size.Size.eGran = pfw.size.Size.eGran.M

class Partition:
   class FormatError( TypeError ): pass
   class MountError( TypeError ): pass

   class Description:
      def __init__( self, **kwargs ):
         kw_start = kwargs.get( "start", None )
         kw_end = kwargs.get( "end", None )
         kw_size = kwargs.get( "size", None )
         kw_label = kwargs.get( "label", "NoLabel" )
         kw_fs = kwargs.get( "fs", "ext4" )
         kw_type = kwargs.get( "type", 83 )
         kw_clone_from = kwargs.get( "clone_from", None )
         kw_file = kwargs.get( "file", None )

         kw_clone_from_size = None
         if None != kw_clone_from:
            if False == os.path.exists( kw_clone_from ):
               pfw.console.debug.warning( f"'clone_from' file does not exist: '{kw_clone_from}'" )
            else:
               kw_clone_from_size = pfw.size.Size( os.stat( kw_clone_from ).st_size, pfw.size.Size.eGran.B, align = ALIGN_SIZE )

         if None != kw_start and None != kw_end:
            self.__start = copy.deepcopy( kw_start )
            self.__end = copy.deepcopy( kw_end )
            self.__size = kw_end - kw_start + pfw.size.SizeSector
            if None != kw_clone_from_size and self.__size < kw_clone_from_size:
               pfw.console.debug.error( "'size' < 'clone_from' size" )
         elif None != kw_size or None != kw_clone_from_size:
            if None != kw_clone_from_size:
               kw_size = kw_clone_from_size
            if None != kw_start:
               self.__start = copy.deepcopy( kw_start )
               self.__end = kw_start + kw_size - pfw.size.SizeSector
               self.__size = copy.deepcopy( kw_size )
            elif None != kw_end:
               self.__start = kw_end - kw_size + pfw.size.SizeSector
               self.__end = copy.deepcopy( kw_end )
               self.__size = copy.deepcopy( kw_size )
            else:
               self.__start = pfw.size.SizeZero
               self.__end = copy.deepcopy( kw_size ) - pfw.size.SizeSector
               self.__size = copy.deepcopy( kw_size )
         else:
            pfw.console.debug.error( "Any valid combination of 'start', 'end', 'size', 'clone_from' have not been defined" )
            raise AttributeError

         self.__label = copy.deepcopy( kw_label )
         self.__fs = copy.deepcopy( kw_fs )
         self.__type = copy.deepcopy( kw_type )
         self.__clone_from = copy.deepcopy( kw_clone_from )
         self.__file = copy.deepcopy( kw_file )
      # def __init__

      def __del__( self ):
         pass
      # def __del__

      def __str__( self ):
         attr_list = [ i for i in Partition.Description.__dict__.keys( ) if i[:2] != pfw.base.class_ignore_field ]
         vector = [ ]
         for attr in attr_list:
            vector.append( str( attr ) + " = " + str( self.__dict__.get( attr ) ) )
         name = "Partition.Description { " + ", ".join( vector ) + " }"
         return name
      # def __str__

      def __setattr__( self, attr, value ):
         attr_list = [ i for i in Partition.Description.__dict__.keys( ) ]
         if attr in attr_list:
            self.__dict__[ attr ] = value
            return
         raise AttributeError
      # def __setattr__

      def info( self, tabulations: int = 0 ):
         pfw.console.debug.info( self.__class__.__name__, ":", tabs = ( tabulations + 0 ) )
         self.__start.info( tabulations + 1 )
         self.__end.info( tabulations + 1 )
         self.__size.info( tabulations + 1 )
         pfw.console.debug.info( "label:        \'", self.__label, "\'", tabs = ( tabulations + 1 ) )
         pfw.console.debug.info( "type:         \'", self.__type, "\'", tabs = ( tabulations + 1 ) )
         pfw.console.debug.info( "fs:           \'", self.__fs, "\'", tabs = ( tabulations + 1 ) )
         pfw.console.debug.info( "clone_from:   \'", self.__clone_from, "\'", tabs = ( tabulations + 1 ) )
         pfw.console.debug.info( "file:         \'", self.__file, "\'", tabs = ( tabulations + 1 ) )
         pfw.console.debug.info( "mount_point:  \'", self.__mount_point, "\'", tabs = ( tabulations + 1 ) )
      # def info

      def start( self ):
         return self.__start
      # def start

      def end( self ):
         return self.__end
      # def start

      def size( self ):
         return self.__size
      # def start

      def set_size( self, size: pfw.size.Size = None ):
         self.__size = size
         self.__end = self.__start + self.__size - pfw.size.SizeSector
      # def set_start

      def label( self ):
         return self.__label
      # def label

      def set_label( self, label: str = None ):
         self.__label = label
      # def set_label

      def type( self ):
         return self.__type
      # def type

      def fs( self ):
         return self.__fs
      # def fs

      def set_fs( self, fs: str = None ):
         self.__fs = fs
      # def set_fs

      def clone_from( self ):
         return self.__clone_from
      # def clone_from

      def file( self ):
         return self.__file
      # def file

      def set_file( self, file: str = None ):
         self.__file = file
      # def set_file

      def mount_point( self ):
         return self.__mount_point
      # def mount_point

      def set_mount_point( self, mount_point: str = None ):
         self.__mount_point = mount_point
      # def set_mount_point



      __size = None # size = end - start + 1 sector
      __start = None # pointing to first partition sector
      __end = None # pointing to last partition sector
      __label = None
      __fs = None
      __type = None
      __clone_from = None
      __file = None
      __mount_point = None
   # class Description

   def __init__( self, description: Description, **kwargs ):
      kw_build = kwargs.get( "build", False )

      self.__description = Partition.Description(
            size = description.size( ),
            start = description.start( ),
            end = description.end( ),
            clone_from = description.clone_from( ),
            file = description.file( ),
         )

      if True == kw_build:
         self.build( description, **kwargs )
   # def __init__

   def __del__( self ):
      pass
   # def __del__

   def __setattr__( self, attr, value ):
      attr_list = [ i for i in Partition.__dict__.keys( ) ]
      if attr in attr_list:
         self.__dict__[ attr ] = value
         return
      raise AttributeError
   # def __setattr__

   def __str__( self ):
      attr_list = [ i for i in Partition.__dict__.keys( ) if i[:2] != pfw.base.class_ignore_field ]
      vector = [ ]
      for attr in attr_list:
         vector.append( str( attr ) + " = " + str( self.__dict__.get( attr ) ) )
      name = "Partition { " + ", ".join( vector ) + " }"
      return name
   # def __str__

   def info( self, tabulations: int = 0 ):
      pfw.console.debug.info( self.__class__.__name__, ":", tabs = ( tabulations + 0 ) )
      self.__description.info( tabulations + 1 )
   # def info

   def build( self, description: Description, **kwargs ):
      result: bool = False
      if True == self.create( **kwargs ):
         result = self.format( description.fs( ) )

      return result
   # def build

   def create( self, **kwargs ):
      kw_force = kwargs.get( "force", False )
      kw_file = kwargs.get( "file", self.__description.file( ) )
      kw_size = kwargs.get( "size", self.__description.size( ) )

      if None != self.__description.mount_point( ):
         pfw.console.debug.error( "image mounted" )
         return False

      if True == os.path.exists( kw_file ):
         if False == kw_force:
            pfw.console.debug.error( "file '%s' exists" % kw_file )
            return False
         else:
            pfw.console.debug.warning( "file '%s' exists, but will be deleted" % kw_file )
            self.delete( )


      self.__description.set_file( kw_file )
      self.__description.set_size( kw_size )
      self.__description.set_fs( )

      if False == create( kw_file, kw_size ):
         pfw.console.debug.error( "image can't be created: (%s)" % ( kw_file ) )
         return False

      return True
   # def create

   def delete( self ):
      result_code = pfw.shell.run_and_wait_with_status( "rm", self.__description.file( ) )["code"]
      return 0 == result_code
   # def delete

   def mount( self, mount_point: str, gen_subdir: bool = False ):
      if None == mount_point:
            pfw.console.debug.error( "Mount point is not defined: '%s'" % self.__description.file( ) )
            return None

      if True == gen_subdir:
         mount_point = gen_mount_point( mount_point )

      if None == self.__description.fs( ):
         pfw.console.debug.error( "Partition is not formated: '%s'" % self.__description.file( ) )
         return None

      if False == mount( self.__description.file( ), mount_point, self.__description.fs( ) ):
         return None

      self.__description.set_mount_point( mount_point )
      return mount_point
   # def mount

   def umount( self ):
      if None == self.__description.mount_point( ):
         pfw.console.debug.error( "Partition is not mounted: '%s'" % self.__description.file( ) )
         return False

      if False == umount( self.__description.file( ) ):
         return False

      self.__description.set_mount_point( )
      return True
   # def umount

   def format( self, fs: str ):
      if None == fs:
         pfw.console.debug.error( "Filesystem is None" )
         return False

      if False == format( self.__description.file( ), fs ):
         return False

      self.__description.set_fs( fs )
      return True
   # def format

   def copy_to( self, source: str, destination: str = "" ):
      if None == self.__description.mount_point( ):
         return False

      if False == os.path.exists( source ):
         return False

      result_code = pfw.shell.run_and_wait_with_status(
              "sudo", "cp"
            , source
            , os.path.join( self.__description.mount_point( ), destination )
         )["code"]
      if 0 != result_code:
         return False

      return True
   # def copy_to

   def copy_from( self, source: str, destination: str ):
      if None == self.__description.mount_point( ):
         return 255

      result_code = pfw.shell.run_and_wait_with_status(
              "sudo", "cp"
            , os.path.join( self.__description.mount_point( ), source )
            , destination
         )["code"]
      if 0 != result_code:
         return False

      return True
   # def copy_from

   def mkdir( self, directory: str ):
      return pfw.shell.run_and_wait_with_status(
              "sudo", "mkdir", "-p"
            , os.path.join( self.__description.mount_point( ), directory )
         )["code"]
   # def mkdir



   __description: Description = None
# class Partition



# https://unix.stackexchange.com/questions/281589/how-to-run-mkfs-on-file-image-partitions-without-mounting
# https://unix.stackexchange.com/questions/316401/how-to-mount-a-disk-image-from-the-command-line
class Drive:
   class FormatError( TypeError ): pass
   class MountError( TypeError ): pass

   def __init__( self, file: str ):
      self.__file = file
      self.__partitions = [ ]
   # def __init__

   def __del__( self ):
      pass
   # def __del__

   def __setattr__( self, attr, value ):
      attr_list = [ i for i in Drive.__dict__.keys( ) ]
      if attr in attr_list:
         self.__dict__[ attr ] = value
         return
      raise AttributeError
   # def __setattr__

   def __str__( self ):
      attr_list = [ i for i in Drive.__dict__.keys( ) if i[:2] != pfw.base.class_ignore_field ]
      vector = [ ]
      for attr in attr_list:
         vector.append( str( attr ) + " = " + str( self.__dict__.get( attr ) ) )
      name = "Drive { " + ", ".join( vector ) + " }"
      return name
   # def __str__

   def info( self, tabulations: int = 0 ):
      pfw.console.debug.info( self.__class__.__name__, ":", tabs = ( tabulations + 0 ) )
      pfw.console.debug.info( "file:      \'", self.__file, "\'", tabs = ( tabulations + 1 ) )
      self.__size.info( tabulations + 1 )
      pfw.console.debug.info( "attached:  \'", self.__attached_to, "\'", tabs = ( tabulations + 1 ) )
      pfw.console.debug.info( "bootable:  \'", self.__bootable_index, "\'", tabs = ( tabulations + 1 ) )
      for index in range( len( self.__partitions ) ):
         self.__partitions[index].info( tabulations + 1 )
   # def info

   def create( self, **kwargs ):
      kw_size = kwargs.get( "size", pfw.size.SizeZero )
      kw_partitions = kwargs.get( "partitions", [ ] )
      kw_force = kwargs.get( "force", False )
      kw_file = kwargs.get( "file", self.__file )

      partitions_size: pfw.size.Size = self.__reserved_start_size + self.__reserved_end_size
      for partition in kw_partitions:
         partitions_size += partition.size( )
      kw_size = pfw.size.max( kw_size, partitions_size )

      if None != self.__attached_to:
         pfw.console.debug.error( "image attached" )
         return False

      if True == os.path.exists( kw_file ):
         if False == kw_force:
            pfw.console.debug.error( "file '%s' exists" % kw_file )
            return False
         else:
            pfw.console.debug.warning( "file '%s' exists, but will be deleted" % kw_file )
            self.delete( )

      self.__file = kw_file
      self.__size = copy.deepcopy( kw_size ).align( ALIGN_SIZE )

      if False == create( kw_file, kw_size ):
         pfw.console.debug.error( "image can't be created: (%s)" % ( kw_file ) )
         return False

      return True
   # def create

   def delete( self ):
      if None != self.__attached_to:
         if False == self.detach( ):
            return False

      result_code = pfw.shell.run_and_wait_with_status( "rm", self.__file )["code"]
      if 0 != result_code:
         pfw.console.debug.error( "image can't be deleted(%s): (%d)" % ( self.__file, result_code ) )
         return False

      self.__size = None
      return True
   # def delete

   def attach( self ):
      if None != self.__attached_to:
         pfw.console.debug.error( "image '%s' is attached to '%s'" % ( self.__file, self.__attached_to ) )
         return False

      self.__attached_to = attach( self.__file )
      return None != self.__attached_to
   # def attach

   def detach( self ):
      if None == self.__attached_to:
         pfw.console.debug.error( "image '%s' is not attached" % self.__file )
         return False

      self.umount( )

      if False == detach( self.__attached_to ):
         return False

      self.__attached_to = None
      return True
   # def detach

   def init( self, partitions: list, **kwargs ):
      kw_util = kwargs.get( "util", "parted" )
      kw_bootable = kwargs.get( "bootable", None )

      if None == self.__attached_to:
         pfw.console.debug.error( "image '%s' is not attached" % self.__file )
         return False

      common_size: pfw.size.Size = copy.deepcopy( self.__reserved_start_size )
      for partition in partitions:
         common_size += partition.size( )

      if common_size > self.__size:
         pfw.console.debug.error( "oversize" )
         return False

      self.__bootable_index = kw_bootable

      # Creating partitions
      if "sfdisk" == kw_util:
         # Building script file for 'sfdisk' command
         pfw.shell.run_and_wait_with_status( "mkdir", "-p" , "/tmp/loop" )["code"]
         dump_file = open( "/tmp/loop/dump", "w+" )
         dump_file.write( "label: dos\n" )
         dump_file.write( "label-id: 0xca40f2e0\n" )
         dump_file.write( "device: " + self.__attached_to + "\n" )
         dump_file.write( "unit: sectors\n" )
         dump_file.write( "\n" )
         next_start: int = 2048
         for index in range( len( partitions ) ):
            self.__partitions.append( Partition.Description( next_start, partitions[index].size( ), 83 ) )

            dump_file.write(
                  self.__attached_to + "p" + str(index + 1) + 
                  " : start= " + str(next_start) + 
                  ", size= " + str(partitions[index].size( ).sectors( )) + 
                  ", type=83"
               )
            if None != self.__bootable_index and self.__bootable_index == index:
               dump_file.write( ", bootable" )
            dump_file.write( "\n" )
            next_start += partitions[index].size( ).sectors( )
         dump_file.write( "\n" )
         dump_file.close( )
         # Apply partition table using 'sfdisk' command
         commands: str = "sudo sfdisk " + self.__attached_to + " < /tmp/loop/dump"
         pfw.console.debug.header( commands )
         os.system( commands )
      elif "parted" == kw_util:
         pfw.shell.run_and_wait_with_status( f"sudo parted {self.__attached_to} -s mklabel gpt" )

         ( start, end ) = ( pfw.size.SizeZero, self.__reserved_start_size - pfw.size.SizeSector )
         for index in range( len( partitions ) ):
            partition = partitions[index]

            start = end + pfw.size.SizeSector
            end = end + partition.size( )

            # Create partition
            pfw.shell.run_and_wait_with_status(
                  f"sudo parted {self.__attached_to} -s mkpart {partition.label( )} {partition.fs( )} {start.sectors( result = 'quotient' )}s {end.sectors( result = 'quotient' )}s"
               )

            pfw.shell.run_and_wait_with_status( f"sudo parted {self.__attached_to} print {index + 1}" )

            # Add partition to the list
            self.__partitions.append(
                  Partition.Description(
                        start = start,
                        end = end,
                        fs = partition.fs( ),
                        label = partition.label( ),
                        clone_from = partition.clone_from( )
                     )
               )

         if None != self.__bootable_index:
            pfw.shell.run_and_wait_with_status( f"sudo parted {self.__attached_to} set {self.__bootable_index} boot on" )

         pfw.shell.run_and_wait_with_status( f"sudo parted {self.__attached_to} -s print unit s print" )
         pfw.shell.run_and_wait_with_status( f"sudo partprobe {self.__attached_to}" )
      else:
         raise AttributeError

      # Format or clone all partitions
      self.init_partitions( )

      return True
   # def init

   def init_partitions( self ):
      if None == self.__attached_to:
         pfw.console.debug.error( "image must be attached" )
         return False

      for index in range( len( self.__partitions ) ):
         partition = self.__partitions[index]
         if None != partition.clone_from( ):
            pfw.shell.run_and_wait_with_status(
                  f"sudo dd if={partition.clone_from( )} of={self.__attached_to}p{index + 1} bs=1M status=none", test = False
               )
         else:
            self.format( index + 1, partition.fs( ) )

      return True
   # def init_partitions

   def format( self, partition: int, fs: str ):
      return format( self.__attached_to + "p" + str(partition), fs )
   # def format

   def mount( self, partition: int, mount_point: str, gen_subdir: bool = False ):
      # Could be done without attach:
      # https://superuser.com/questions/694430/how-to-inspect-disk-image

      if None == self.__attached_to:
         pfw.console.debug.error( "image '%s' is not attached" % self.__file )
         return None

      if None == mount_point:
            pfw.console.debug.error( "Mount point is not defined" )
            return None

      if True == gen_subdir:
         mount_point = gen_mount_point( mount_point )

      if False == mount( f"{self.__attached_to}p{partition}", mount_point ):
         return None

      self.__partitions[ partition - 1 ].set_mount_point( mount_point )

      return mount_point
   # def mount

   def umount( self, partition: int = None ):
      if None == self.__attached_to:
         pfw.console.debug.error( "image '%s' is not attached" % self.__file )
         return False

      indexes: list = [ ]
      if None == partition:
         indexes = range( 1, len( self.__partitions ) + 1 )
      else:
         indexes = [ partition ]

      result_code: bool = True
      for index in indexes:
         if None == self.__partitions[ index - 1 ].mount_point( ):
            continue

         if False == umount( self.__partitions[ index - 1 ].mount_point( ) ):
            self.__partitions[ index - 1 ].set_mount_point( )
         else:
            result_code = False

      return result_code
   # def umount





   __file: str = None
   __size: pfw.size.Size = None
   __attached_to: int = None
   __partitions: list = [ ]
   __bootable_index: int = None
   __reserved_start_size = pfw.size.SizeMegabyte # first 2048 reserved sectors
   __reserved_end_size = pfw.size.SizeMegabyte # last 2048 reserved sectors
# class Drive
