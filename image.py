import os

import base.console
import base.shell
import base.size



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
      attr_list = [ i for i in Description.__dict__.keys( ) if i[:2] != base.base.class_ignore_field ]
      vector = [ ]
      for attr in attr_list:
         vector.append( str( attr ) + " = " + str( self.__dict__.get( attr ) ) )
      name = "Description { " + ", ".join( vector ) + " }"
      return name
   # def __str__

   def info( self, tabulations: int = 0 ):
      base.console.debug.info( self.__class__.__name__, ":", tabs = ( tabulations + 0 ) )
      base.console.debug.info( "file:         \'", self.__file, "\'", tabs = ( tabulations + 1 ) )
      base.console.debug.info( "size:         \'", self.__size, "\'", tabs = ( tabulations + 1 ) )
      base.console.debug.info( "mount point:  \'", self.__mount_point, "\'", tabs = ( tabulations + 1 ) )
      base.console.debug.info( "fs:           \'", self.__fs, "\'", tabs = ( tabulations + 1 ) )
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
      attr_list = [ i for i in Partition.__dict__.keys( ) if i[:2] != base.base.class_ignore_field ]
      vector = [ ]
      for attr in attr_list:
         vector.append( str( attr ) + " = " + str( self.__dict__.get( attr ) ) )
      name = "Partition { " + ", ".join( vector ) + " }"
      return name
   # def __str__

   def info( self, tabulations: int = 0 ):
      base.console.debug.info( self.__class__.__name__, ":", tabs = ( tabulations + 0 ) )
      base.console.debug.info( "image:        \'", self.__file, "\'", tabs = ( tabulations + 1 ) )
      base.console.debug.info( "mount point:  \'", self.__mount_point, "\'", tabs = ( tabulations + 1 ) )
      self.__size.info( tabulations + 1 )
   # def info

   def create( self, size: base.size.Size, force: bool = False ):
      if None != self.__mount_point:
         base.console.debug.error( "image mounted" )
         return False

      if True == os.path.exists( self.__file ):
         if False == force:
            base.console.debug.error( "file exists: ", self.__file )
            return False
         else:
            base.console.debug.warning( "file exists: ", self.__file )
            self.delete( )

      self.__size = size
      self.__size.align( base.size.Size.eGran.M )

      result_code = base.shell.run_and_wait_with_status(
              "dd"
            , "if=/dev/zero"
            , "of=" + self.__file
            , "bs=" + str( int( base.size.Size.eGran.M ) )
            , "count=" + str( self.__size.megabytes( ) )
         )["code"]
      return 0 == result_code
   # def create

   def delete( self ):
      result_code = base.shell.run_and_wait_with_status( "rm", self.__file )["code"]
      return 0 == result_code
   # def delete

   def mount( self, mount_point: str ):
      if None == self.__file_system:
         raise self.MountError( "Partition is not formated: '%s'" % self.__file )

      result_code = base.shell.run_and_wait_with_status( "sudo", "mkdir", "-p", mount_point )["code"]
      if 0 != result_code:
         return False

      result_code = base.shell.run_and_wait_with_status(
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

      result_code = base.shell.run_and_wait_with_status(
              "sudo", "umount"
            , self.__file
         )["code"]
      if 0 != result_code:
         return False

      self.__mount_point = None
      return True
   # def umount

   def format( self, file_system: str ):
      result_code = base.shell.run_and_wait_with_status(
            "mkfs"
            , "-t", file_system
            , self.__file
         )["code"]
      if 0 != result_code:
         return False

      self.__file_system = file_system
      return True
   # def format

   def copy_to( self, source: str, destination: str = "" ):
      if None == self.__mount_point:
         return 255

      if False == os.path.exists( source ):
         return 254

      result_code = base.shell.run_and_wait_with_status(
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

      result_code = base.shell.run_and_wait_with_status(
              "sudo", "cp"
            , os.path.join( self.__mount_point, source )
            , destination
         )["code"]
      if 0 != result_code:
         return False

      return True
   # def copy_from

   def mkdir( self, dir: str ):
      return base.shell.run_and_wait_with_status(
              "sudo", "mkdir", "-p"
            , os.path.join( self.__mount_point, dir )
         )["code"]
   # def mkdir




   __file: str = None
   __size: base.size.Size = None
   __file_system: str = None
   __mount_point: str = None
# class Partition



# https://unix.stackexchange.com/questions/281589/how-to-run-mkfs-on-file-image-partitions-without-mounting
# https://unix.stackexchange.com/questions/316401/how-to-mount-a-disk-image-from-the-command-line
class Drive:
   class FormatError( TypeError ): pass
   class MountError( TypeError ): pass

   class Partition:
      def __init__( self, start: int, end: int, id_type: int = 83 ):
         self.__start = start
         self.__end = end
         self.__size = base.size.Size( self.__end - self.__start + 1, base.size.Size.eGran.S )
         self.__id_type = id_type
      # def __init__
      def __init__( self, start: int, size: base.size.Size, id_type: int = 83 ):
         self.__start = start
         self.__size = size
         self.__end = self.__start + self.__size.sectors( ) -1 
         self.__id_type = id_type
      # def __init__

      def __del__( self ):
         pass
      # def __del__

      def __setattr__( self, attr, value ):
         attr_list = [ i for i in Drive.Partition.__dict__.keys( ) ]
         if attr in attr_list:
            self.__dict__[ attr ] = value
            return
         raise AttributeError
      # def __setattr__

      def __str__( self ):
         attr_list = [ i for i in Drive.Partition.__dict__.keys( ) if i[:2] != base.base.class_ignore_field ]
         vector = [ ]
         for attr in attr_list:
            vector.append( str( attr ) + " = " + str( self.__dict__.get( attr ) ) )
         name = "Drive.Partition { " + ", ".join( vector ) + " }"
         return name
      # def __str__

      def info( self, tabulations: int = 0 ):
         base.console.debug.info( self.__class__.__name__, ":", tabs = ( tabulations + 0 ) )
         base.console.debug.info( "start:     \'", self.__start, "\'", tabs = ( tabulations + 1 ) )
         base.console.debug.info( "end:       \'", self.__end, "\'", tabs = ( tabulations + 1 ) )
         self.__size.info( tabulations + 1 )
         base.console.debug.info( "id type:   \'", self.__id_type, "\'", tabs = ( tabulations + 1 ) )
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

      def id_type( self ):
         return self.__id_type
      # def start

      __start: int = None
      __end: int = None
      __size: base.size.Size = None
      __id_type: int = None
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
      attr_list = [ i for i in Drive.__dict__.keys( ) if i[:2] != base.base.class_ignore_field ]
      vector = [ ]
      for attr in attr_list:
         vector.append( str( attr ) + " = " + str( self.__dict__.get( attr ) ) )
      name = "Drive { " + ", ".join( vector ) + " }"
      return name
   # def __str__

   def info( self, tabulations: int = 0 ):
      base.console.debug.info( self.__class__.__name__, ":", tabs = ( tabulations + 0 ) )
      base.console.debug.info( "file:      \'", self.__file, "\'", tabs = ( tabulations + 1 ) )
      self.__size.info( tabulations + 1 )
      base.console.debug.info( "attached:  \'", self.__attached_to, "\'", tabs = ( tabulations + 1 ) )
      base.console.debug.info( "bootable:  \'", self.__bootable_index, "\'", tabs = ( tabulations + 1 ) )
      for index in range( len( self.__partitions ) ):
         self.__partitions[index].info( tabulations + 1 )
   # def info

   def create( self, size: base.size.Size, force: bool = False ):
      if None != self.__attached_to:
         base.console.debug.error( "image attached" )
         return False

      if True == os.path.exists( self.__file ):
         if False == force:
            base.console.debug.error( "file exists: ", self.__file )
            return False
         else:
            base.console.debug.warning( "file exists: ", self.__file )
            self.delete( )

      self.__size = size
      self.__size.align( base.size.Size.eGran.M )

      result_code = base.shell.run_and_wait_with_status(
              "dd"
            , "if=/dev/zero"
            , "of=" + self.__file
            , "bs=" + str( int( base.size.Size.eGran.M ) )
            , "count=" + str( self.__size.megabytes( ) )
         )["code"]
      if 0 != result_code:
         base.console.debug.error( "image can't be created(%s): (%d)" % ( self.__file, result_code ) )
         self.__size = None
         return False

      return True
   # def create

   def delete( self ):
      if None != self.__attached_to:
         if False == self.detach( ):
            return False

      result_code = base.shell.run_and_wait_with_status( "rm", self.__file )["code"]
      if 0 != result_code:
         base.console.debug.error( "image can't be deleted(%s): (%d)" % ( self.__file, result_code ) )
         return False

      self.__size = None
      return True
   # def delete

   def attach( self ):
      if None != self.__attached_to:
         base.console.debug.error( "image '%s' is attached to '%s'" % ( self.__file, self.__attached_to ) )
         return False

      result = base.shell.run_and_wait_with_status( "sudo", "losetup", "-f" )
      if 0 != result["code"]:
         base.console.debug.error( "free loop device was not find" )
         return False
      attach_to: str = result["output"]

      result_code = base.shell.run_and_wait_with_status(
            "sudo", "losetup", "-v", "-P", attach_to, self.__file
         )["code"]
      if 0 != result_code:
         base.console.debug.error( "image attach error to device(%s): (%d)" % ( attach_to, result_code ) )
         return False

      self.__attached_to = attach_to
      return True
   # def attach

   def detach( self ):
      if None == self.__attached_to:
         base.console.debug.error( "image '%s' is not attached" % self.__file )
         return False

      self.umount( )

      result_code = base.shell.run_and_wait_with_status( "sudo", "losetup", "-d", self.__attached_to )["code"]
      if 0 != result_code:
         return False

      self.__attached_to = None
      return True
   # def detach

   def init( self, partitions: list, bootable_index: int = 0 ):
      if None == self.__attached_to:
         base.console.debug.error( "image '%s' is not attached" % self.__file )
         return False

      common_size: base.size.Size = base.size.Size( 2048, base.size.Size.eGran.S ) # first 2048 reserved sectors
      for partition in partitions:
         partition["size"].align( base.size.Size.eGran.S )
         common_size += partition["size"]

      if common_size > self.__size:
         base.console.debug.error( "oversize" )
         return False

      base.shell.run_and_wait_with_status( "mkdir", "-p" , "/tmp/loop" )["code"]

      self.__bootable_index = bootable_index

      # Building script file for 'sfdisk' command
      dump_file = open( "/tmp/loop/dump", "w+" )
      dump_file.write( "label: dos\n" )
      dump_file.write( "label-id: 0xca40f2e0\n" )
      dump_file.write( "device: " + self.__attached_to + "\n" )
      dump_file.write( "unit: sectors\n" )
      dump_file.write( "\n" )
      next_start: int = 2048
      for index in range( len( partitions ) ):
         self.__partitions.append( Drive.Partition( next_start, partitions[index]["size"], 83 ) )

         dump_file.write(
               self.__attached_to + "p" + str(index + 1) + 
               " : start= " + str(next_start) + 
               ", size= " + str(partitions[index]["size"].sectors( )) + 
               ", type=83"
            )
         if self.__bootable_index == index:
            dump_file.write( ", bootable" )
         dump_file.write( "\n" )
         next_start += partitions[index]["size"].sectors( )
      dump_file.write( "\n" )
      dump_file.close( )

      # Apply partition table using 'sfdisk' command
      commands: str = "sudo sfdisk " + self.__attached_to + " < /tmp/loop/dump"
      base.console.debug.header( commands )
      os.system( commands )

      # Format all partitions
      for index in range( len( partitions ) ):
         self.format( index + 1, partitions[index]["fs"] )

      return True
   # def init

   def format( self, partition: int, file_system: str ):
      result_code = base.shell.run_and_wait_with_status(
              "sudo", "mkfs"
            , "-t", file_system
            , self.__attached_to + "p" + str(partition)
         )["code"]
      if 0 != result_code:
         base.console.debug.error( "partition '%s' format error: %d" % ( self.__attached_to + "p" + str(partition), result_code ) )
         return False

      return True
   # def format

   def mount( self, partition: int, mount_point: str ):
      # Could be done without attach:
      # https://superuser.com/questions/694430/how-to-inspect-disk-image

      if None == self.__attached_to:
         base.console.debug.error( "image '%s' is not attached" % self.__file )
         return False

      result_code = base.shell.run_and_wait_with_status( "sudo", "mkdir", "-p", mount_point )["code"]
      if 0 != result_code:
         base.console.debug.error( "create directory '%s' error: %d" % ( mount_point, result_code ) )
         return False

      result_code = base.shell.run_and_wait_with_status(
              "sudo", "mount"
            , self.__attached_to + "p" + str(partition)
            , mount_point
         )["code"]
      if 0 != result_code:
         base.console.debug.error( "mount partition '%s' to directory '%s' error: %d" % ( self.__attached_to + "p" + str(index), mount_point, result_code ) )
         return False

      return True
   # def mount

   def umount( self, partition: int = None ):
      if None == self.__attached_to:
         base.console.debug.error( "image '%s' is not attached" % self.__file )
         return False

      indexes: list = [ ]
      if None == partition:
         indexes = range( 1, len( self.__partitions ) + 1 )
      else:
         indexes = [ partition ]

      result_code: bool = True
      for index in indexes:
         result_umount = base.shell.run_and_wait_with_status(
                 "sudo", "umount", self.__attached_to + "p" + str(index)
            )["code"]
         if 0 != result_umount:
            base.console.debug.error( "umount partition '%s' error: %d" % ( self.__attached_to + "p" + str(index), result_umount ) )
            result_code = False

      return result_code
   # def umount





   __file: str = None
   __size: base.size.Size = None
   __attached_to: int = None
   __partitions: list = [ ]
   __bootable_index: int = None
# class Drive
