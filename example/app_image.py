#!/usr/bin/python



import os
import sys

pfw_path = None
for arg in sys.argv[1:]:
   if arg.startswith( "--pfw=" ):
      pfw_path = arg.split("=", 1)[1]
      sys.argv.remove( arg )
      break

if not pfw_path:
   print( "ERROR: Define path to 'pfw' as '--pfw=<path>'" )
   exit(1)

if not os.path.exists( pfw_path ):
   print( f"ERROR: {pfw_path} does not exist" )
   exit(1)

print( f"INFO: Path to 'pfw': {pfw_path}" )

sys.path.insert( 0, pfw_path )
try:
   import pfw.console
   print( f"INFO: 'pfw' import success" )
except ImportError:
   print( f"ERROR: 'pfw' import failed" )



import pfw.base.configuration

pfw.base.configuration.init( verbose = False )



import pfw.size
import pfw.linux.fs
import pfw.linux.image

def image_test( ):
   partition_0 = pfw.linux.image.Partition(
         size = pfw.size.Size( 1, pfw.size.Size.eGran.G ),
         fs = pfw.linux.fs.builder( "fat32" ),
         label = "ESP",
         bootable = True,
         esp = True
      )
   partition_1 = pfw.linux.image.Partition(
         size = pfw.size.Size( 1, pfw.size.Size.eGran.G ),
         fs = pfw.linux.fs.builder( "ext4" ),
         label = "system"
      )
   partition_2 = pfw.linux.image.Partition(
         size = pfw.size.Size( 1, pfw.size.Size.eGran.G ),
         fs = pfw.linux.fs.builder( "ext4" ),
         label = "data"
      )

   device = pfw.linux.image.Device(
         partitions = [
            partition_0,
            partition_1,
            partition_2
         ]
      )
   device.info( )

   image_file = "/mnt/dev/tmp/tmp.img"

   pfw.linux.image.create( image_file, pfw.size.Size( 5, pfw.size.Size.eGran.G ) )
   attached_to = pfw.linux.image.attach( image_file )
   attached_to_test = pfw.linux.image.attached_to( image_file )
   if attached_to != attached_to_test:
      pfw.console.debug.error( f"{attached_to} != {attached_to_test}" )
   pfw.console.debug.promt( )
   pfw.linux.image.detach( attached_to_test )

   # creating image
   pfw.linux.image.init_device( image_file, device )

   # cloning image
   cloned_device = pfw.linux.image.inspect( image_file )
   cloned_device.info( )
   pfw.linux.image.init_device( f"{image_file}_clone", cloned_device )



def main( ):
   image_test( )

if __name__ == "__main__":
   main( )
