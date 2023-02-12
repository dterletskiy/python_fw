import pfw.console
import pfw.shell



def is_running( name: str ):
   result = pfw.shell.execute( f"pgrep -x {name}", output = pfw.shell.eOutput.PTY )
   if 0 == result["code"] and None != result["output"]:
      return int( result["output"] )

   return None
# def is_running

def kill( name: str ):
   pid = is_running( name )
   if None != pid:
      pfw.shell.execute( f"kill -9 {str( pid )}", sudo = True, output = pfw.shell.eOutput.PTY )

   return None
# def kill

def kill_all( name: str ):
   pfw.shell.execute( f"killall {name}", sudo = True, output = pfw.shell.eOutput.PTY )
# def kill_all
