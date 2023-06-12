import os
import re

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
