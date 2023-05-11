import os

import pfw.base.struct
import pfw.base.net
import pfw.console
import pfw.shell



REPO_TOOL_URL = "https://storage.googleapis.com/git-repo-downloads/repo"



class Repo:
   def __init__( self, destination: str, **kwargs ):
      kw_tool_url = kwargs.get( "tool_url", REPO_TOOL_URL )
      kw_manifest_url = kwargs.get( "manifest_url", None )
      kw_manifest_name = kwargs.get( "manifest_name", None )
      kw_manifest_branch = kwargs.get( "manifest_branch", None )
      kw_manifest_depth = kwargs.get( "manifest_depth", None )
      kw_depth = kwargs.get( "depth", None )

      pfw.shell.execute( f"mkdir -p {destination}", output = pfw.shell.eOutput.PTY )

      self.__tool_url = kw_tool_url
      self.__tool = os.path.join( destination, "repo" )
      self.__source_dir = destination
      self.__manifest_url = kw_manifest_url
      self.__manifest_name = kw_manifest_name
      self.__manifest_branch = kw_manifest_branch
      self.__manifest_depth = kw_manifest_depth
      self.__depth = kw_depth
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

   def info( self, **kwargs ):
      kw_tabs = kwargs.get( "tabs", 0 )
      kw_msg = kwargs.get( "msg", "" )
      pfw.console.debug.info( f"{kw_msg} (type {self.__class__.__name__}):", tabs = ( kw_tabs + 0 ) )

      pfw.console.debug.info( "tool url:          \'", self.__tool_url, "\'", tabs = ( tabulations + 1 ) )
      pfw.console.debug.info( "tool:              \'", self.__tool, "\'", tabs = ( tabulations + 1 ) )
      pfw.console.debug.info( "source dir:        \'", self.__source_dir, "\'", tabs = ( tabulations + 1 ) )
      pfw.console.debug.info( "branch:            \'", self.__branch, "\'", tabs = ( tabulations + 1 ) )

      if None == self.__source_dir:
         return

      # https://stackoverflow.com/questions/14402425/how-do-i-know-the-current-version-in-an-android-repo
      manifest_git_path = os.path.join( self.__source_dir, ".repo/manifests.git" )
      pfw.shell.execute( f"git --git-dir {manifest_git_path} log default" )
      pfw.shell.execute( f"git --git-dir {manifest_git_path} tag" )
      pfw.shell.execute( f"git --git-dir {manifest_git_path} branch -a" )

      command: str = f"{self.__tool} --trace --time forall"
      command += " -c \"git rev-parse --show-toplevel && git rev-parse HEAD\""
      pfw.shell.execute( command, cwd = self.__source_dir, output = pfw.shell.eOutput.PTY )
   # def info

   def install( self ):
      result = pfw.base.net.download( self.__tool_url, self.__source_dir )
      if 0 != result["code"]:
         return False

      result = pfw.shell.execute( f"chmod a+x {self.__tool}" )
      return 0 == result["code"]
   # def install

   def init( self, **kwargs ):
      command: str = f"{self.__tool} --trace --time init"
      command += f" --manifest-url={self.__manifest_url}"
      command += f" --manifest-name={self.__manifest_name}" if self.__manifest_name else ""
      command += f" --manifest-branch={self.__manifest_branch}" if self.__manifest_branch else ""
      command += f" --manifest-depth={self.__manifest_depth}" if self.__manifest_depth else ""
      command += f" --depth={self.__depth}" if self.__depth else ""
      result = pfw.shell.execute( command, cwd = self.__source_dir, output = pfw.shell.eOutput.PTY )

      return 0 == result["code"]
   # def init

   def sync( self ):
      command: str = f"{self.__tool} --trace --time sync"
      command += f" --current-branch"
      command += f" --no-clone-bundle"
      command += f" --no-tags"
      result = pfw.shell.execute( command, cwd = self.__source_dir, output = pfw.shell.eOutput.PTY )

      return 0 == result["code"]
   # def sync

   def status( self ):
      command: str = f"{self.__tool} --trace --time status"
      result = pfw.shell.execute( command, cwd = self.__source_dir, output = pfw.shell.eOutput.PTY )

      return 0 == result["code"]
   # def status

   def revert( self ):
      command: str = f"{self.__tool} --trace --time forall"
      command += f" -vc \"git reset --hard\""
      result = pfw.shell.execute( command, cwd = self.__source_dir )

      return 0 == result["code"]
   # def revert



   __tool_url: str = REPO_TOOL_URL
   __tool: str = None
   __source_dir: str = None
   __depth: str = None
   __manifest_url: str = None
   __manifest_name: str = None
   __manifest_branch: str = None
   __manifest_depth: str = None
# class Repo
