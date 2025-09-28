import os
import re
import json

import pfw.console
import pfw.shell



def build( **kwargs ):
   kw_dokerfile = kwargs.get( "dokerfile", None )
   kw_image_name = kwargs.get( "image_name", None )
   kw_image_tag = kwargs.get( "image_tag", None )
   kw_build_args = kwargs.get( "build_args", [ ] )

   command: str = "docker build"
   command += f" --no-cache=True"
   command += f" --progress=plain"
   command += f" --file {kw_dokerfile}" if kw_dokerfile else ""
   command += f" --tag {kw_image_name}" if kw_image_name else ""
   command += f":{kw_image_tag}" if kw_image_name and kw_image_tag else ""
   for build_arg in kw_build_args:
      command += f" --build-arg {build_arg}" if build_arg else ""
   command += f" ."
   result = pfw.shell.execute( command, output = pfw.shell.eOutput.PTY )

   return 0 == result["code"]
# def build

def pull( image_name: str, tag: str, **kwargs ):
   kw_image_tag = kwargs.get( "image_tag", None )

   command: str = f"docker pull"
   command += f" {image_name}"
   command += f":{kw_image_tag}" if kw_image_tag else ""
   result = pfw.shell.execute( command, output = pfw.shell.eOutput.PTY )

   return 0 == result["code"]
# def pull

def rmi( image_name: str, *kwargs ):
   kw_image_tag = kwargs.get( "image_tag", None )

   command: str = "docker rmi"
   command += f" {image_name}"
   command += f":{kw_image_tag}" if kw_image_tag else ""
   result = pfw.shell.execute( command, output = pfw.shell.eOutput.PTY )

   return 0 == result["code"]
# def rmi

def info( **kwargs ):
   kw_image_name = kwargs.get( "name", None )

   if not kw_image_name:
      return None

   parts = kw_image_name.split( ":", 1 )
   image_name = parts[0]
   image_tag = parts[1] if len( parts ) > 1 else None

   command = f"docker images --format json"
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

      if image_name == data.get( "Repository" ):
         if image_tag:
            if image_tag == data.get( "Tag" ):
               return data
            else:
               return None
         return data

   return None
# def test

def is_exists( image_name: str, **kwargs ):
   """
   This function tests if image with 'image_name' exists in the system.
   'image_name' containes from 'name' and optionally from ':tag'.
   Examples:
      linux.docker.image.is_exists( "u20" )
      linux.docker.image.is_exists( "u20:latest" )
   """
   return None != info( name = image_name )
# def is_exists
