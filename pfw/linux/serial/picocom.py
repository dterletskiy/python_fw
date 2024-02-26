import pfw.console
import pfw.shell



def send( command: str, device: str, **kwargs ):
   kw_baudrate = kwargs.get( "baudrate", None )

   kwargs[ "output" ] = kwargs.get( "output", pfw.shell.eOutput.PTY )

   shell_command = "picocom -qrX"
   shell_command += f" -b {kw_baudrate}" if kw_baudrate else ""
   shell_command += f" {device}"
   shell_command += f"; echo '{command}' | picocom -qrix 1000 {device}"

   return pfw.shell.execute( shell_command, **kwargs )
# def ping
