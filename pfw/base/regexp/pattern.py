import re

import pfw.console



groups = {
   "signed": {
      "int": r"([+-]?)(\d+)",
      "float": r"([+-]?)(\d+)(?:\.(\d+))",
      "number": r"([+-]?)(\d+)(?:\.(\d+))?",
   },
   "unsigned": {
      "int": r"(\d+)",
      "float": r"(\d+)(?:\.(\d+))",
      "number": r"(\d+)(?:\.(\d+))?",
   },
}

no_group = {
   "signed": {
      "int": r"[+-]?\d+",
      "float": r"[+-]?\d+(?:\.\d+)",
      "number": r"[+-]?\d+(?:\.\d+)?",
   },
   "unsigned": {
      "int": r"\d+",
      "float": r"\d+(?:\.\d+)",
      "number": r"\d+(?:\.\d+)?",
   },
}

group = {
   "signed": {
      "int": r"([+-]?\d+)",
      "float": r"([+-]?\d+(?:\.\d+))",
      "number": r"([+-]?\d+(?:\.\d+)?)",
   },
   "unsigned": {
      "int": r"(\d+)",
      "float": r"(\d+(?:\.\d+))",
      "number": r"(\d+(?:\.\d+)?)",
   },
}

