import os
import re

import pfw.base
import pfw.console



def install( ):
   pfw.shell.execute( "apt update", sudo = True, output = pfw.shell.eOutput.PTY )
   pfw.shell.execute( "apt install -y ca-certificates curl gnupg lsb-release", sudo = True, output = pfw.shell.eOutput.PTY )

   DOCKER_URL = "https://download.docker.com/linux/ubuntu"
   DOCKER_GPG_KEY_URL = f"{DOCKER_URL}/gpg"
   KEYRING_FILE = "/usr/share/keyrings/docker-archive-keyring.gpg"

   command = f"if [ ! -f {KEYRING_FILE} ]; then curl -fsSL {DOCKER_GPG_KEY_URL} | sudo -S gpg --dearmor -o {KEYRING_FILE}; fi"
   pfw.shell.execute( command, output = pfw.shell.eOutput.PTY )

   target_string = f"deb [arch=$(dpkg --print-architecture) signed-by={KEYRING_FILE}] {DOCKER_URL} $(lsb_release -cs) stable"
   command = "echo \"" + target_string + "\" | sudo -S tee /etc/apt/sources.list.d/docker.list > /dev/null"
   pfw.shell.execute( command, output = pfw.shell.eOutput.PTY )

   pfw.shell.execute( "apt update", sudo = True, output = pfw.shell.eOutput.PTY )
   pfw.shell.execute( "apt install -y docker-ce docker-ce-cli containerd.io", sudo = True, output = pfw.shell.eOutput.PTY )
   pfw.shell.execute( "groupadd docker", sudo = True, output = pfw.shell.eOutput.PTY )
   pfw.shell.execute( "usermod -aG docker ${USER}", sudo = True, output = pfw.shell.eOutput.PTY )
# def install

def prune( ):
   pfw.shell.execute( "docker system prune --all --volumes", output = pfw.shell.eOutput.PTY )
# def prune

def commit( **kwargs ):
   kw_author = kwargs.get( "author", None )
   kw_message = kwargs.get( "message", None )
   kw_container = kwargs.get( "container", None )
   kw_image = kwargs.get( "image", None )
   kw_change = kwargs.get( "change", { } )
   # kw_change = kwargs.get( "change", { "USER": "root", "ENV": [ "PATH ~/.local/bin:\${PATH}" ] } )

   command: str = "docker commit"
   command += f" --author '{kw_author}'" if kw_author else ""
   command += f" --message '{kw_message}'" if kw_message else ""
   for key, value in kw_change.items( ):
      if "USER" == key:
         command += f" --change 'USER {value}'"
      elif "ENV" == key:
         if isinstance( value, list ) or isinstance( value, tuple ):
            for item in value:
               command += f" --change 'ENV {item}'"
         elif isinstance( value, str ):
            command += f" --change 'ENV {item}'"
      else:
         pfw.console.debug.warning( f"unsuported parameter '{key}' for --change" )
   command += f" {kw_container}"
   command += f" {kw_image}"
   pfw.shell.execute( command, output = pfw.shell.eOutput.PTY )
# def commit

def build( **kwargs ):
   kw_dokerfile = kwargs.get( "dokerfile", None )
   kw_image_name = kwargs.get( "image_name", None )
   kw_image_tag = kwargs.get( "image_tag", None )
   kw_build_args = kwargs.get( "build_args", [ ] )

   command: str = "docker build"
   command += " --no-cache=True"
   command += f" --file {kw_dokerfile}" if kw_dokerfile else ""
   command += f" --tag {kw_image_name}" if kw_image_name else ""
   command += f":{kw_image_tag}" if kw_image_name and kw_image_tag else ""
   for build_arg in kw_build_args:
      command += f" --build-arg {build_arg}" if build_arg else ""
   pfw.shell.execute( command, output = pfw.shell.eOutput.PTY )
# def build



class Container:

   class Mapping:
      def __init__( self, host: str, guest: str, **kwargs ):
         self.__host = host
         self.__guest = guest
      # def __init__

      def __del__( self ):
         pass
      # def __del__

      def __setattr__( self, attr, value ):
         attr_list = [ i for i in Container.Mapping.__dict__.keys( ) ]
         if attr in attr_list:
            self.__dict__[ attr ] = value
            return
         raise AttributeError
      # def __setattr__

      def __str__( self ):
         attr_list = [ i for i in Container.Mapping.__dict__.keys( ) if i[:2] != pfw.base.class_ignore_field ]
         vector = [ ]
         for attr in attr_list:
            vector.append( str( attr ) + " = " + str( self.__dict__.get( attr ) ) )
         name = "Container.Mapping { " + ", ".join( vector ) + " }"
         return name
      # def __str__

      def host( self ):
         return self.__host
      # def name

      def guest( self ):
         return self.__guest
      # def name



      __host: str = None
      __guest: str = None
   # class Mapping



   def __init__( self, **kwargs ):
      kw_name = kwargs.get( "name", None )
      kw_image = kwargs.get( "image", None )
      kw_hostname = kwargs.get( "hostname", None )
      kw_volume_mapping = kwargs.get( "volume_mapping", [ ] )
      kw_port_mapping = kwargs.get( "port_mapping", [ ] )
      kw_memory = kwargs.get( "memory", 4*1024*1024*1024 )
      kw_swap = kwargs.get( "swap", -1 )
      kw_cpus = kwargs.get( "cpus", None )
      kw_env = kwargs.get( "env", None )

      self.__name = kw_name
      self.__hostname = kw_hostname
      self.__image = kw_image
      self.__volume_mapping = kw_volume_mapping
      self.__port_mapping = kw_port_mapping

      result = self.is_exists( )
      if None != result:
         self.__image = result["image"]
   # def __init__

   def __del__( self ):
      pass
   # def __del__

   def __setattr__( self, attr, value ):
      attr_list = [ i for i in Container.__dict__.keys( ) ]
      if attr in attr_list:
         self.__dict__[ attr ] = value
         return
      raise AttributeError
   # def __setattr__

   def __str__( self ):
      attr_list = [ i for i in Container.__dict__.keys( ) if i[:2] != pfw.base.class_ignore_field ]
      vector = [ ]
      for attr in attr_list:
         vector.append( str( attr ) + " = " + str( self.__dict__.get( attr ) ) )
      name = "Container { " + ", ".join( vector ) + " }"
      return name
   # def __str__

   def info( self, **kwargs ):
      tabulations: int = kwargs.get( "tabulations", 0 )
      pfw.console.debug.info( self.__class__.__name__, ":", tabs = ( tabulations + 0 ) )
      pfw.console.debug.info( "name:         \'", self.__name, "\'", tabs = ( tabulations + 1 ) )
   # def info

   def is_exists( self, **kwargs ):
      kw_name = kwargs.get( "name", self.__name )

      if None != kw_name:
         command = f"docker ps -a -f name={kw_name}"
         result = pfw.shell.execute( command, output = pfw.shell.eOutput.PTY )
         output = result["output"].split( "\r\n" )
         if None != output:
            output_list = output[1].split( )
            if 0 < len( output_list ) and kw_name == output_list[-1]:
               pfw.console.debug.warning( "Container with name '%s' already exists with id '%s'" % (kw_name, output_list[0]) )
               return { "id": output_list[0], "image": output_list[1] }

      return None
   # def is_exists

   def name( self ):
      return self.__name
   # def name

   def pull( self, name: str, tag: str ):
      command: str = f"docker pull {name}"
      command += f":{tag}" if tag else ""
      result = pfw.shell.execute( command, output = pfw.shell.eOutput.PTY )

      return 0 == result["code"]
   # def pull

   def create( self ):
      if None != self.is_exists( ):
         return False

      command: str = f"docker create --name {self.__name} --hostname {self.__hostname} -it"
      for item in self.__volume_mapping:
         command += f" -v {item.host( )}:{item.guest( )}"
         pfw.shell.execute( f"mkdir -p {item.host( )}" )
      for item in self.__port_mapping:
         command += f" -p {item.host( )}:{item.guest( )}"
      command += f" {self.__image}"
      result = pfw.shell.execute( command, output = pfw.shell.eOutput.PTY )

      return 0 == result["code"]
   # def create

   def run( self ):
      kw_daemon = kwargs.get( "daemon", False )
      kw_disposable = kwargs.get( "disposable", False )

      if None != self.is_exists( ):
         return False

      command: str = f"docker run --name {self.__name} --hostname {self.__hostname} -it"
      command += " -d" if kw_daemon else ""
      command += " --rm" if kw_disposable else ""
      for item in self.__volume_mapping:
         command += f" -v {item.host( )}:{item.guest( )}"
         pfw.shell.execute( f"mkdir -p {item.host( )}" )
      for item in self.__port_mapping:
         command += f" -p {item.host( )}:{item.guest( )}"
      command += f" {self.__image}"
      result = pfw.shell.execute( command, output = pfw.shell.eOutput.PTY )

      return 0 == result["code"]
   # def run

   def start( self ):
      command: str = f"docker start {self.__name}"
      pfw.shell.execute( command, output = pfw.shell.eOutput.PTY )
   # def start

   def stop( self ):
      command: str = f"docker stop {self.__name}"
      pfw.shell.execute( command, output = pfw.shell.eOutput.PTY )
   # def stop

   def remove( self ):
      command: str = f"docker rm {self.__name}"
      pfw.shell.execute( command, output = pfw.shell.eOutput.PTY )
   # def remove

   def exec( self, cmd: str ):
      command: str = f"docker exec -it {self.__name} {cmd}"
      return pfw.shell.execute( command, output = pfw.shell.eOutput.PTY )
   # def exec

   def commit( self, **kwargs ):
      kwargs[ "container" ] = self.__name
      commit( **kwargs )
   # def commit

   def __add_volume_mapping( self, **kwargs ):
      kw_host = kwargs.get( "host", None )
      kw_guest = kwargs.get( "guest", None )
      kw_mapping = kwargs.get( "mapping", None )

      if None != kw_mapping and isinstance( kw_mapping, Container.Mapping ):
         self.__volume_mapping.append( kw_mapping )

      if (None, None) != (kw_host, kw_guest) and ( type( kw_host ) is str ) and ( type( kw_guest ) is str ):
         self.__volume_mapping.append( Container.Mapping( kw_host, kw_guest ) )

      if None != kw_mapping:
         self.__volume_mapping.extend( kw_mapping )
   # def __add_volume_mapping

   def __add_port_mapping( self, **kwargs ):
      kw_host = kwargs.get( "host", None )
      kw_guest = kwargs.get( "guest", None )
      kw_mapping = kwargs.get( "mapping", None )

      if None != kw_mapping and isinstance( kw_mapping, Container.Mapping ):
         self.__port_mapping.append( kw_mapping )

      if (None, None) != (kw_host, kw_guest) and ( type( kw_host ) is str ) and ( type( kw_guest ) is str ):
         self.__port_mapping.append( Container.Mapping( kw_host, kw_guest ) )

      if None != kw_mapping:
         self.__port_mapping.extend( kw_mapping )
   # def __add_port_mapping



   __name: str = None
   __image: str = None
   __hostname: str = None
   __volume_mapping: list = None 
   __port_mapping: list = None 
# class Container
