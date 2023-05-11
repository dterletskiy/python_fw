import os
import requests

import pfw.console



def download( url: str, to: str ):
   file_name = url.split('/')[-1]

   request = requests.get( url, stream = True, allow_redirects = True )

   with open( os.path.join( to, file_name ), 'wb' ) as file:
      count: int = 0;
      for chunk in request.iter_content( chunk_size = 10 * 1024 * 1024 ):
         file.write( chunk )
         count += 1
         pfw.console.debug.trace( "downloaded: ", 10 * count, "MB" )

   return True
# def download
