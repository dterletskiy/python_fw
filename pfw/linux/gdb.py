#!/usr/bin/python3

import pfw.console
import pfw.shell



def run( **kwargs ):
   kw_ip = kwargs.get( "ip", "localhost" )
   kw_port = kwargs.get( "port", 1234 )
   kw_arch = kwargs.get( "arch", None )
   kw_file = kwargs.get( "file", None )
   kw_lib_path = kwargs.get( "lib_path", None )
   kw_src_path = kwargs.get( "src_path", None )
   kw_load_symbols = kwargs.get( "load_symbols", None ) # { str: [ ] }
   kw_break_names = kwargs.get( "break_names", None ) # [ ]
   kw_break_addresses = kwargs.get( "break_addresses", None ) # [ ]
   kw_break_code = kwargs.get( "break_code", None ) # { str: [ ] }
   kw_ex_list = kwargs.get( "ex_list", [ ] )

   command = f"gdb-multiarch"
   command += f" -q"
   command += f" --nh"
   command += f" -tui"

   # command += f" -ex \"layout split\""
   # command += f" -ex \"layout asm\""
   command += f" -ex \"layout regs\""
   command += f" -ex \"set disassemble-next-line on\""
   command += f" -ex \"show configuration\""
   # Processing ex_list and filling "-ex" parameters
   for kw_ex_list_item in kw_ex_list:
      command += f" -ex \"{kw_ex_list_item}\""
   # Processing specific named kwargs parameters and filling/overriding "-ex" parameters
   command += f" -ex \"target remote {kw_ip}:{str(kw_port)}\""
   if None != kw_arch:
      command += f" -ex \"set architecture {kw_arch}\""
   if None != kw_file:
      command += f" -ex \"file {kw_file}\""
   if None != kw_lib_path:
      command += f" -ex \"set solib-search-path {kw_lib_path}\""
   if None != kw_src_path:
      command += f" -ex \"set directories {kw_src_path}\""
   if None != kw_load_symbols:
      for symbols_file in kw_load_symbols:
         for symbols_offset in kw_load_symbols[ symbols_file ]:
            if None == symbols_offset:
               symbols_offset = ""
            command += f" -ex \"add-symbol-file {symbols_file} {symbols_offset}\""
   if None != kw_break_names:
      for break_name in kw_break_names:
         command += f" -ex \"b {break_name}\""
   if None != kw_break_addresses:
      for break_addr in kw_break_addresses:
         command += f" -ex \"b *{break_addr}\""
   if None != kw_break_code:
      for break_file in kw_break_code:
         for break_line in kw_break_code[ break_file ]:
            command += f" -ex \"b {break_file}:{break_line}\""

   command += f" -ex \"info breakpoints\""
   command += f" -ex \"info files\""

   pfw.shell.execute( command, output = pfw.shell.eOutput.PTY )
# run



def example_debug_uboot( **kwargs ):
   source_dir = "/mnt/u-boot/"
   file = "u-boot"
   arch = None
   lib_path = None
   src_path = None

   pfw.linux.gdb.run(
         arch = arch,
         file = file,
         lib_path = lib_path,
         src_path = src_path,
         load_symbols = {
            file: [ 0x23ff03000 ], # in case of "u-boot" "x0" register when enter to "relocate_code" function
         },
         break_names = [
            "relocate_code",
            "relocate_done",
            "do_bootm",
            "do_bootm_states",
            "bootm_find_other",
            "bootm_find_images",
            "boot_get_ramdisk",
            "select_ramdisk",
            "android_image_load",
            "android_bootloader_boot_kernel",
            "boot_jump_linux",
            "announce_and_cleanup",
            "armv8_switch_to_el2",
         ],
         break_addresses = [
         ],
         break_code = {
            f"{source_dir}/arch/arm/cpu/armv8/transition.S": [ 30 ]
         },
         none = None
      )
# def example_debug_uboot

def example_debug_linux( **kwargs ):
   source_dir = "/mnt/linux/"
   file = "vmlinux"
   arch = None

   pfw.linux.gdb.run(
         arch = arch,
         file = file,
         load_symbols = {
            file: [ 0x40410800 ], # kernel 5.15 loaded to 0x40410800
            # file: [ 0x53010000 ], # kernel 5.15 loaded to 0x40410800
         },
         break_names = [
            "primary_entry",
            "__primary_switch",
            "__primary_switched",
            "start_kernel",
            "rest_init",
            "cpu_startup_entry"
         ],
         break_code = {
         },
         ex_list = [
            # f"add-auto-load-safe-path {project.dirs( ).build( )}",
            # f"add-auto-load-safe-path " + project.dirs( ).source( "scripts/gdb/vmlinux-gdb.py" ),
            # f"source {project.dirs( ).build( 'vmlinux-gdb.py' )}",
         ],
         none = None
      )
# def example_debug_linux
