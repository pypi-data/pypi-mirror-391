import as3lib as as3
from as3lib import as3state, metaclasses
from as3lib.flash import utils
from as3lib.flash.events import DataEvent, Event, EventDispatcher, HTTPStatusEvent, IOErrorEvent, PermissionEvent, ProgressEvent, SecurityErrorEvent
import miniamf
from miniamf import sol
from tkinter import filedialog


def getClassByAlias(aliasName: str):
   try:
      return miniamf.get_class_alias(aliasName)
   except miniamf.UnknownClassAlias:
      raise as3.ReferenceError(f'Alias {aliasName} was not registered.')


def navigateToURL(request, window: str = None):...


def registerClassAlias(aliasName: str, classObject):
   if aliasName is None or classObject is None:
      raise as3.TypeError('Arguements to registerClassAlias can not be null.')
   miniamf.register_class(classObject, aliasName)


def sendToURL(request):...


class DatagramSocket:...


class FileFilter:
   def __init__(self, description: str, extension: str, macType: str = None):
      self.description = description
      self.extension = extension
      self.macType = macType

   def extensionsToArray(self):
      return as3.Array(*self.extension.split(';'))

   def macTypeToArray(self):
      if self.macType is not None:
         return as3.Array(*self.macType.split(';'))

   def toTkTuple(self):
      return (self.description, self.extension.split(';'))


class FileReference(EventDispatcher):
   @property
   def creationDate(self):
      return self._creationDate

   @property
   def creator(self):
      return self._creator

   @property
   def data(self):
      return self._data

   @property
   def extension(self):
      return self._extension

   @property
   def modificationDate(self):
      return self._modificationDate

   @property
   def name(self):
      return self._name

   @staticmethod
   def _getPerStat():
      return True
   permissionStatus = property(fget=_getPerStat)

   @property
   def size(self):
      return self._size

   @property
   def type(self):
      return self._type

   def __init__(self):
      super().__init__()
      self._location = None
      self.cancel = Event('cancel', False, False)
      self.complete = Event('complete', False, False)
      self.httpResponseStatus = HTTPStatusEvent('httpResponseStatus', False, False)
      self.httpStatus = HTTPStatusEvent('httpStatus', False, False)
      self.ioError = IOErrorEvent('ioError', False, False)
      self.open = Event('open', False, False)
      self.permissionStatus = PermissionEvent('permissionStatus', False, False)
      self.progress = ProgressEvent('progress', False, False)
      self.securityError = SecurityErrorEvent('securityError', False, False)
      self.select = Event('select', False, False)
      self.uploadCompleteData = DataEvent('uploadCompleteEvent', False, False)

   def _setFile(self, file):
      # Sets the file and all of its details
      ...

   def browse(self, typeFilter: list | tuple = None):
      # typeFilter is an Array/list/tuple of FileFilter objects
      # TODO: Make a custom file browser window that calls all of events properly. This does not function properly
      #       the way it is currently implemented. True is supposed to be returned when the dialog is opened, not after the events.
      if typeFilter is not None:
         filename = filedialog.askopenfilename(title='Select a file to upload', filetypes=tuple(i.toTkTuple() for i in typeFilter))
      else:
         filename = filedialog.askopenfilename(title='Select a file to upload')
      if filename in {None, ()}:
         self.dispatchEvent(self.cancel)
      else:
         self.dispatchEvent(self.select)
      return True

   def cancel(self):...  # Cancels the 'download' without calling the cancel event

   def dowload(self, request, defaultFileName=None):...

   def load(self):...

   def requestPermission(self):...

   def save(self, data, defaultFileName=None):
      # TODO: add check for blacklisted characters  / \ : * ? " < > | %
      self.dispatchEvent(self.open)
      file = defaultFileName.split('.')
      savetype = 0  # 1=UTF-8 2=XML 3=ByteArray
      if data is None:
         raise as3.ArguementError('Invalid Data')
      elif isinstance(data, str):
         # write a UTF-8 text file
         savetype = 1
      #elif type(data) == #XML:
         # Write as xml format text file with format preserved
         #savetype = 2
      elif isinstance(data, utils.ByteArray):
         # write data to file as is (in byte form)
         savetype = 3
      else:
         # convert to string and save as text file. If it fails throw ArguementError
         try:
            data = str(data)
         except Exception:
            raise as3.ArguementError('Invalid Data')
      if len(file) == 1:
         # no extension
         filename = filedialog.asksaveasfilename(title='Select location for download')
      else:
         # extension
         # !doesn't seen to work
         ext = f'.{file[-1]}'
         filename = filedialog.asksaveasfilename(title='Select location for download', defaultextension=ext)
      if filename in {None, ()}:
         self.dispatchEvent(self.cancel)
      else:
         self.dispatchEvent(self.select)
         self._location = filename
         self.dispatchEvent(self.complete)

   def upload(self, request, uploadDataFieldName, testUpload=False):...

   def uploadUnencoded(self, request):...


class FileReferenceList:...


class GroupSpecifier:...


class InterfaceAddress:
   #address = classmethod()
   #broadcast = classmethod()
   def __getAddrType():...
   #ipVersion = classmethod(fget=__AddrType)
   #prefixLength = classmethod()


class IPVersion(metaclass=metaclasses._AS3_CONSTANTSOBJECT):
   IPV4 = 'IPv4'
   IPV6 = 'IPv6'


class LocalConnection:...


class NetGroup:...


class NetGroupInfo:...


class NetGroupReceiveMode:...


class NetGroupReplicationStrategy:...


class NetGroupSendMode:...


class NetGroupSendResult:...


class NetMonitor:...


class NetStream:...


class NetStreamAppendBytesAction:...


class NetStreamInfo:...


class NetStreamMulticastInfo:...


class NetStreamPlayOptions:...


class NetStreamPlayTransitions:...


class NetworkInfo:...


class NetworkInterface:...


class ObjectEncoding(metaclass=metaclasses._AS3_CONSTANTSOBJECT):
   AMF0 = 0
   AMF3 = 3
   DEFAULT = 3


class Responder:...


class SecureSocket:...


class SharedObject(dict):
   # TODO: Make this a child of EventDispatcher
   # TODO: Implement remote shared objects
   defaultObjectEncoding = 3  # This can be set globally

   def _getEncoded(self):
      return sol.encode(self._name, self['data'], encoding=self.objectEncoding)

   @property
   def size(self):
      return len(self._getEncoded())

   @property
   def data(self):
      return self['data']

   def __init__(self):
      self.objectEncoding = SharedObject.defaultObjectEncoding
      super().__init__()
      self._name = None
      self._path = None
      self['data'] = {}

   def clear(self):
      self._path.unlink(missing_ok=True)
      self['data'].clear()

   def close(self):...

   def connect(self):...

   def flush(self, minDiskSpace=0):
      with self._path.open('wb+') as f:
         f.write(self._getEncoded().getvalue())
      ...
      return SharedObjectFlushStatus.FLUSHED

   @staticmethod
   def getLocal(name, localPath='', secure=False):
      # gets local shared object; if object exists, set path and load it. if not, just set path
      # localPath is relative to as3state.appdatadirectory
      if as3state.appdatadirectory is None:
         raise as3.Error('Application specific data directory was not set. Can not safely determine location.')
      obj = SharedObject()
      path = as3state.appdatadirectory / localPath.strip('/\\')  # Path separator at the start causes issues but doesn't matter at the end
      obj._name = name
      obj._path = path / f'{name}.sol'
      if obj._path.is_file():
         with obj._path.open('rb') as f:
            obj['data'] = dict(sol.load(f))
      return obj

   @staticmethod
   def getRemote(name, remotePath=None, persistance=False, secure=False):...

   def send(self, *arguments):...

   def setDirty(self, propertyName):...

   def setProperty(self, propertyName, value=None):...


class SharedObjectFlushStatus(metaclass=metaclasses._AS3_CONSTANTSOBJECT):
   FLUSHED = 'flushed'
   PENDING = 'pending'


class Socket:...


class URLLoader:...


class URLLoaderDataFormat:...


class URLRequest:...


class URLRequestDefaults:...


class URLRequestHeader:...


class URLRequestMethod:...


class URLStream:...


class URLVariables:...


class XMLSocket:...


if __name__ == '__main__':
   def eventCancel(event=None):
      print('cancel')

   def eventSelect(event=None):
      print('select')

   def eventComplete(event=None):
      print('complete')

   filter1 = FileFilter('Text File', '*.txt')
   filter2 = FileFilter('Shell Script', '*.sh')
   filter3 = FileFilter('Files', '*.xml;*.exe;*.py')
   fr = FileReference()
   fr.addEventListener(Event.CANCEL, eventCancel)
   fr.addEventListener(Event.SELECT, eventSelect)
   fr.addEventListener(Event.COMPLETE, eventComplete)
   fr.browse([filter1, filter2, filter3])
   fr.save('test', 'test.txt')
