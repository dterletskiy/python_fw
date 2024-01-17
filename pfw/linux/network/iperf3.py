import pfw.console
import pfw.shell



def server( **kwargs ):
   kw_bind = kwargs.get( "bind", None )
   kw_port = kwargs.get( "port", None )
   kw_interval = kwargs.get( "interval", None )
   kw_daemon = kwargs.get( "daemon", False )
   kw_one_off = kwargs.get( "one_off", False )
   kw_verbose = kwargs.get( "verbose", False )
   kw_json = kwargs.get( "json", False )
   kw_namespace = kwargs.get( "namespace", None )

   kwargs[ "output" ] = kwargs.get( "output", pfw.shell.eOutput.PTY )

   command = ""
   command += f"ip netns exec {kw_namespace}" if kw_namespace else ""
   command += f" iperf3 -s"
   command += f" -p {kw_port}" if kw_port else ""
   command += f" -B {kw_bind}" if kw_bind else ""
   command += f" -D" if kw_daemon else ""
   command += f" -V" if kw_verbose else ""
   command += f" -J" if kw_json else ""
   command += f" -1" if kw_one_off else ""
   command += f" -i {kw_interval}" if kw_interval else ""

   return pfw.shell.execute( command, **kwargs )
# def server

def client( ip, **kwargs ):
   kw_bind = kwargs.get( "bind", None )
   kw_port = kwargs.get( "port", None )
   kw_interval = kwargs.get( "interval", None )
   kw_time = kwargs.get( "time", None )
   kw_bytes = kwargs.get( "bytes", None )
   kw_length = kwargs.get( "length", None )
   kw_udp = kwargs.get( "udp", False )
   kw_title = kwargs.get( "title", None )
   kw_verbose = kwargs.get( "verbose", False )
   kw_json = kwargs.get( "json", False )
   kw_namespace = kwargs.get( "namespace", None )

   kwargs[ "output" ] = kwargs.get( "output", pfw.shell.eOutput.PTY )

   command = ""
   command += f"ip netns exec {kw_namespace}" if kw_namespace else ""
   command += f" iperf3 -c {ip}"
   command += f" -p {kw_port}" if kw_port else ""
   command += f" -B {kw_bind}" if kw_bind else ""
   command += f" -i {kw_interval}" if kw_interval else ""
   command += f" -t {kw_time}" if kw_time else ""
   command += f" -n {kw_bytes}" if kw_bytes else ""
   command += f" -l {kw_length}" if kw_length else ""
   command += f" -T {kw_title}" if kw_title else ""
   command += f" -u" if kw_udp else ""
   command += f" -V" if kw_verbose else ""
   command += f" -J" if kw_json else ""

   return pfw.shell.execute( command, **kwargs )
# def client
