import enum
import os
import copy
import re
import random
import tempfile

import pfw.base.struct
import pfw.console
import pfw.shell




class eFamily( enum.Enum ):
   def __str__( self ):
      return str( self.value )

   ext = "ext"
   fat = "fat"
# class eGran

class eName( enum.Enum ):
   def __str__( self ):
      return str( self.value )

   ext2 = "ext2"
   ext3 = "ext3"
   ext4 = "ext4"
   fat12 = "fat12"
   fat16 = "fat16"
   fat32 = "fat32"
   exfat = "exfat"
# class eGran



class FileSystem:
   def __init__( self, **kwargs ):
      self.__family = kwargs.get( "family", None )
      self.__name = kwargs.get( "name", None )
      self.__tool = kwargs.get( "tool", None )
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

      pfw.console.debug.info( f"family: '{self.__family}'", tabs = ( kw_tabulations + 1 ) )
      pfw.console.debug.info( f"name: '{self.__name}'", tabs = ( kw_tabulations + 1 ) )
      pfw.console.debug.info( f"tool: '{self.__tool}'", tabs = ( kw_tabulations + 1 ) )

   # def info

   def format( self, device: str, **kwargs ):
      kw_label = kwargs.get( "label", "NoLabel" )

      command: str = f"{self.__tool}"

      if eFamily.ext == self.__family:
         command += f" -L {kw_label}"
      elif eFamily.fat == self.__family:
         command += f" -n {kw_label}"
         if eName.fat12 == self.__name:
            command += f" -F 12"
         elif eName.fat16 == self.__name:
            command += f" -F 16"
         elif eName.fat32 == self.__name:
            command += f" -F 32"

      command += f" {device}"

      return 0 == pfw.shell.execute( command, sudo = True )["code"]
   # def format



   def family( self ):
      return self.__family
   # def family

   def name( self ):
      return self.__name
   # def name



   __family: eFamily = None
   __name: eName = None
   __tool: str = None
# class FileSystem




ext2: FileSystem = FileSystem(
      family = eFamily.ext,
      name = eName.ext2,
      tool = "mkfs.ext2",
   )

ext3: FileSystem = FileSystem(
      family = eFamily.ext,
      name = eName.ext3,
      tool = "mkfs.ext3",
   )

ext4: FileSystem = FileSystem(
      family = eFamily.ext,
      name = eName.ext4,
      tool = "mkfs.ext4",
   )

fat12: FileSystem = FileSystem(
      family = eFamily.fat,
      name = eName.fat12,
      tool = "mkfs.fat",
   )

fat16: FileSystem = FileSystem(
      family = eFamily.fat,
      name = eName.fat16,
      tool = "mkfs.fat",
   )

fat32: FileSystem = FileSystem(
      family = eFamily.fat,
      name = eName.fat32,
      tool = "mkfs.fat",
   )

exfat: FileSystem = FileSystem(
      family = eFamily.fat,
      name = eName.exfat,
      tool = "mkfs.exfat",
   )




def builder( name: str ):
   filesystems: dict = {
      "ext2"   : ext2,
      "ext3"   : ext3,
      "ext4"   : ext4,
      "fat12"  : fat12,
      "fat16"  : fat16,
      "fat32"  : fat32,
      "exfat"  : exfat,
   }

   fs = filesystems.get( name, None )
   if None == fs:
      pfw.console.debug.error( f"Undefined filesystem name: '{name}'" )

   return fs
# def builder
