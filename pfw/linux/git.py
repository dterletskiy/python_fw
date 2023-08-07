import os
import re

import pfw.base.struct
import pfw.console
import pfw.shell



g_patterns_2: dict = {
   "https": r"^https://(.+)/(.+)\.git$",
   "git": r"^git://(.+)/(.+)\.git$",
}

g_patterns_3: dict = {
   "https": r"^https://(.+)/(.+)/(.+)\.git$",
   "git": r"^git@(.+):(.+)/(.+)\.git$"
}

def build_structire( url ):
   for key in g_patterns_2:
      pattern = g_patterns_2[ key ]
      match = re.match( pattern, url )
      if not match:
         continue

      remote = match.group( 1 )
      user = ""
      name = match.group( 2 )
      return [ remote, user, name ]

   for key in g_patterns_3:
      pattern = g_patterns_3[ key ]
      match = re.match( pattern, url )
      if not match:
         continue

      remote = match.group( 1 )
      user = match.group( 2 )
      name = match.group( 3 )
      return [ remote, user, name ]
# def build_structire

class Repo:
   class DirectoryError( Exception ):
      def __init__( self, message ):
         self.message = message

      def __str__( self ):
         return self.message

   def __init__( self, **kwargs ):
      kw_url = kwargs.get( "url", None )
      kw_branch = kwargs.get( "branch", None )
      kw_directory = kwargs.get( "directory", None ) # if this parameter is set repo will be cloned directly to this directory
      kw_structure = kwargs.get( "structure", False ) # if this parameter is set to 'True' repo will be cloned to <directory>/<remote>/<user>/<name>
      kw_name = kwargs.get( "name", None )
      kw_depth = kwargs.get( "depth", None )

      self.__url = kw_url
      self.__branch = kw_branch
      self.__depth = kw_depth
      self.__name = kw_name
      self.__directory = os.path.join( kw_directory, "/".join( build_structire( kw_url ) ) ) if kw_structure else kw_directory

      pfw.shell.execute( f"mkdir -p {self.__directory}", output = pfw.shell.eOutput.PTY )
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
      tabulations: int = kwargs.get( "tabulations", 0 )
      kw_msg = kwargs.get( "msg", "" )
      pfw.console.debug.info( f"{kw_msg} (type {self.__class__.__name__}):", tabs = ( tabulations + 0 ) )
      pfw.console.debug.info( "url:          \'", self.__url, "\'", tabs = ( tabulations + 1 ) )
      pfw.console.debug.info( "branch:       \'", self.__branch, "\'", tabs = ( tabulations + 1 ) )
      pfw.console.debug.info( "depth:        \'", self.__depth, "\'", tabs = ( tabulations + 1 ) )
      pfw.console.debug.info( "directory:    \'", self.__directory, "\'", tabs = ( tabulations + 1 ) )
      pfw.console.debug.info( "name:         \'", self.__name, "\'", tabs = ( tabulations + 1 ) )
   # def info

   def url( self ):
      return self.__url
   # def url

   def branch( self ):
      return self.__branch
   # def branch

   def depth( self ):
      return self.__depth
   # def depth

   def directory( self ):
      return self.__directory
   # def directory

   def name( self ):
      return self.__name
   # def name

   def is_repo( self, **kwargs ):
      kw_directory: int = kwargs.get( "directory", self.__directory )

      if not os.path.exists( kw_directory ):
         return False
      if not os.path.isdir( kw_directory ):
         return False

      if not os.path.exists( os.path.join( kw_directory, ".git" ) ):
         return False

      # https://stackoverflow.com/a/16925062
      command = f"git rev-parse --is-inside-work-tree"

      result = pfw.shell.execute( command, output = pfw.shell.eOutput.PTY, cwd = kw_directory )
      return 0 == result["code"]
   # def is_repo

   def clone( self ):
      if self.is_repo( directory = self.__directory ):
         pfw.console.debug.error( f"directory '{self.__directory}' already contains git repository" )
         return False

      command = "git clone"
      command += f" --recursive"
      command += f" --depth {self.__depth}" if self.__depth not in [ None, 0 ] else ""
      command += f" --branch {self.__branch}" if None != self.__branch else ""
      command += f" {self.__url}"
      command += f" {self.__directory}"

      result = pfw.shell.execute( command, output = pfw.shell.eOutput.PTY, cwd = self.__directory )
      return 0 == result["code"]
   # def clone

   def remove( self ):
      command = f"rm -rf {self.__directory}"

      result = pfw.shell.execute( command, output = pfw.shell.eOutput.PTY, cwd = self.__directory )
      return 0 == result["code"]
   # def remove

   def pull( self ):
      command = "git pull"

      result = pfw.shell.execute( command, output = pfw.shell.eOutput.PTY, cwd = self.__directory )
      return 0 == result["code"]
   # def pull

   def push( self ):
      command = "git push"

      result = pfw.shell.execute( command, output = pfw.shell.eOutput.PTY, cwd = self.__directory )
      return 0 == result["code"]
   # def push

   def status( self ):
      command = "git status"

      result = pfw.shell.execute( command, output = pfw.shell.eOutput.PTY, cwd = self.__directory )
      return 0 == result["code"]
   # def status

   def log( self ):
      kw_count = kwargs.get( "count", None )
      kw_oneline = kwargs.get( "oneline", False )
      kw_stat = kwargs.get( "stat", False )
      kw_patch = kwargs.get( "patch", False )

      command = "git log"
      command += f" --max-count {kw_count}" if None != kw_count else ""
      command += f" --oneline {kw_oneline}" if None != kw_oneline else ""
      command += f" --stat {kw_stat}" if None != kw_stat else ""

      result = pfw.shell.execute( command, output = pfw.shell.eOutput.PTY, cwd = self.__directory )
      return 0 == result["code"]
   # def log

   __url: str = None
   __branch: str = None
   __depth: int = None
   __directory: str = None
   __name: str = None
# class Repo



class Collector:
   def __init__( self, **kwargs ):
      kw_directory = kwargs.get( "directory", None )
      kw_repo = kwargs.get( "repo", None )
      kw_repos = kwargs.get( "repos", None )
      kw_url = kwargs.get( "url", None )
      kw_urls = kwargs.get( "urls", None )

      self.__directory = kw_directory
      self.__repos = [ ]

      self.add( repo = kw_repo, repos = kw_repos, url = kw_url, urls = kw_urls )
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
      tabulations: int = kwargs.get( "tabulations", 0 )
      pfw.console.debug.info( self.__class__.__name__, ":", tabs = ( tabulations + 0 ) )
      pfw.console.debug.info( "name:         \'", self.__name, "\'", tabs = ( tabulations + 1 ) )
      for repo in self.__repos:
         repo.info( tabulations = tabulations + 1 )
   # def info

   def add_repo( self, repo: Repo ):
      for item in self.__repos:
         if item.directory( ) == repo.directory( ):
            pfw.console.debug.warning( "directory '%s' already used for repo '%s'" % ( repo.directory( ), item.url( ) ) )
            return False

      self.__repos.append( repo )
      return True
   # def add_repo

   def add_repos( self, repos: list ):
      result: bool = True
      for repo in repos:
         result &= self.add_repo( repo )

      return result
   # def add_repos

   def add_url( self, url: str ):
      if None == url:
         pfw.console.debug.error( "can't add url because it's 'None'" )
         return False

      if None == self.__directory:
         pfw.console.debug.error( "can't add url '%s' because of directory is not defined" % ( url ) )
         return False

      return self.add_repo( Repo( url = url, directory = self.__directory, structure = True ) )
   # def add_url

   def add_urls( self, urls: list ):
      if None == self.__directory:
         pfw.console.debug.error( "can't add urls '%s' because of directory is not defined" % ( urls ) )
         return False

      result: bool = True
      for url in urls:
         result &= self.add_url( url )

      return result
   # def add_urls

   def add( self, **kwargs ):
      kw_repo = kwargs.get( "repo", None )
      kw_repos = kwargs.get( "repos", None )
      kw_url = kwargs.get( "url", None )
      kw_urls = kwargs.get( "urls", None )

      result: bool = True

      if None != kw_repo:
         result &= self.add_repo( kw_repo )

      if None != kw_repos:
         result &= self.add_repos( kw_repos )

      if None != kw_url:
         result &= self.add_url( kw_url )

      if None != kw_urls:
         result &= self.add_urls( kw_urls )

      return result
   # def add

   def clone( self ):
      for repo in self.__repos:
         repo.clone( )
   # def clone

   def pull( self ):
      for repo in self.__repos:
         repo.pull( )
   # def pull

   def push( self ):
      for repo in self.__repos:
         repo.push( )
   # def push

   def status( self ):
      for repo in self.__repos:
         repo.status( )
   # def status

   __name: str = None
   __repos: list = [ ]
   __directory: str = None
# class Collector



def example( ):
   urls = [
      "git@github.com:dterletskiy/carpc.git",
      "git@github.com:dterletskiy/carpc-tutorial.git",
   ]

   repo_dir = "/mnt/dev/tmp/"
   repos = [
      pfw.linux.git.Repo(
            url = "git@github.com:dterletskiy/carpc-tutorial.git",
            directory = repo_dir,
            structure = True
         ),
      pfw.linux.git.Repo(
            url = "git@github.com:dterletskiy/carpc-examples.git",
            directory = repo_dir,
            structure = True
         ),
   ]
   repo_collector = pfw.linux.git.Collector( repos = repos, urls = urls, directory = repo_dir )
   repo_collector.info( )
# def example
