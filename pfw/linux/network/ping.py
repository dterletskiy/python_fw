import pfw.console
import pfw.shell



def ping( **kwargs ):
   kw_ip = kwargs.get( "ip", "8.8.8.8" )
   kw_interval = kwargs.get( "interval", None )
   kw_count = kwargs.get( "count", None )
   kw_namespace = kwargs.get( "namespace", None )

   kwargs[ "output" ] = kwargs.get( "output", pfw.shell.eOutput.PTY )
   kwargs[ "sudo" ] = None != kw_namespace or kwargs.get( "sudo", False )

   command = ""
   command += f"ip netns exec {kw_namespace}" if kw_namespace else ""
   command += " ping"
   command += f" -i {kw_interval}" if kw_interval else ""
   command += f" -c {kw_count}" if kw_count else ""
   command += f" {kw_ip}"
   return pfw.shell.execute( command, **kwargs )
# def ping
