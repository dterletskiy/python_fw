"""Compatibility facade for the decomposed console modules."""

from pfw import log as _log
from pfw import prompt as _prompt
from pfw.terminal import AnsiBackground
from pfw.terminal import AnsiCodes
from pfw.terminal import AnsiCursor
from pfw.terminal import AnsiForeground
from pfw.terminal import AnsiStyle
from pfw.terminal import Background
from pfw.terminal import BEL
from pfw.terminal import CSI
from pfw.terminal import Cursor
from pfw.terminal import Foreground
from pfw.terminal import OSC
from pfw.terminal import Style
from pfw.terminal import clear_line
from pfw.terminal import clear_screen
from pfw.terminal import code_to_chars
from pfw.terminal import set_title



TRACE = _log.TRACE
AnsiFormat = _log.AnsiFormat
Format = _log.Format
ConsoleLogger = _log.ConsoleLogger
_AnsiFormatter = _log._AnsiFormatter
_AnsiHandler = _log._AnsiHandler

configure = _log.configure


class AnsiDebug( ConsoleLogger ):
   def prompt( self, string: str = "Press any key...", **kwargs ):
      kwargs.setdefault( "colored", self.color_mode( ) )
      return _prompt.prompt( string, **kwargs )

   def prompt_dep( self, string: str = "Press any key...", **kwargs ):
      kwargs.setdefault( "colored", self.color_mode( ) )
      return _prompt.prompt_dep( string, **kwargs )


printf = AnsiDebug( inspect = 0 )
log = AnsiDebug( inspect = 1 )
debug = log

prompt = _prompt.prompt
prompt_dep = _prompt.prompt_dep
getpass = _prompt.getpass
