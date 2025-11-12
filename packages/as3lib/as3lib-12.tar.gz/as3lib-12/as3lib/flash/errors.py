from as3lib import Error


class DRMManagerError(Error):
   name = 'DRMManagerError'

   def __init__(self, message):
      super().__init__(message)


class EOFError(Error):
   name = 'EOFError'

   def __init__(self, message):
      super().__init__(message)


class IllegalOperationError(Error):
   name = 'IllegalOperationError'

   def __init__(self, message):
      super().__init__(message)


class InvalidSWFError(Error):
   name = 'InvalidSWFError'

   def __init__(self, message):
      super().__init__(message)


class IOError(Error):
   name = 'IOError'

   def __init__(self, message):
      super().__init__(message)


class MemoryError(Error):
   name = 'MemoryError'

   def __init__(self, message):
      super().__init__(message)


class PermissionError(Error):
   name = 'PermissionError'

   def __init__(self, message):
      super().__init__(message)


class ScriptTimeoutError(Error):
   name = 'ScriptTimeoutError'

   def __init__(self, message):
      super().__init__(message)


class SQLError(Error):
   name = 'SQLError'

   def __init__(self, message):
      super().__init__(message)


class SQLErrorOperation(Error):
   name = 'SQLErrorOperation'

   def __init__(self, message):
      super().__init__(message)


class StackOverflowError(Error):
   name = 'StackOverflowError'

   def __init__(self, message):
      super().__init__(message)
