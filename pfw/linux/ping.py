import beepy
import re

import pfw.base
import pfw.console
import pfw.shell




error_count: int = 0
def processor( line: str ):
   global error_count

   match = re.match( rf"(\d+) bytes from (.+): icmp_seq=(\d+) ttl=(\d+) time=(\d+)\.?(\d*) ms", line )
   if match:
      error_count = 0
   else:
      pfw.console.debug.error( line )
      error_count += 1
      if 4 < error_count:
         # 1 : 'coin'
         # 2 : 'robot_error'
         # 3 : 'error'
         # 4 : 'ping'
         # 5 : 'ready'
         # 6 : 'success'
         # 7 : 'wilhelm'
         beepy.beep( sound = 3 )
# def processor

def ping( **kwargs ):
   kw_destination = kwargs.get( "destination", "8.8.8.8" )
   kw_interval = kwargs.get( "interval", None )
   kw_count = kwargs.get( "count", None )
   kw_processor = kwargs.get( "processor", None )

   command = "ping"
   command += f" -i {kw_interval}" if kw_interval else ""
   command += f" -c {kw_count}" if kw_count else ""
   command += f" {kw_destination}"
   pfw.shell.execute( command, processor = kw_processor )
# def ping
