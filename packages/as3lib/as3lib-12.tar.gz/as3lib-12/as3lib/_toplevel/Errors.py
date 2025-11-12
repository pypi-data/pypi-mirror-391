from as3lib._toplevel.trace import errorTrace
from as3lib._toplevel.Object import Object
import traceback


def _genErrNum():
   i = 0
   while True:
      yield i
      i += 1


_ErNo = _genErrNum()


# !Implement the debug functionality as specified here https://help.adobe.com/en_US/FlashPlatform/reference/actionscript/3/Error.html
class Error(Exception, Object):
   name = 'Error'
   message = 'Error'
   errorID = 0

   def __init__(self, message="", id=0):
      self.errorID = next(_ErNo) if id == 0 else id
      self.message = message
      errorTrace(self.toString())

   def getStackTrace(self):
      return f'{self.name}: Error #{self.errorID}: {self.message}\n{"".join(traceback.format_tb(self.__traceback__))}'

   def toString(self):
      return f'{self.name}: {self.message}'


class ArgumentError(Error):
   name = 'ArguementError'

   def __init__(self, message):
      super().__init__(message)


class DefinitionError(Error):
   name = 'DefinitionError'

   def __init__(self, message):
      super().__init__(message)


class EvalError(Error):
   name = 'EvalError'

   def __init__(self, message):
      super().__init__(message)


class RangeError(Error):
   name = 'RangeError'

   def __init__(self, message):
      super().__init__(message)


class ReferenceError(Error):
   name = 'ReferenceError'

   def __init__(self, message):
      super().__init__(message)


class SecurityError(Error):
   name = 'SecurityError'

   def __init__(self, message):
      super().__init__(message)


class SyntaxError(Error):
   name = 'SyntaxError'

   def __init__(self, message):
      super().__init__(message)


class TypeError(Error):
   name = 'TypeError'

   def __init__(self, message):
      super().__init__(message)


class URIError(Error):
   name = 'URIError'

   def __init__(self, message):
      super().__init__(message)


class VerifyError(Error):
   name = 'VerifyError'

   def __init__(self, message):
      super().__init__(message)
