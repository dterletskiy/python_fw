import getpass
import sys

from pfw import terminal



PROMPT_FORMAT = terminal.Foreground.MAGENTA
RESET_FORMAT = terminal.Background.RESET + terminal.Foreground.RESET + terminal.Style.RESET



def _message( string, colored ):
   if terminal.is_color_enabled( sys.stdout, colored ):
      return PROMPT_FORMAT + string + RESET_FORMAT
   return string


def _getpassword( string ):
   try:
      import getch
   except ModuleNotFoundError as error:
      raise ModuleNotFoundError(
         "Asterisk prompts require the optional 'getch' package."
      ) from error

   print( string, end = '', flush = True )

   password = ''
   while True:
      character = getch.getch( )
      if '\r' == character or '\n' == character:
         break
      print( '*', end = '', flush = True )
      password += character

   print( "" )
   return password


def prompt( string: str = "Press any key...", **kwargs ):
   mask = kwargs.get( "mask", None )
   colored = kwargs.get( "colored", terminal.get_color_mode( ) )
   message = _message( string, colored )

   if None == mask:
      return input( message )

   try:
      import pwinput
   except ModuleNotFoundError as error:
      raise ModuleNotFoundError(
         "Masked prompts require the optional 'pwinput' package."
      ) from error

   return pwinput.pwinput( prompt = message, mask = mask )


def prompt_dep( string: str = "Press any key...", **kwargs ):
   prompt_type = kwargs.get( "type", "show" )
   colored = kwargs.get( "colored", terminal.get_color_mode( ) )
   message = _message( string, colored )

   caller = input
   if "hide" == prompt_type:
      caller = getpass.getpass
   elif "asterisk" == prompt_type:
      caller = _getpassword

   return caller( message )
