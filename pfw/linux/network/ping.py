import pfw.console
import pfw.shell



def ping( ip: str, **kwargs ):
   kw_interval = kwargs.get( "interval", None )
   kw_count = kwargs.get( "count", None )
   kw_namespace = kwargs.get( "namespace", None )
   kw_interface = kwargs.get( "interface", None )

   kwargs[ "output" ] = kwargs.get( "output", pfw.shell.eOutput.PTY )

   command = ""
   command += f"ip netns exec {kw_namespace}" if None != kw_namespace else ""
   command += " ping"
   command += f" -i {kw_interval}" if None != kw_interval else ""
   command += f" -c {kw_count}" if None != kw_count else ""
   command += f" -I {kw_interface}" if None != kw_interface else ""
   command += f" {ip}"
   return pfw.shell.execute( command, **kwargs )
# def ping
