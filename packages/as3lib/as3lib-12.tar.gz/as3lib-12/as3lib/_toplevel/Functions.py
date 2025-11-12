from as3lib import as3state
import builtins
from pathlib import Path, PurePath
try:
   from warnings import deprecated
except Exception:
   from as3lib.py_backports import deprecated
from as3lib._toplevel.Constants import _NaN_value, _NegInf_value, _PosInf_value, NInfinity, Infinity, NaN
from as3lib._toplevel.int import int
from as3lib._toplevel.uint import uint
from as3lib._toplevel.Number import Number
from as3lib._toplevel.Errors import Error


def decodeURI():...


def decodeURIComponent():...


def encodeURI():...


def encodeURIComponent():...


def escape():
   '''
   Converts the parameter to a string and encodes it in a URL-encoded format, where most nonalphanumeric characters are replaced with % hexadecimal sequences. When used in a URL-encoded string, the percentage symbol (%) is used to introduce escape characters, and is not equivalent to the modulo operator (%).
   The following characters are not converted to escape sequences by the escape() function.
   0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ@-_.*+/
   '''
   ...


def isFinite(num):
   return not (num in (_PosInf_value, _NegInf_value, _NaN_value) or isinstance(num, (NInfinity, Infinity, NaN)))


def isNaN(num):
   return num == _NaN_value or isinstance(num, NaN)


def isXMLName(str_: str):
   # currently this is spec compatible with the actual xml specs but unknown if it is the same as the actionscript function.
   whitelist = {'-', '_', '.'}
   if len(str_) == 0 or not str_[0].isalpha() and str_[0] != '_' or str_[:3].lower() == 'xml' or ' ' in str_:
      return False
   for i in str_:
      if not i.isalnum() and i not in whitelist:
         return False
   return True


def parseFloat(str_: str):
   # !Make stop a second period
   str_ = str_.lstrip()
   size = len(str_)
   if size == 0:
      return NaN()
   if str_[0].isdigit():
      j = 0
      while j != size and (str_[j].isdigit() or str_[j] == "."):
         j += 1
      return Number(str_[:j])
   return NaN()


def parseInt(str_: str, radix: int | uint = 0):
   str_ = str_.lstrip()
   zero = False
   if len(str_) >= 2 and str_.startswith('0x'):
      radix = 16
      str_ = str_[2:]
   elif radix < 2 or radix > 36:
      raise Error(f'parseInt; radix {radix} is outside of the acceptable range')
   if str_.startswith('0'):
      zero = True
      str_.lstrip("0")
   radixchars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'[:radix]
   str_ = str_.upper()
   j = 0
   while j < len(str_) and str_[j] in radixchars:
      j += 1
   if j == 0:
      return 0 if zero else NaN()
   return int(builtins.int(str_[:j], radix))


def unescape():...


def EnableDebug():
   '''
   Enables as3lib debug mode. This is a substitute for have an entire separate interpreter.
   '''
   as3state.as3DebugEnable = True


def DisableDebug():
   '''
   Disables as3lib debug mode. This is a substitute for have an entire separate interpreter.
   '''
   as3state.as3DebugEnable = False


@deprecated('formatTypeToName is deprecated and will be removed in version 13. Use type.__name__ instead.')
def formatTypeToName(arg: type):
   tempStr = f'{arg}'
   if tempStr.find('.') != -1:
      return tempStr.split('.')[-1].split("'")[0]
   return tempStr.split("'")[1]


def isEven(Num: builtins.int | float | int | Number | uint | NaN | Infinity | NInfinity):
   if isinstance(Num, (NaN, Infinity, NInfinity)):
      return False
   if isinstance(Num, (builtins.int, int, uint)):
      return Num % 2 == 0
   if isinstance(Num, (float, Number)):...


def isOdd(Num: builtins.int | float | int | Number | uint | NaN | Infinity | NInfinity):
   if isinstance(Num, (NaN, Infinity, NInfinity)):
      return False
   if isinstance(Num, (builtins.int, int, uint)):
      return Num % 2 != 0
   if isinstance(Num, (float, Number)):...


def objIsChildClass(obj, cls):
   '''
   Checks both isinstance and issubclass for (obj,cls)
   '''
   return isinstance(obj, cls) or issubclass(obj, cls)


if as3state.platform == 'Windows':
   BlacklistedChars = {'<', '>', ':', '"', '\\', '/', '|', '?', '*', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''}
   BlacklistedNames = {'CON', 'PRN', 'AUX', 'NUL', 'COM0', 'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'COM¹', 'COM²', 'COM³', 'LPT0', 'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9', 'LPT¹', 'LPT²', 'LPT³'}

   def isValidDirectory(directory, separator=None):
      '''
      Checks if a given directory is valid on the current platform
      '''
      if isinstance(directory, PurePath):
         # While this is ten times slower than using a string, it is much simpler and more robust so should give less incorrect answers
         temp = directory.resolve()
         while True:
            # get directory name and convert it to uppercase since windows is not case sensitive
            tempname = temp.name.upper()
            # invalid if blacklisted characters are used
            for i in tempname:
               if i in BlacklistedChars:
                  return False
            # invalid if last character is " " or "." or if name or name before a period is blacklisted
            if tempname.endswith((' ', '.')) or tempname.split('.')[0] in BlacklistedNames:
               return False
            temp = temp.parent
            if temp == temp.parent:
               break
         # Check drive letter
         if not (str(temp)[0].isalpha() and str(temp)[1:] in {':', ':\\', ':/'}):
            return False
      elif separator is not None:
         directory = str(directory)
         # convert path to uppercase since windows is not cas sensitive
         directory = directory.upper()
         # remove trailing path separator
         if directory[-1] == separator:
            directory = directory[:-1]
         # remove drive letter or server path designator
         if directory[0].isalpha() and directory[1] == ':' and directory[2] == separator:
            directory = directory[3:]
         elif directory.startswith('\\\\'):
            directory = directory[2:]
         elif directory.startswith(f'.{separator}'):
            directory = directory[-(len(directory)-2):]
         for i in directory.split(separator):
            # invalid if blacklisted characters are used
            for j in i:
               if j in BlacklistedChars:
                  return False
            # invalid if last character is " " or "." or if name or name before a period is blacklisted
            if i.endswith((' ', '.')) or i.split('.')[0] in BlacklistedNames:
               return False
      return True
else:
   BlacklistedChars = {'/', '<', '>', '|', ':', '&', ''}
   BlacklistedNames = {'.', '..'}

   def isValidDirectory(directory, separator=None):
      '''
      Checks if a given directory is valid on the current platform
      '''
      if isinstance(directory, PurePath):
         # While this is ten times slower than using a string, it is much simpler and more robust so should give less incorrect answers
         temp = directory.resolve()
         while True:
            tempname = temp.name
            # invalid if blacklisted names are used
            if tempname in BlacklistedNames:
               return False
            # invalid if blacklisted characters are used
            for i in tempname:
               if i in BlacklistedChars:
                  return False
            temp = temp.parent
            if temp == temp.parent:
               break
      elif separator is not None:
         directory = str(directory)
         # remove trailing path separator
         if directory[-1] == separator:
            directory = directory[:-1]
         elif directory.endswith(f'{separator}.'):
            directory = directory[:-2]
         # remove starting path separator
         if directory[0] == separator:
            directory = directory[-(len(directory)-1):]
         elif directory.startswith((f'.{separator}', f'~{separator}')):
            directory = directory[-(len(directory)-2):]
         for i in directory.split(separator):
            # invalid if blacklisted names are used
            if i in BlacklistedNames:
               return False
            # invalid if blacklisted characters are used
            for j in i:
               if j in BlacklistedChars:
                  return False
      return True


def setDataDirectory(directory: str):
   if not isValidDirectory(Path(directory)):
      raise Error(f'setDataDirectory; Directory {directory} not valid')
   as3state.appdatadirectory = Path(directory)
