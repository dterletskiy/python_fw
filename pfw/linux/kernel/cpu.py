#!/usr/bin/python3

import re

import pfw.console



# This class is designed to process the '/proc/stat' file and retrieve information about
# CPU load both in general and per core. The constructor takes a line read from '/proc/stat'
# as input and, if it matches the specified pattern, analyzes it to collect metrics related
# to the CPU (refer to 'https://man7.org/linux/man-pages/man5/proc.5.html' for details).

# The collected metrics from these objects can later be utilized for calculating CPU load (function 'cpu_load').
class ProcStatCPU:
   def __new__( cls, string: str, **kwargs ):
      pattern = rf"cpu(\d*)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)"
      if match := re.match( pattern, string ):
         return object.__new__( cls )

      return None
   # def __new__

   def __init__( self, string: str, **kwargs ):
      pattern = rf"cpu(\d*)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)"
      match = re.match( pattern, string )
      if None == match:
         return

      self.__string = string

      self.__core          = int( match.group(1) ) if "" != match.group(1) else "ALL"
      self.__user          = int( match.group(2) )
      self.__nice          = int( match.group(3) )
      self.__system        = int( match.group(4) )
      self.__idle          = int( match.group(5) )
      self.__iowait        = int( match.group(6) )
      self.__irq           = int( match.group(7) )
      self.__softirq       = int( match.group(8) )
      self.__steal         = int( match.group(9) )
      self.__guest         = int( match.group(10) )
      self.__guest_nice    = int( match.group(11) )

      self.__work = self.__user + self.__nice + self.__system + self.__irq + self.__softirq + self.__steal + self.__guest + self.__guest_nice

      self.__no_work = self.__idle + self.__iowait

      self.__total = self.__work + self.__no_work
   # def __init__

   def info( self, **kwargs ):
      kw_tabs = kwargs.get( "tabs", kwargs.get( "tabulations", 0 ) )
      kw_message = kwargs.get( "message", "" )
      pfw.console.printf.info( f"{kw_message} (type {self.__class__.__name__}):", tabs = ( kw_tabs + 0 ) )

      pfw.console.printf.info( "string:      \'", self.__string, "\'", tabs = ( kw_tabs + 1 ) )
      pfw.console.printf.info( "core:        \'", self.__core, "\'", tabs = ( kw_tabs + 1 ) )
      pfw.console.printf.info( "user:        \'", self.__user, "\'", tabs = ( kw_tabs + 1 ) )
      pfw.console.printf.info( "nice:        \'", self.__nice, "\'", tabs = ( kw_tabs + 1 ) )
      pfw.console.printf.info( "system:      \'", self.__system, "\'", tabs = ( kw_tabs + 1 ) )
      pfw.console.printf.info( "idle:        \'", self.__idle, "\'", tabs = ( kw_tabs + 1 ) )
      pfw.console.printf.info( "iowait:      \'", self.__iowait, "\'", tabs = ( kw_tabs + 1 ) )
      pfw.console.printf.info( "irq:         \'", self.__irq, "\'", tabs = ( kw_tabs + 1 ) )
      pfw.console.printf.info( "softirq:     \'", self.__softirq, "\'", tabs = ( kw_tabs + 1 ) )
      pfw.console.printf.info( "steal:       \'", self.__steal, "\'", tabs = ( kw_tabs + 1 ) )
      pfw.console.printf.info( "guest:       \'", self.__guest, "\'", tabs = ( kw_tabs + 1 ) )
      pfw.console.printf.info( "guest_nice:  \'", self.__guest_nice, "\'", tabs = ( kw_tabs + 1 ) )
      pfw.console.printf.info( "work:        \'", self.__work, "\'", tabs = ( kw_tabs + 1 ) )
      pfw.console.printf.info( "no_work:     \'", self.__no_work, "\'", tabs = ( kw_tabs + 1 ) )
      pfw.console.printf.info( "total:       \'", self.__total, "\'", tabs = ( kw_tabs + 1 ) )
   # def info

   def work( self ):
      return self.__work
   # def work

   def no_work( self ):
      return self.__no_work
   # def no_work

   def total( self ):
      return self.__total
   # def total

   def core( self ):
      return self.__core
   # def core



   __core         = None
   __user         = None
   __nice         = None
   __system       = None
   __idle         = None
   __iowait       = None
   __irq          = None
   __softirq      = None
   __steal        = None
   __guest        = None
   __guest_nice   = None
# class ProcStatCPU



def cpu_load( start: ProcStatCPU, end: ProcStatCPU ):
   if start.core( ) != end.core( ):
      pfw.console.debug.error( f"trying to calculate core load between two timestamp for different cores: '{start.core( )}' and '{end.core( )}'" )
   return ( end.work( ) - start.work( ) ) / ( end.total( ) - start.total( ) )
# def cpu_load
