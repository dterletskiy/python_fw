import os



CSI = '\033['
OSC = '\033]'
BEL = '\007'
_UNSET = object( )
_COLOR_MODE = None



def code_to_chars( code ):
   return CSI + str(code) + 'm'

def set_title( title ):
   return OSC + '2;' + title + BEL

def clear_screen( mode = 2 ):
   return CSI + str(mode) + 'J'

def clear_line( mode = 2 ):
   return CSI + str(mode) + 'K'


class AnsiCodes( object ):
   def __init__( self ):
      for name in dir( self ):
         if not name.startswith('_'):
            value = getattr( self, name )
            setattr( self, name, code_to_chars( value ) )


class AnsiCursor( object ):
   def UP(self, n=1):
      return CSI + str(n) + 'A'
   def DOWN(self, n=1):
      return CSI + str(n) + 'B'
   def FORWARD(self, n=1):
      return CSI + str(n) + 'C'
   def BACK(self, n=1):
      return CSI + str(n) + 'D'
   def POS(self, x=1, y=1):
      return CSI + str(y) + ';' + str(x) + 'H'


class AnsiForeground( AnsiCodes ):
   BLACK          = 30
   RED            = 31
   GREEN          = 32
   YELLOW         = 33
   BLUE            = 34
   MAGENTA        = 35
   CYAN            = 36
   WHITE          = 37
   RESET          = 39
   LIGHTBLACK     = 90
   LIGHTRED       = 91
   LIGHTGREEN     = 92
   LIGHTYELLOW    = 93
   LIGHTBLUE      = 94
   LIGHTMAGENTA   = 95
   LIGHTCYAN      = 96
   LIGHTWHITE     = 97


class AnsiBackground( AnsiCodes ):
   BLACK          = 40
   RED            = 41
   GREEN          = 42
   YELLOW         = 43
   BLUE            = 44
   MAGENTA        = 45
   CYAN            = 46
   WHITE          = 47
   RESET          = 49
   LIGHTBLACK     = 100
   LIGHTRED       = 101
   LIGHTGREEN     = 102
   LIGHTYELLOW    = 103
   LIGHTBLUE      = 104
   LIGHTMAGENTA   = 105
   LIGHTCYAN      = 106
   LIGHTWHITE     = 107


class AnsiStyle( AnsiCodes ):
   BOLD           = 1
   DIM            = 2
   UNDERLINED     = 4
   BLINK          = 5
   REVERSE        = 7
   HIDDEN         = 8
   RESET          = 0



Foreground        = AnsiForeground( )
Background        = AnsiBackground( )
Style             = AnsiStyle( )
Cursor            = AnsiCursor( )



def get_color_mode( ):
   return _COLOR_MODE


def set_color_mode( value ):
   global _COLOR_MODE

   if None != value and not isinstance( value, bool ):
      raise TypeError( "colored must be True, False, or None" )

   previous = _COLOR_MODE
   _COLOR_MODE = value
   return previous


def is_color_enabled( file, colored = _UNSET ):
   if colored is _UNSET:
      colored = _COLOR_MODE

   if None != colored:
      return bool( colored )

   if "NO_COLOR" in os.environ or "dumb" == os.environ.get( "TERM", "" ).lower( ):
      return False

   try:
      return bool( file.isatty( ) )
   except ( AttributeError, OSError, ValueError ):
      return False
