import git
from git import RemoteProgress
from tqdm import tqdm

import base.console

ignore_field = "__"



class CloneProgress( RemoteProgress ):
   def __init__( self ):
      super( ).__init__( )
      self.pbar = tqdm( )

   def updat( self, op_code, cur_count, max_count=None, message='' ):
      self.updat1( op_code, cur_count, max_count, message )

   def updat1( self, op_code, cur_count, max_count=None, message='' ):
      if message:
         base.console.debug.info( message )

   def updat2( self, op_code, cur_count, max_count=None, message='' ):
      if message:
         base.console.debug.info( 'update(%s, %s, %s, %s)' % (op_code, cur_count, max_count, message) )

   def updat3( self, op_code, cur_count, max_count=None, message='' ):
      base.console.debug.info( op_code, cur_count, max_count, cur_count / (max_count or 100.0), message or "NO MESSAGE" )

   def update4( self, op_code, cur_count, max_count=None, message='' ):
      self.pbar.total = max_count
      self.pbar.n = cur_count
      self.pbar.refresh( )

   def update5( self, op_code, cur_count, max_count=None, message='' ):
      pbar = tqdm( total=max_count )
      pbar.update( cur_count )
# class CloneProgress








# import os
# import sys
# import datetime
# import shutil
# import errno
# import ntpath

# import base.console
# import base.file



# project_path: str = "/home/scorpion/Source/RPC/"
# git: str = "cd " + project_path + "; git "
# archive_path: str = "/home/scorpion/Source/RPC_Archive/"
# exceptions: list = [ ".git", "git.py", "base.py", "console.py", "__pycache__" ]



# archive_directories: list = [ ]
# for archive in os.listdir( archive_path ):
#    archive_directories.append( os.path.join( archive_path, archive ) )
# archive_directories.sort( )
# base.console.debug.info( "root: ", archive_directories )


# os.system( git + "init" )
# os.system( git + "commit --allow-empty -m 'Initial commit'" )
# for archive_directory in archive_directories:
#    base.console.debug.info( "---------- Processing: ", archive_directory, " ----------" )
#    base.file.clean_dir( project_path, exceptions )
#    base.file.copy_recursively( archive_directory, project_path )
#    os.system( git + "add ." )
#    os.system( git + "status" )
#    os.system( git + "commit -m 'version " + ntpath.basename( archive_directory ) + "'" )
#    os.system( git + "status" )
