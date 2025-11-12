import as3lib as as3
from as3lib import as3state, Error, metaclasses
from as3lib.flash.events import EventDispatcher, TimerEvent
from datetime import datetime
from threading import Timer as timedExec
from miniamf import util
from miniamf.amf3 import ByteArray as _ByteArray


class ByteArray:...  # dummy class


def clearInterval():...


def clearTimeout():...


def describeType():...


def escapeMultiByte():...


def getDefinitionByName():...


def getQualifiedClassName():...


def getQualifiedSuperclassName():...


def getTimer():
   return int(util.get_timestamp(datetime.now()) * 1000) - as3state.startTime


def setInterval():...


def setTimeout():...


def unescapeMultiByte():...


class IDataInput:...


class IDataOutput:...


class ByteArray(_ByteArray):
   defaultObjectEncoding = 3  # This can be set globally

   @property
   def bytesAvailable(self):
      return self.remaining()

   @property
   def endian(self):
      return super().endian

   @endian.setter
   def endian(self, endian):
      super().endian = endian

   @property
   def length(self):
      return len(self)

   @length.setter
   def length(self, value: int):...

   @property
   def position(self):
      return self.tell()

   @position.setter
   def position(self, value):
      self.seek(value)

   @property
   def shareable(self):
      return self.__sharable

   @shareable.setter
   def shareable(self, value: bool):
      self.__sharable = value

   def __init__(self, data=None):
      super().__init__(data)
      self.objectEncoding = ByteArray.defaultObjectEncoding  # This currently does nothing

   def __repr__(self):
      return f'ByteArray({self.getvalue()})'

   def atomicCompareAndSwapIntAt(self, byteIndex: int, expectedValue: int, newValue: int):
      if byteIndex % 4 != 0 or byteIndex < 0:
         raise as3.ArguementError('ByteArray.atomicCompareAndSwapIntAt; byteIndex must be a multiple of 4 and can not be negative.')
      ...

   def atomicCompareAndSwapLength(self, expectedLength: int, newLength: int):
      '''
      In a single atomic operation, compares this byte array's length with a provided value and, if they match, changes the length of this byte array.

      This method is intended to be used with a byte array whose underlying memory is shared between multiple workers (the ByteArray instance's shareable property is true). It does the following:

         1) Reads the integer length property of the ByteArray instance
         2) Compares the length to the value passed in the expectedLength argument
         3) If the two values are equal, it changes the byte array's length to the value passed as the newLength parameter, either growing or shrinking the size of the byte array
         4) Otherwise, the byte array is not changed

      All these steps are performed in one atomic hardware transaction. This guarantees that no operations from other workers make changes to the contents of the byte array during the compare-and-resize operation.

      Parameters
         expectedLength:int — the expected value of the ByteArray's length property. If the specified value and the actual value match, the byte array's length is changed.
         newLength:int — the new length value for the byte array if the comparison succeeds
      Returns
         int — the previous length value of the ByteArray, regardless of whether or not it changed
      '''
      oldlen = self.length
      if self.length == expectedLength:
         self.length = newLength
      return oldlen

   def clear(self):
      'Clears the contents of the byte array and resets the length and position properties to 0. Calling this method explicitly frees up the memory used by the ByteArray instance.'
      self.truncate(0)

   def compress(self, algorithm: str):
      if algorithm != 'zlib':
         raise NotImplementedError('The underlying stream currently only supports zlib compression.')
      self.compressed = True

   def deflate():...

   def inflate():...

   def readBytes(self, bytes: ByteArray, offset=0, length=0):
      bytes.seek(offset)
      bytes.write(self.read(length))

   def toJSON(self, k: str):
      '''
      Provides an overridable method for customizing the JSON encoding of values in an ByteArray object.

      The JSON.stringify() method looks for a toJSON() method on each object that it traverses. If the toJSON() method is found, JSON.stringify() calls it for each value it encounters, passing in the key that is paired with the value.

      ByteArray provides a default implementation of toJSON() that simply returns the name of the class. Because the content of any ByteArray requires interpretation, clients that wish to export ByteArray objects to JSON must provide their own implementation. You can do so by redefining the toJSON() method on the class prototype.

      The toJSON() method can return a value of any type. If it returns an object, stringify() recurses into that object. If toJSON() returns a string, stringify() does not recurse and continues its traversal.

      Parameters
         k:String — The key of a key/value pair that JSON.stringify() has encountered in its traversal of this object

      Returns
         * — The class name string.
      '''
      return 'ByteArray'

   def toString(self):...

   def uncompress(self, algorithm: str):
      if algorithm != 'zlib':
         raise NotImplementedError('The underlying stream currently only supports zlib compression.')
      self.compressed = False

   def writeBytes(self, bytes: ByteArray, offset=0, length=0):
      startpos = bytes.tell()
      bytes.seek(offset)
      self.write(bytes.read(length))
      bytes.seek(startpos)  # !I don't know if it is supposed to do this


class CompressionAlgorithm(metaclass=metaclasses._AS3_CONSTANTSOBJECT):
   DEFLATE = 'deflate'
   LZMA = 'lzma'
   ZLIB = 'zlib'


class Dictionary(dict):
   def __init__(self, weakKeys: as3.allBoolean = False):
      return super().__init__()

   def __getitem__(self, item):
      return self.get(item)  # I think this is how actionscript does it but I'm not sure

   def toJSON(self, k: str):
      return 'Dictionary'


class Endian(metaclass=metaclasses._AS3_CONSTANTSOBJECT):
   BIG_ENDIAN = 'bigEndian'
   LITTLE_ENDIAN = 'littleEndian'


class Timer(EventDispatcher):
   # TODO: If repeatCount is set to a total that is the same or less then currentCount the timer stops and will not fire again.
   @property
   def currentCount(self):
      return self._currentCount

   @property
   def delay(self):
      return self._delay

   @delay.setter
   def delay(self, number_ms: as3.allNumber):
      if self.running:
         self.stop()
         self._delay = number_ms
         self.start()
      else:
         self._delay = number_ms

   @property
   def repeatCount(self):
      return self._repeatCount

   @repeatCount.setter
   def repeatCount(self, number: as3.allInt):
      self._repeatCount = number

   @property
   def running(self):
      return self._running

   def _TimerTick(self):
      self._currentCount += 1
      self.dispatchEvent(self.timer)
      if self.currentCount >= self.repeatCount and self.repeatCount != 0:
         self.dispatchEvent(self.timerComplete)
      else:
         del self._timer
         self._timer = timedExec(self.delay/1000, self._TimerTick)
         self._timer.start()

   def __init__(self, delay: as3.allNumber, repeatCount: as3.allInt = 0):
      super().__init__()
      self._currentCount = 0
      if delay < 0:
         raise Error()
      self._delay = delay
      self._repeatCount = repeatCount
      self._running = False
      self.timer = TimerEvent('timer', False, False)
      self.timerComplete = TimerEvent('timerComplete', False, False)

   def reset(self):
      self.stop()
      self._currentCount = 0

   def start(self):
      if not self.running and (self.currentCount < self.repeatCount or self.repeatCount == 0):
         self._timer = timedExec(self.delay/1000, self._TimerTick)
         self._running = True
         self._timer.start()

   def stop(self):
      if self.running:
         self._timer.cancel()
         del self._timer
         self._running = False
