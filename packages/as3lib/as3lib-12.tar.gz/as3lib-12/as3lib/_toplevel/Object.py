class Object:
   # ActionScript3 Base object
   def __init__(self):...

   def hasOwnProperty(self, name: str):...

   def isPrototypeOf(self, theClass):
      return isinstance(theClass, self.__class__)

   def propertyIsEnumerable(self, name: str):...

   def setPropertyIsEnumerable(self, name: str, isEnum=True):...

   def toLocaleString(self):
      return self.toString()

   def toString(self):...

   def valueOf(self):
      return self
