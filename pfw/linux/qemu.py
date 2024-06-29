#!/usr/bin/python3

import os
import datetime

import pfw.console
import pfw.shell
import pfw.linux.dt



EMULATOR: str = ""

# Function to set default path to the emulator.
# This path will be used for futher qemu calls in case if
# another path won't be defined.
def init( qemu_path: str ):
   global EMULATOR
   EMULATOR = qemu_path
# def init

# This function return full path to the emulator
def qemu( emulator: str, **kwargs ):
   kw_qemu_path = kwargs.get( "qemu_path", None )

   kw_qemu_path = kw_qemu_path if kw_qemu_path else EMULATOR

   return os.path.join( kw_qemu_path, emulator )
# def qemu

def run( parameters, **kwargs ):
   kw_emulator = kwargs.get( "emulator", None )
   kw_bios = kwargs.get( "bios", None )
   kw_kernel = kwargs.get( "kernel", None )
   kw_initrd = kwargs.get( "initrd", None )
   kw_append = kwargs.get( "append", None )
   kw_dtb = kwargs.get( "dtb", None )
   kw_cwd = kwargs.get( "cwd", None )
   kw_arch = kwargs.get( "arch", None )
   kw_gdb = kwargs.get( "gdb", False )
   kw_dump_dtb = kwargs.get( "dump_dtb", False )
   kw_dump_dtb_path = kwargs.get( "dump_dtb_path", f"/tmp/dtb/{str(datetime.datetime.now( ))}.dtb" )
   kw_output = kwargs.get( "output", pfw.shell.eOutput.PTY )

   if kw_dump_dtb:
      pfw.shell.execute( f"mkdir -p {os.path.dirname( kw_dump_dtb_path )}", output = kw_output )

   if "x86" == kw_arch:
      kw_emulator = qemu( f"qemu-system-x86_64", qemu_path = kw_emulator )
   elif "x86_64" == kw_arch:
      kw_emulator = qemu( f"qemu-system-x86_64", qemu_path = kw_emulator )
   elif "arm" == kw_arch or "arm32" == kw_arch:
      kw_emulator = qemu( f"qemu-system-arm", qemu_path = kw_emulator )
   elif "arm64" == kw_arch or "aarch64" == kw_arch:
      kw_emulator = qemu( f"qemu-system-aarch64", qemu_path = kw_emulator )

   command: str = f"{kw_emulator} {parameters}"
   command += f" -bios {kw_bios}" if kw_bios else ""
   command += f" -kernel {kw_kernel}" if kw_kernel else ""
   command += f" -initrd {kw_initrd}" if kw_initrd else ""
   command += f" -append \"{kw_append}\"" if kw_append else ""
   command += f" -dtb {kw_dtb}" if kw_dtb else ""
   command += f" -machine dumpdtb={kw_dump_dtb_path}" if kw_dump_dtb else ""
   command += f" -s -S" if kw_gdb else ""

   result = pfw.shell.execute( command, cwd = kw_cwd, sudo = False, output = kw_output )

   if True == kw_dump_dtb:
      pfw.linux.dt.decompile( kw_dump_dtb_path, kw_dump_dtb_path + ".dts" )

   return result["code"]
# def run
