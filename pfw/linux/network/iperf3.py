import pfw.console
import pfw.shell



def server( **kwargs ):
   kw_bind = kwargs.get( "bind", None )
   kw_port = kwargs.get( "port", None )
   kw_affinity = kwargs.get( "affinity", None )
   kw_interval = kwargs.get( "interval", None )
   kw_daemon = kwargs.get( "daemon", False )
   kw_one_off = kwargs.get( "one_off", False )
   kw_verbose = kwargs.get( "verbose", False )
   kw_json = kwargs.get( "json", False )
   kw_namespace = kwargs.get( "namespace", None )

   kwargs[ "output" ] = kwargs.get( "output", pfw.shell.eOutput.PTY )

   command = ""
   command += f"ip netns exec {kw_namespace}" if None != kw_namespace else ""
   command += f" iperf3 -s"
   command += f" -p {kw_port}" if None != kw_port else ""
   command += f" -B {kw_bind}" if None != kw_bind else ""
   command += f" -A {kw_affinity}" if None != kw_affinity else ""
   command += f" -D" if kw_daemon else ""
   command += f" -V" if kw_verbose else ""
   command += f" -J" if kw_json else ""
   command += f" -1" if kw_one_off else ""
   command += f" -i {kw_interval}" if None != kw_interval else ""
   command += f" --forceflush"

   return pfw.shell.execute2( command, **kwargs )
# def server

def client( ip, **kwargs ):
   kw_bind = kwargs.get( "bind", None )
   kw_port = kwargs.get( "port", None )
   kw_affinity = kwargs.get( "affinity", None )
   kw_interval = kwargs.get( "interval", None )
   kw_time = kwargs.get( "time", None )
   kw_bytes = kwargs.get( "bytes", None )
   kw_length = kwargs.get( "length", None )
   kw_udp = kwargs.get( "udp", False )
   kw_title = kwargs.get( "title", None )
   kw_bitrate = kwargs.get( "bitrate", None )
   kw_omit = kwargs.get( "omit", None )
   kw_reverse = kwargs.get( "reverse", False )
   kw_bidir = kwargs.get( "bidir", False )
   kw_verbose = kwargs.get( "verbose", False )
   kw_timestamp = kwargs.get( "timestamp", False )
   kw_json = kwargs.get( "json", False )
   kw_namespace = kwargs.get( "namespace", None )

   kwargs[ "output" ] = kwargs.get( "output", pfw.shell.eOutput.PTY )

   command = ""
   command += f"ip netns exec {kw_namespace}" if None != kw_namespace else ""
   command += f" iperf3 -c {ip}"
   command += f" -p {kw_port}" if None != kw_port else ""
   command += f" -B {kw_bind}" if None != kw_bind else ""
   command += f" -A {kw_affinity}" if None != kw_affinity else ""
   command += f" -i {kw_interval}" if None != kw_interval else ""
   command += f" -t {kw_time}" if None != kw_time else ""
   command += f" -n {kw_bytes}" if None != kw_bytes else ""
   command += f" -l {kw_length}" if None != kw_length else ""
   command += f" -b {kw_bitrate}" if None != kw_bitrate else ""
   command += f" -T {kw_title}" if None != kw_title else ""
   command += f" -R" if kw_reverse else ""
   command += f" --bidir" if kw_bidir else ""
   command += f" --timestamps" if kw_timestamp else ""
   command += f" -O {kw_omit}" if kw_omit else ""
   command += f" -u" if kw_udp else ""
   command += f" -V" if kw_verbose else ""
   command += f" -J" if kw_json else ""
   command += f" --forceflush"

   return pfw.shell.execute2( command, **kwargs )
# def client
