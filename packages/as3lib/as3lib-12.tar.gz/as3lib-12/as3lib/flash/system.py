import as3lib as as3
from as3lib import as3state, metaclasses
from functools import cache
import platform
import sys


class ApplicationDomain:...


class Capabilities:
   # TODO: get actual values
   # TODO: document changes from original
   def _propTrue():
      return True

   def _propFalse():
      return False

   avHardwareDisable = property(fget=_propTrue)  # This is not needed so it is always True

   @property
   @cache
   def cpuAddressSize():  # returns 32 (32bit system) or 64 (64bit system)
      return as3.Number(platform.architecture()[0][:-3])

   @property
   @cache
   def cpuArchitecture():  # returns 'PowerPC','x86','SPARC',or 'ARM'
      if platform.machine() in {'x86', 'x86_64', 'AMD64'}:
         return 'x86'
      if platform.machine() == 'PowerPC':
         return 'PowerPC'
      if platform.machine() in {'ARM', 'ARM64'}:
         return 'ARM'

   #hasAccessibility

   hasAudio = property(fget=_propTrue)

   #hasAudioEncoder
   #hasEmbeddedVideo
   #hasIME
   #hasMP3
   #hasPrinting
   #hasScreenBroadcast
   #hasScreenPlayback
   #hasStreamingAudio
   #hasStreamingVideo
   #hasTLS
   #hasVideoEncoder

   @property
   def isDebugger():
      return as3state.as3DebugEnable

   isEmbeddedInAcrobat = property(fget=_propFalse)  # Always false because this is irelavant

   #language
   #languages
   #localFileReadDisable

   @property
   @cache
   def manufacturer():
      if as3state.platform == 'Windows':
         return 'Adobe Windows'
      if as3state.platform == 'Linux':
         return 'Adobe Linux'
      if as3state.platform == 'Darwin':
         return 'Adobe Macintosh'

   #maxLevelIDC

   @property
   @cache
   def os():
      # TODO: add others
      if as3state.platform == 'Windows':...
      if as3state.platform == 'Linux':
         return f'Linux {platform.release()}'
      if as3state.platform == 'Darwin':...

   #pixelAspectRatio

   @property
   def playerType():
      return 'StandAlone'

   #screenColor
   #screenDPI

   @property
   def screenResolutionX():
      return as3state.width

   @property
   def screenResolutionY():
      return as3state.height

   #serverString
   #supports32BitProcesses
   #supports64BitProcesses
   #touchscreenType

   @property
   @cache
   def version():
      tempfv = as3state.flashVersion
      if as3state.platform == 'Windows':
         return f'Win {tempfv[0]},{tempfv[1]},{tempfv[2]},{tempfv[3]}'
      if as3state.platform == 'Linux':
         return f'LNX {tempfv[0]},{tempfv[1]},{tempfv[2]},{tempfv[3]}'
      if as3state.platform == 'Darwin':
         return f'MAC {tempfv[0]},{tempfv[1]},{tempfv[2]},{tempfv[3]}'
      if as3state.platform == 'Android':
         return f'AND {tempfv[0]},{tempfv[1]},{tempfv[2]},{tempfv[3]}'

   def hasMultiChannelAudio(type: str):...


def fscommand(command, args=''):
   '''
   This is a simplified version of fscommand and does not do everything it should
   '''
   if command == 'quit':...
   elif command == 'fullscreen':...
   elif command == 'allowscale':...
   elif command == 'showmenu':...
   elif command == 'exec':...
   elif command == 'trapallkeys':...


class ImageDecodingPolicy(metaclass=metaclasses._AS3_CONSTANTSOBJECT):
   ON_DEMAND = 'onDemand'
   ON_LOAD = 'onLoad'


class IME:...


class IMEConversionMode(metaclass=metaclasses._AS3_CONSTANTSOBJECT):
   ALPHANUMERIC_FULL = 'ALPHANUMERIC_FULL'
   ALPHANUMERIC_HALF = 'ALPHANUMERIC_HALF'
   CHINESE = 'CHINESE'
   JAPANESE_HIRAGANA = 'JAPANESE_HIRAGANA'
   JAPANESE_KATAKANA_FULL = 'JAPANESE_KATAKANA_FULL'
   JAPANESE_KATAKANA_HALF = 'JAPANESE_KATAKANA_HALF'
   KOREAN = 'KOREAN'
   UNKNOWN = 'UNKNOWN'


class JPEGLoaderContex:...


class LoaderContext:...


class MessageChannel:...


class MessageChannelState(metaclass=metaclasses._AS3_CONSTANTSOBJECT):
   CLOSED = 'closed'
   CLOSING = 'closing'
   OPEN = 'open'


class Security:...


class SecurityDomain:...


class SecurityPanel:...


class System:
   #freeMemory
   #ime
   #privateMemory
   #totalMemory
   #totalMemoryNumber
   #useCodePage

   def disposeXML():...

   def exit(code: int | as3.Int | as3.uint = 0):
      sys.exit(int(code))

   def gc():...

   def pause():...

   def pauseForGCIfCollectionImminent():...

   def resume():...

   def setClipboard():...


class SystemUpdater:...


class SystemUpdaterType(metaclass=metaclasses._AS3_CONSTANTSOBJECT):
   DRM = 'drm'
   SYSTEM = 'system'


class TouchscreenType(metaclass=metaclasses._AS3_CONSTANTSOBJECT):
   FINGER = 'finger'
   NONE = 'none'
   STYLUS = 'stylus'


class Worker:...


class WorkerDomain:...


class WorkerState(metaclass=metaclasses._AS3_CONSTANTSOBJECT):
   NEW = 'new'
   RUNNING = 'running'
   TERMINATED = 'terminated'
