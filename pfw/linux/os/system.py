import pfw.console
import pfw.shell



def cores( ):
   result = pfw.shell.execute( "grep -c ^processor /proc/cpuinfo", output = pfw.shell.eOutput.PTY )["output"]
   if 0 == result["code"] and None != result["output"]:
      return int( result["output"] )

   return None
# def cores
