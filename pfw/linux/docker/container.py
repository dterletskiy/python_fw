import os
import re
import json

import pfw.base.struct
import pfw.console
import pfw.shell
import pfw.os.environment



class Mapping:
   def __init__( self, host: str, guest: str, **kwargs ):
      self.__host = host
      self.__guest = guest
   # def __init__

   def __del__( self ):
      pass
   # def __del__

   def __setattr__( self, attr, value ):
      attr_list = [ i for i in self.__class__.__dict__.keys( ) ]
      if attr in attr_list:
         self.__dict__[ attr ] = value
         return
      raise AttributeError
   # def __setattr__

   def __str__( self ):
      attr_list = [ i for i in self.__class__.__dict__.keys( ) if i[:2] != pfw.base.struct.ignore_field ]
      vector = [ f"{str( attr )} = {str( self.__dict__.get( attr ) )}" for attr in attr_list ]
      return self.__class__.__name__ + " { " + ", ".join( vector ) + " }"
   # def __str__

   def host( self ):
      return self.__host
   # def name

   def guest( self ):
      return self.__guest
   # def name

   def as_string( self, delimiter = ":" ):
      return f"{self.__host}{delimiter}{self.__guest}"
   # def as_string



   __host: str = None
   __guest: str = None
# class Mapping

def commit( container_name: str, **kwargs ):
   kw_author = kwargs.get( "author", None )
   kw_message = kwargs.get( "message", None )
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
   command += f" {container_name}"
   command += f" {kw_image}"
   result = pfw.shell.execute( command, output = pfw.shell.eOutput.PTY )

   return 0 == result["code"]
# def commit

def info( **kwargs ):
   kw_container_name = kwargs.get( "name", None )

   if not kw_container_name:
      return None

   command = f"docker ps --all --format json"
   result = pfw.shell.execute( command, output = pfw.shell.eOutput.PTY )
   output_list = result["output"].split( "\r\n" )

   for item in output_list:
      try:
         data = json.loads( item )
      except json.JSONDecodeError as e:
         # pfw.console.debug.error( "JSON format error:" )
         # pfw.console.debug.error( "   Message:", e.msg )
         # pfw.console.debug.error( "   Position:", e.pos )
         continue

      if kw_container_name == data.get( "Names" ):
         return data

   return None
# def info

def test( container_name: str, **kwargs ):
   kw_test = kwargs.get( "test", "exists" )

   if kw_test not in [ "exists", "started" ]:
      return None

   if not container_name:
      return None

   command = f"docker ps "
   if "exists" == kw_test:
      command += f" --all"
   command += f" --filter name={container_name}"
   result = pfw.shell.execute( command, output = pfw.shell.eOutput.PTY )
   output = result["output"].split( "\r\n" )
   if not output:
      return None

   output_list = output[1].split( )
   if 0 >= len( output_list ) or container_name != output_list[-1]:
      return None

   pfw.console.debug.info( "Container with name '%s' already exists with id '%s'" % (container_name, output_list[0]) )
   return { "id": output_list[0], "image": output_list[1] }
# def test

def is_exists( container_name: str, **kwargs ):
   """
   This function tests if container with 'container_name' exists in the system.
   Examples:
      linux.docker.container.is_exists( "u20" )
   """
   return None != info( name = container_name )
# def is_exists

def is_started( container_name: str, **kwargs ):
   """
   This function tests if container with 'container_name' is running in the system.
   Examples:
      linux.docker.container.is_started( "u20" )
   """
   if data := info( name = container_name ):
      return data.get( "State", "none" ) == "running"

   return False
# def is_started

def create( container_name: str, image_name: str, **kwargs ):
   kw_image_tag = kwargs.get( "image_tag", None )
   kw_hostname = kwargs.get( "hostname", "hostname" )
   kw_workdir = kwargs.get( "workdir", None )
   kw_volume_mapping = kwargs.get( "volume_mapping", [ ] )
   kw_port_mapping = kwargs.get( "port_mapping", [ ] )
   kw_env = kwargs.get( "env", [ ] )
   kw_disposable = kwargs.get( "disposable", False )

   if is_exists( container_name ):
      pfw.console.debug.error( f"Container with name '{container_name}' already exists" )
      return False

   command: str = f"docker create"
   command += f" --interactive"
   command += f" --tty"
   command += f" --name {container_name}"
   command += f" --hostname {kw_hostname}"
   command += f" --rm" if kw_disposable else ""
   command += f" --workdir {kw_workdir}" if kw_workdir else ""
   # Fix terminal's window size in container
   # https://stackoverflow.com/a/50617797
   # https://github.com/moby/moby/issues/33794#issuecomment-312873988
   command += " --env COLUMNS=\"`tput cols`\" --env LINES=\"`tput lines`\""
   for env in kw_env:
      if isinstance( env, pfw.os.environment.Environment ):
         command += f" --env {env.as_string( )}"
   for item in kw_volume_mapping:
      if isinstance( item, Mapping ):
         command += f" --volume {item.as_string( )}"
   for item in kw_port_mapping:
      if isinstance( item, Mapping ):
         command += f" --publish {item.as_string( )}"
   command += f" {image_name}:{kw_image_tag}" if kw_image_tag else f" {image_name}"
   result = pfw.shell.execute( command, output = pfw.shell.eOutput.PTY )

   return 0 == result["code"]
# def create

def remove( container_name: str, **kwargs ):
   command: str = f"docker rm {container_name}"
   pfw.shell.execute( command, output = pfw.shell.eOutput.PTY )
# def remove

def start( container_name: str, **kwargs ):
   command: str = f"docker start {container_name}"
   pfw.shell.execute( command, output = pfw.shell.eOutput.PTY )
# def start

def stop( container_name: str, **kwargs ):
   command: str = f"docker stop {container_name}"
   pfw.shell.execute( command, output = pfw.shell.eOutput.PTY )
# def stop

def run( container_name: str, image_name: str, **kwargs ):
   kw_image_tag = kwargs.get( "image_tag", None )
   kw_hostname = kwargs.get( "hostname", "hostname" )
   kw_workdir = kwargs.get( "workdir", None )
   kw_volume_mapping = kwargs.get( "volume_mapping", [ ] )
   kw_port_mapping = kwargs.get( "port_mapping", [ ] )
   kw_env = kwargs.get( "env", [ ] )
   kw_disposable = kwargs.get( "disposable", False )
   kw_daemon = kwargs.get( "daemon", False )
   kw_command = kwargs.get( "command", None )

   if is_exists( container_name ):
      pfw.console.debug.error( f"Container with name '{container_name}' already exists" )
      return False

   command: str = f"docker run"
   command += f" --interactive"
   command += f" --tty"
   command += f" --name {container_name}"
   command += f" --hostname {kw_hostname}"
   command += f" --rm" if kw_disposable else ""
   command += f" --workdir {kw_workdir}" if kw_workdir else ""
   # Fix terminal's window size in container
   # https://stackoverflow.com/a/50617797
   # https://github.com/moby/moby/issues/33794#issuecomment-312873988
   command += " --env COLUMNS=\"`tput cols`\" --env LINES=\"`tput lines`\""
   for env in kw_env:
      if isinstance( env, pfw.os.environment.Environment ):
         command += f" --env {env.as_string( )}"
   for item in kw_volume_mapping:
      if isinstance( item, Mapping ):
         command += f" --volume {item.as_string( )}"
   for item in kw_port_mapping:
      if isinstance( item, Mapping ):
         command += f" --publish {item.as_string( )}"
   command += f" --detach" if kw_daemon else ""
   command += f" {image_name}:{kw_image_tag}" if kw_image_tag else f" {image_name}"
   command += f" {kw_command}" if kw_command else ""
   result = pfw.shell.execute( command, output = pfw.shell.eOutput.PTY )

   return 0 == result["code"]
# def run

def exec( container_name: str, **kwargs ):
   kw_command = kwargs.get( "command", None )
   kw_workdir = kwargs.get( "workdir", None )

   command: str = f"docker exec"
   command += f" --interactive"
   command += f" --tty"
   command += f" --workdir {kw_workdir}" if kw_workdir else ""
   command += f" {container_name}"
   command += f" {kw_command}" if kw_command else ""
   return pfw.shell.execute( command, output = pfw.shell.eOutput.PTY )
# def exec
