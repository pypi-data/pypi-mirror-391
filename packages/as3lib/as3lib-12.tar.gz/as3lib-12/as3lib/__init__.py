from . import as3state, config
from pathlib import Path
from subprocess import check_output
import os
import builtins
from functools import partial
from miniamf import add_type

'''
initerrors
0 - platform not implemented
1 - function not implemented for current platform
2 - (Linux specific) unexpected display server (expected x11 or wayland)
3 - dependency not found
4 - other error
'''


# Helper functions
def defaultTraceFilePath_Flash(sysverOverride: tuple = None):
   '''
   Outputs the defualt file path for trace as defined by https://web.archive.org/web/20180227100916/helpx.adobe.com/flash-player/kb/configure-debugger-version-flash-player.html
   Arguements:
      sysverOverride - A tuple containing the system and version of system you want to choose. ex: ('Windows','XP')
   '''
   if as3state.platform == 'Windows':
      username = os.getlogin()
   elif as3state.platform in {'Linux', 'Darwin'}:
      from pwd import getpwuid
      username = getpwuid(os.getuid())[0]
   if sysverOverride is not None:
      if sysverOverride[0] == 'Linux':
         return fr'/home/{username}/.macromedia/Flash_Player/Logs/flashlog.txt'
      if sysverOverride[0] == 'Darwin':
         return fr'/Users/{username}/Library/Preferences/Macromedia/Flash Player/Logs/flashlog.txt'
      if sysverOverride[0] == 'Windows':
         if sysverOverride[1] in {'95', '98', 'ME', 'XP'}:
            return fr'C:\Documents and Settings\{username}\Application Data\Macromedia\Flash Player\Logs\flashlog.txt'
         if sysverOverride[1] in {'Vista', '7', '8', '8.1', '10', '11'}:
            return fr'C:\Users\{username}\AppData\Roaming\Macromedia\Flash Player\Logs\flashlog.txt'
   if as3state.platform == 'Linux':
      return fr'/home/{username}/.macromedia/Flash_Player/Logs/flashlog.txt'
   if as3state.platform == 'Windows':
      return fr'C:\Users\{username}\AppData\Roaming\Macromedia\Flash Player\Logs\flashlog.txt'
   if as3state.platform == 'Darwin':
      return fr'/Users/{username}/Library/Preferences/Macromedia/Flash Player/Logs/flashlog.txt'


def sm_x11():
   '''
   Gets and returns screen width, screen height, refresh rate, and color depth on x11
   '''
   for option in check_output(('xrandr', '--current')).decode('utf-8').split('\n'):
      if '*' in option:
         for i in option.split(' '):
            if i != '' and '*' in i:
               rr = i.strip('*+')
               break
         break
   depth = check_output('xwininfo -root | grep Depth', shell=True).decode('utf-8').split(':')[1].strip(' \n')
   width = check_output('xwininfo -root | grep Width', shell=True).decode('utf-8').split(':')[1].strip(' \n')
   height = check_output('xwininfo -root | grep Height', shell=True).decode('utf-8').split(':')[1].strip(' \n')
   return int(width), int(height), float(rr), int(depth)


def sm_wayland():
   return sm_x11()  # Only works on XWayland


def sm_windows():
   import ctypes
   try:
      import win32api
   except ModuleNotFoundError:
      as3state.initerror.append((3, 'Windows: Requirement pywin32 either not installed or not accessible.'))
      return 1600, 900, 60.0, 16
   settings = win32api.EnumDisplaySettings(win32api.EnumDisplayDevices().DeviceName, -1)
   return int(ctypes.windll.user32.GetSystemMetrics(0)), int(ctypes.windll.user32.GetSystemMetrics(1)), float(getattr(settings, 'DisplayFrequency')), int(getattr(settings, 'BitsPerPel'))


def sm_darwin():
   as3state.initerror.append((1, 'Darwin: Fetching screen properties is not implemented.'))
   raise NotImplementedError('Fetching screen properties on Darwin')


def setScreenProperties(func):
   try:
      temp = func()
   except:
      temp = (1600, 900, 60.0, 16)
   as3state.width, as3state.height, as3state.refreshrate, as3state.colordepth = temp

# Initialise as3lib
if as3state.startTime is None:
   from datetime import datetime
   from miniamf import util
   as3state.startTime = int(util.get_timestamp(datetime.now()) * 1000)
if not as3state.initdone:
   import platform
   as3state.platform = platform.system()
   as3state.separator = '\\' if as3state.platform == 'Windows' else '/'
   as3state.pythonversion = platform.python_version()
   as3state.librarydirectory = Path(__file__).resolve().parent
   as3state.userdirectory = Path.home()
   as3state.desktopdirectory = Path(os.environ.get('XDG_DESKTOP_DIR', as3state.userdirectory / 'Desktop'))
   as3state.documentsdirectory = Path(os.environ.get('XDG_DOCUMENTS_DIR', as3state.userdirectory / 'Documents'))
   as3state.defaultTraceFilePath_Flash = defaultTraceFilePath_Flash()

   if as3state.platform == 'Linux':
      as3state.displayserver = os.environ.get('XDG_SESSION_TYPE', 'error')
      if as3state.displayserver == 'x11':
         setScreenProperties(sm_x11)
      elif as3state.displayserver == 'wayland':
         setScreenProperties(sm_wayland)
      else:
         as3state.initerror.append((2, f'Linux: Display server "{as3state.windowmanagertype}" not supported.'))
   elif as3state.platform == 'Windows':
      setScreenProperties(sm_windows)
   elif as3state.platform == 'Darwin':
      setScreenProperties(sm_darwin)
   elif as3state.platform == '':
      as3state.initerror.append((4, 'Detected platform is blank. Something is very wrong.'))
   else:
      as3state.initerror.append((0, f'Current platform {as3state.platform} not supported.'))

   # Load the config
   config.Load()
   if as3state.ClearLogsOnStartup:
      if as3state.TraceOutputFileName.exists():
         with open(as3state.TraceOutputFileName, 'w') as f:
            f.write('')

   # Display errors to user
   if as3state.initerror:
      print(f'Warning: as3lib has initialised with errors, some functionality may be broken.\n{"".join(f"\t({i[0]}) {i[1]}\n" for i in as3state.initerror)}')

   # Set the default appdatadirectory
   import __main__
   if hasattr(__main__, '__file__'):
      as3state.appdatadirectory = Path(__main__.__file__).resolve().parent
   else:  # Fall back to working directory
      as3state.appdatadirectory = Path.cwd()

   # Tell others that library has been initialised
   as3state.initdone = True


# Export toplevel and set up miniamf adapters
from ._toplevel.Array import Array
from ._toplevel.Boolean import Boolean
from ._toplevel.Constants import true, false, NInfinity, Infinity, NaN, undefined, null
from ._toplevel.Date import Date
from ._toplevel.Errors import ArgumentError, DefinitionError, Error, EvalError, RangeError, ReferenceError, SecurityError, SyntaxError, TypeError, URIError, VerifyError
from ._toplevel.Functions import decodeURI, decodeURIComponent, encodeURI, encodeURIComponent, escape, isFinite, isNaN, isXMLName, parseFloat, parseInt, unescape, EnableDebug, DisableDebug, isValidDirectory, setDataDirectory
from ._toplevel.int import int as Int
from ._toplevel.JSON import JSON
from ._toplevel.Math import Math
from ._toplevel.Namespace import Namespace
from ._toplevel.Number import Number
from ._toplevel.Object import Object
from ._toplevel.QName import QName
from ._toplevel.RegExp import RegExp
from ._toplevel.String import String
from ._toplevel.trace import trace
from ._toplevel.Types import allArray, allBoolean, allInt, allNumber, allNone, allString
from ._toplevel.uint import uint
from ._toplevel.Vector import Vector


try:
   def adapter(func, obj, encoder):
      return func(obj)

   add_type(Array, partial(adapter, list))
   add_type(Boolean, partial(adapter, bool))
   add_type(int, partial(adapter, builtins.int))
   add_type(Number, partial(adapter, float))
   add_type(String, partial(adapter, str))
   add_type(uint, partial(adapter, int))
except Exception as e:
   raise Error('Failed to set up miniamf type adapters.') from e


__all__ = (
   'formatToString',
   'as3import',

   'true',
   'false',
   'NInfinity',
   'Infinity',
   'NaN',
   'undefined',
   'null',

   'allArray',
   'allBoolean',
   'allInt',
   'allNumber',
   'allNone',
   'allString',

   'ArgumentError',
   'Array',
   'Boolean',
   'Date',
   'DefinitionError',
   'decodeURI',
   'decodeURIComponent',
   'encodeURI',
   'encodeURIComponent',
   'Error',
   'escape',
   'EvalError',
   'Int',
   'isFinite',
   'isNaN',
   'isXMLName',
   'JSON',
   'Math',
   'Namespace',
   'Number',
   'Object',
   'parseFloat',
   'parseInt',
   'QName',
   'RangeError',
   'ReferenceError',
   'RegExp',
   'SecurityError',
   'String',
   'SyntaxError',
   'trace',
   'TypeError',
   'uint',
   'unescape',
   'URIError',
   'Vector',
   'VerifyError',
   'EnableDebug',
   'DisableDebug',
   'isValidDirectory',
   'setDataDirectory'
)
