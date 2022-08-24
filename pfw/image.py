import os
import copy

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



class Description:
   def __init__( self, file: str, mount_point: str, size: str, fs: str ):
      self.__file = file
      self.__mount_point = mount_point
      self.__size = size
      self.__fs = fs
   # def __init__

   def __del__( self ):
      pass
   # def __del__

   def __setattr__( self, attr, value ):
      attr_list = [ i for i in Description.__dict__.keys( ) ]
      if attr in attr_list:
         self.__dict__[ attr ] = value
         return
      raise AttributeError
   # def __setattr__

   def __str__( self ):
      attr_list = [ i for i in Description.__dict__.keys( ) if i[:2] != pfw.base.class_ignore_field ]
      vector = [ ]
      for attr in attr_list:
         vector.append( str( attr ) + " = " + str( self.__dict__.get( attr ) ) )
      name = "Description { " + ", ".join( vector ) + " }"
      return name
   # def __str__

   def info( self, tabulations: int = 0 ):
      pfw.console.debug.info( self.__class__.__name__, ":", tabs = ( tabulations + 0 ) )
      pfw.console.debug.info( "file:         \'", self.__file, "\'", tabs = ( tabulations + 1 ) )
      pfw.console.debug.info( "size:         \'", self.__size, "\'", tabs = ( tabulations + 1 ) )
      pfw.console.debug.info( "mount point:  \'", self.__mount_point, "\'", tabs = ( tabulations + 1 ) )
      pfw.console.debug.info( "fs:           \'", self.__fs, "\'", tabs = ( tabulations + 1 ) )
   # def info

   def resize( self, size ):
      self.__size = size

   def file( self ):
      return self.__file
   # def arch

   def mount_point( self ):
      return self.__mount_point
   # def arch

   def size( self ):
      return self.__size
   # def arch

   def fs( self ):
      return self.__fs
   # def arch

   __file: str = None
   __mount_point: str = None
   __size: str = None
   __fs: str = None
# class Description


class Partition:
   class FormatError( TypeError ): pass
   class MountError( TypeError ): pass

   def __init__( self, file: str ):
      self.__file = file
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
      pfw.console.debug.info( "image:        \'", self.__file, "\'", tabs = ( tabulations + 1 ) )
      pfw.console.debug.info( "mount point:  \'", self.__mount_point, "\'", tabs = ( tabulations + 1 ) )
      self.__size.info( tabulations + 1 )
   # def info

   def create( self, size: pfw.size.Size, force: bool = False ):
      if None != self.__mount_point:
         pfw.console.debug.error( "image mounted" )
         return False

      if True == os.path.exists( self.__file ):
         if False == force:
            pfw.console.debug.error( "file exists: ", self.__file )
            return False
         else:
            pfw.console.debug.warning( "file exists: ", self.__file )
            self.delete( )

      self.__size = size
      self.__size.align( pfw.size.Size.eGran.M )

      result_code = pfw.shell.run_and_wait_with_status(
              "dd"
            , "if=/dev/zero"
            , "of=" + self.__file
            , "bs=" + str( int( pfw.size.Size.eGran.M ) )
            , "count=" + str( self.__size.megabytes( ) )
         )["code"]
      return 0 == result_code
   # def create

   def delete( self ):
      result_code = pfw.shell.run_and_wait_with_status( "rm", self.__file )["code"]
      return 0 == result_code
   # def delete

   def mount( self, mount_point: str ):
      if None == self.__file_system:
         raise self.MountError( "Partition is not formated: '%s'" % self.__file )

      result_code = pfw.shell.run_and_wait_with_status( "sudo", "mkdir", "-p", mount_point )["code"]
      if 0 != result_code:
         return False

      result_code = pfw.shell.run_and_wait_with_status(
              "sudo", "mount"
            , "-t", self.__file_system
            , self.__file
            , mount_point
            , "-o", "loop"
         )["code"]
      if 0 != result_code:
         return False

      self.__mount_point = mount_point
      return True
   # def mount

   def umount( self ):
      if None == self.__mount_point:
         raise self.MountError( "Partition is not mounted: '%s'" % self.__file )

      result_code = pfw.shell.run_and_wait_with_status(
              "sudo", "umount"
            , self.__file
         )["code"]
      if 0 != result_code:
         return False

      self.__mount_point = None
      return True
   # def umount

   def format( self, file_system: str ):
      result = format ( self.__file, file_system )
      if True == result:
         self.__file_system = file_system
      return result
   # def format

   def copy_to( self, source: str, destination: str = "" ):
      if None == self.__mount_point:
         return 255

      if False == os.path.exists( source ):
         return 254

      result_code = pfw.shell.run_and_wait_with_status(
              "sudo", "cp"
            , source
            , os.path.join( self.__mount_point, destination )
         )["code"]
      if 0 != result_code:
         return False

      return True
   # def copy_to

   def copy_from( self, source: str, destination: str ):
      if None == self.__mount_point:
         return 255

      result_code = pfw.shell.run_and_wait_with_status(
              "sudo", "cp"
            , os.path.join( self.__mount_point, source )
            , destination
         )["code"]
      if 0 != result_code:
         return False

      return True
   # def copy_from

   def mkdir( self, dir: str ):
      return pfw.shell.run_and_wait_with_status(
              "sudo", "mkdir", "-p"
            , os.path.join( self.__mount_point, dir )
         )["code"]
   # def mkdir




   __file: str = None
   __size: pfw.size.Size = None
   __file_system: str = None
   __mount_point: str = None
# class Partition



# https://unix.stackexchange.com/questions/281589/how-to-run-mkfs-on-file-image-partitions-without-mounting
# https://unix.stackexchange.com/questions/316401/how-to-mount-a-disk-image-from-the-command-line
class Drive:
   class FormatError( TypeError ): pass
   class MountError( TypeError ): pass

   class Partition:
      def __init__( self, **kwargs ):
         kw_start = kwargs.get( "start", None )
         kw_end = kwargs.get( "end", None )
         kw_size = kwargs.get( "size", None )
         kw_label = kwargs.get( "label", "NoLabel" )
         kw_fs = kwargs.get( "fs", "ext4" )
         kw_type = kwargs.get( "type", 83 )
         kw_clone_from = kwargs.get( "clone_from", None )

         if None != kw_start and None != kw_end:
            self.__start = copy.deepcopy( kw_start )
            self.__end = copy.deepcopy( kw_end )
            self.__size = kw_end - kw_start + pfw.size.SizeSector
         elif None != kw_size or None != kw_clone_from:
            if None != kw_clone_from:
               kw_size = pfw.size.Size( os.stat( kw_clone_from ).st_size, pfw.size.Size.eGran.B, align = pfw.size.Size.eGran.M )
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

         self.__label = kw_label
         self.__fs = kw_fs
         self.__type = kw_type
         self.__clone_from = kw_clone_from
      # def __init__

      def __del__( self ):
         pass
      # def __del__

      def __str__( self ):
         attr_list = [ i for i in Drive.Partition.__dict__.keys( ) if i[:2] != pfw.base.class_ignore_field ]
         vector = [ ]
         for attr in attr_list:
            vector.append( str( attr ) + " = " + str( self.__dict__.get( attr ) ) )
         name = "Drive.Partition { " + ", ".join( vector ) + " }"
         return name
      # def __str__

      def __setattr__( self, attr, value ):
         attr_list = [ i for i in Drive.Partition.__dict__.keys( ) ]
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

      def label( self ):
         return self.__label
      # def label

      def type( self ):
         return self.__type
      # def type

      def fs( self ):
         return self.__fs
      # def fs

      def clone_from( self ):
         return self.__clone_from
      # def clone_from



      __size = None; # size = end - start + 1 sector
      __start = None; # pointing to first partition sector
      __end = None; # pointing to last partition sector
      __label = None;
      __fs = None;
      __type = None;
      __clone_from = None;
   # class Partition

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
      kw_align = kwargs.get( "align", "parted" )
      kw_force = kwargs.get( "force", False )

      partitions_size: pfw.size.Size = self.__reserved_start_size + self.__reserved_end_size
      for partition in kw_partitions:
         partitions_size += partition.size( )
      kw_size = pfw.size.max( kw_size, partitions_size )

      if None != self.__attached_to:
         pfw.console.debug.error( "image attached" )
         return False

      if True == os.path.exists( self.__file ):
         if False == kw_force:
            pfw.console.debug.warning( "file exists: ", self.__file )
            self.__size = pfw.size.Size( os.stat( self.__file ).st_size )
            return False
         else:
            pfw.console.debug.warning( "file exists but will be deleted: ", self.__file )
            self.delete( )
            self.__size = copy.deepcopy( kw_size ).align( pfw.size.Size.eGran.M )
      else:
         self.__size = copy.deepcopy( kw_size ).align( pfw.size.Size.eGran.M )

      result_code = pfw.shell.run_and_wait_with_status(
              "dd"
            , "if=/dev/zero"
            , "of=" + self.__file
            , "bs=" + str( int( pfw.size.Size.eGran.M ) )
            , "count=" + str( self.__size.megabytes( ) )
         )["code"]
      if 0 != result_code:
         pfw.console.debug.error( "image can't be created(%s): (%d)" % ( self.__file, result_code ) )
         self.__size = None
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

      result = pfw.shell.run_and_wait_with_status( "sudo", "losetup", "-f" )
      if 0 != result["code"]:
         pfw.console.debug.error( "free loop device was not find" )
         return False
      attach_to: str = result["output"]

      result_code = pfw.shell.run_and_wait_with_status(
            "sudo", "losetup", "-v", "-P", attach_to, self.__file
         )["code"]
      if 0 != result_code:
         pfw.console.debug.error( "image attach error to device(%s): (%d)" % ( attach_to, result_code ) )
         return False

      self.__attached_to = attach_to
      return True
   # def attach

   def detach( self ):
      if None == self.__attached_to:
         pfw.console.debug.error( "image '%s' is not attached" % self.__file )
         return False

      self.umount( )

      result_code = pfw.shell.run_and_wait_with_status( "sudo", "losetup", "-d", self.__attached_to )["code"]
      if 0 != result_code:
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
            self.__partitions.append( Drive.Partition( next_start, partitions[index].size( ), 83 ) )

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

            pfw.shell.run_and_wait_with_status(
                  f"sudo parted {self.__attached_to} -s mkpart {partition.label( )} {partition.fs( )} {start.sectors( )}s {end.sectors( )}s"
               )

            pfw.shell.run_and_wait_with_status( f"sudo parted {self.__attached_to} print {index + 1}" )

            self.__partitions.append(
                  Drive.Partition(
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
      for index in range( len( partitions ) ):
         partition = partitions[index]
         if None != partition.clone_from( ):
            pfw.shell.run_and_wait_with_status(
                  f"sudo dd if={partition.clone_from( )} of={self.__attached_to}p{index + 1} bs=1M status=none", test = False
               )
         else:
            self.format( index + 1, partition.fs( ) )

      return True
   # def init

   def format( self, partition: int, file_system: str ):
      return format( self.__attached_to + "p" + str(partition), file_system )
   # def format

   def mount( self, partition: int, mount_point: str ):
      # Could be done without attach:
      # https://superuser.com/questions/694430/how-to-inspect-disk-image

      if None == self.__attached_to:
         pfw.console.debug.error( "image '%s' is not attached" % self.__file )
         return False

      result_code = pfw.shell.run_and_wait_with_status( "sudo", "mkdir", "-p", mount_point )["code"]
      if 0 != result_code:
         pfw.console.debug.error( "create directory '%s' error: %d" % ( mount_point, result_code ) )
         return False

      result_code = pfw.shell.run_and_wait_with_status(
              "sudo", "mount"
            , self.__attached_to + "p" + str(partition)
            , mount_point
         )["code"]
      if 0 != result_code:
         pfw.console.debug.error( "mount partition '%s' to directory '%s' error: %d" % ( self.__attached_to + "p" + str(partition), mount_point, result_code ) )
         return False

      return True
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
         result_umount = pfw.shell.run_and_wait_with_status(
                 "sudo", "umount", self.__attached_to + "p" + str(index)
            )["code"]
         if 0 != result_umount:
            pfw.console.debug.error( "umount partition '%s' error: %d" % ( self.__attached_to + "p" + str(index), result_umount ) )
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
