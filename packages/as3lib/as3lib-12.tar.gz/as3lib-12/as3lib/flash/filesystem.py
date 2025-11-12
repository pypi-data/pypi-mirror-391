import as3lib as as3
from as3lib import metaclasses, as3state
from subprocess import CalledProcessError, check_output


class File:
   # applicationDirectory
   # applicationStorageDirectory
   # cacheDirectory
   # desktopDirectory
   # documentsDirectory
   # downloaded
   # exists
   # icon
   # isDirectory
   # isHidden
   # isPackage
   # isSymbolicLink
   # lineEnding
   # nativePath
   # parent
   # permissionStatus
   # separator
   # spaceAvailable
   # systemCharset
   # url
   # userDirectory
   def __init__(self, path: str):
      # TODO: detect url path
      # TODO: convert path to native path and url
      # TODO: Throw exception ArguementError if path is invalid
      self._filepath = path

   def __str__(self):
      return self.toString()

   def browseForDirectory():...

   def browseForOpen():...

   def browseForOpenMultiple():...

   def browseForSave():...

   def cancel():...

   def canonicalize():...

   def clone():...

   def copyTo():...

   def copyToAsync():...

   def createDirectory():...

   def createTempDirectory():...

   def createTempFile():...

   def deleteDirectory():...

   def deleteDirectoryAsync():...

   def deleteFile():...

   def deleteFileAsync():...

   def getDirectoryListing():...

   def getDirectoryListingAsync():...

   def getRelativePath():...

   @staticmethod
   def getRootDirectories():
      # TODO: Make windows function better
      if as3state.platform == 'Windows':
         tempDrives = as3.Array()
         for i in check_output(('fsutil', 'fsinfo', 'drives')).decode('utf-8').strip('\r\n').split(' ')[1:]:
            i = i.strip('\\')
            if i == '':
               continue
            try:
               check_output(('fsutil', 'fsinfo', 'volumeinfo', i))  # This requires admin permissions on the main drive
               tempDrives.push(File(i))
            except CalledProcessError as e:
               if 'not ready' in e.output.decode('utf-8'):
                  continue
               tempDrives.push(File(i))
         return tempDrives
      elif as3state.platform in {'Linux', 'Darwin'}:
         return as3.Array(File('/'))

   def moveTo():...

   def moveToAsync():...

   def moveToTrash():...

   def moveToTrashAsync():...

   def openWithDefaultApplication():...

   def requestPermission():...

   def resolvePath():...

   def toString():...


class FileMode(metaclass=metaclasses._AS3_CONSTANTSOBJECT):
   APPEND = "append"
   READ = "read"
   UPDATE = "update"
   WRITE = "write"


class FileStream:...


class StorageVolume:...


class StorageVolumeInfo:...
