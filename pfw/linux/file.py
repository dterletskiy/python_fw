import pfw.console
import pfw.shell



def size( path: str, sudo: bool = False ):
   # @TDA: To implement lates in general implementation.
   # Fake command to execute it with 'root' to avoid password promt string in next command what will go to result
   if sudo:
      pfw.shell.execute( f"pwd", sudo = sudo, output = pfw.shell.eOutput.PTY, print = False, collect = False )

   result = pfw.shell.execute( f"du -hsb {path}", sudo = sudo, output = pfw.shell.eOutput.PTY )
   if 0 != result["code"]:
      return None

   return int( result["output"].split( )[ 0 ] )
# def file_size

def mktemp( **kwargs ):
   kw_location = kwargs.get( "location", None )
   kw_directory = kwargs.get( "directory", False )
   kw_template = kwargs.get( "template", None )

   command: str = "mktemp"
   command += f" --directory" if kw_directory else ""
   command += f" --tmpdir={kw_location}" if kw_location else ""
   command += f" {kw_template}" if kw_template else ""
   result = pfw.shell.execute( command, output = pfw.shell.eOutput.PTY )

   if 0 != result["code"]:
      pfw.console.debug.error( "Unable to create temporary file/directory" )
      return None

   file = result["output"].split( "\r\n" )[0]
   return file
# def mktemp
