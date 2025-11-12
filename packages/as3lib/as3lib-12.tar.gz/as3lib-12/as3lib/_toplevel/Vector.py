from as3lib._toplevel.Object import Object
from as3lib._toplevel.Constants import null
from as3lib._toplevel.Errors import RangeError, TypeError


class Vector(list, Object):
   '''
   AS3 Vector datatype.

   Since python does not allow for multiple things to have the same name, the function and the class constructor have been merged. Here's how it works now:
     - If sourceArray is defined, the behavior for the function is used and the arguements are ignored.
     - The arguement "superclass" is provided for convinience. It makes the Vector object check the type as a superclass instead of as a strict type. Passing sourceArray sets this to true
   '''
   def __init__(self, type, length=0, fixed=False, superclass=False, sourceArray: list | tuple = None):
      self.__type = type
      if sourceArray is not None:
         self.__superclass = True
         super().__init__(sourceArray)  # !Temporary, must convert first in real implementation
      else:
         self.__superclass = superclass
         super().__init__((null() for i in range(length)))
      self.fixed = fixed

   @property
   def _type(self):
      return self.__type

   @property
   def fixed(self):
      return self.__fixed

   @fixed.setter
   def fixed(self, value):
      self.__fixed = value

   @property
   def length(self):
      return len(self)

   @length.setter
   def length(self, value):
      if self.fixed:
         raise RangeError('Can not set vector length while fixed is set to true.')
      if value > 4294967296:
         raise RangeError('New vector length outside of accepted range (0-4294967296).')
      if len(self) > value:
         while len(self) > value:
            self.pop()
      elif len(self) < value:
         while len(self) < value:
            self.append(null())

   def __repr__(self):
      return f'as3lib.Vector({self.__type}, {self})'

   def __getitem__(self, item):
      if isinstance(item, slice):...
      else:
         return super().__getitem__(item)

   def __setitem__(self, item, value):
      if self.__superclass:
         if isinstance(value, (self._type, null)):
            super().__setitem__(item, value)
      else:
         if isinstance(value, null) or type(value) is self._type:
            super().__setitem__(item, value)

   def concat(self, *args):
      temp = Vector(self._type, superclass=True)
      temp.extend(self)
      if len(args) > 0:
         for i in args:
            if isinstance(i, Vector) and issubclass(i._type, self._type):
               temp.extend(i)
            elif not isinstance(i, Vector):
               raise TypeError('Vector.concat; One or more arguements are not of type Vector')
            else:
               raise TypeError('Vector.concat; One or more arguements do not have a base type that can be converted to the current base type.')
      temp.fixed = self.fixed
      return temp

   def every(self, callback, thisObject):
      for i in range(len(self)):
         if callback(self[i], i, self) is False:
            return False
      return True

   def filter(self, callback, thisObject):
      tempVector = Vector(type_=self._type, superclass=self.__superclass)
      for i in range(len(self)):
         if callback(self[i], i, self) is True:
            tempVector.push(self[i])
      return tempVector

   def forEach(self, callback, thisObject):
      for i in range(len(self)):
         callback(self[i], i, self)

   def indexOf(self, searchElement, fromIndex=0):
      if fromIndex < 0:
         fromIndex = len(self) - fromIndex
      for i in range(fromIndex, len(self)):
         if self[i] == searchElement:
            return i
      return -1

   def insertAt(self, index, element):
      if self.fixed:
         raise RangeError('insertAt can not be called on a Vector with fixed set to true.')
      elif self.__superclass:
         if isinstance(element, (self._type, null)):...
      else:...

   def join(self, sep: str = ','):...

   def lastIndexOf(self, searchElement, fromIndex=None):
      if fromIndex is None:
         fromIndex = len(self)
      elif fromIndex < 0:
         fromIndex = len(self) - fromIndex
      ...
      # index = self[::-1].indexOf(searchElement,len(self)-1-fromIndex)
      # return index if index == -1 else len(self)-1-index

   def map(self, callback, thisObject):
      tempVect = Vector(type_=self._type, length=len(self), superclass=self.__superclass)
      for i in range(len(self)):
         tempVect[i] = callback(self[i], i, self)
      return tempVect

   def pop(self):
      if self.fixed:
         raise RangeError('pop can not be called on a Vector with fixed set to true.')
      return super().pop(-1)

   def push(self, *args):
      if self.fixed:
         raise RangeError('push can not be called on a Vector with fixed set to true.')
      # !Check item types
      self.extend(args)
      return len(self)

   def removeAt(self, index):
      if self.fixed:
         raise RangeError('removeAt can not be called on a Vector with fixed set to true.')
      elif False:  # !Index out of bounds
         raise RangeError('index is out of bounds.')
      return super().pop(index)

   def reverse(self):
      super().reverse()
      return self

   def shift(self):
      if self.fixed:
         raise RangeError('shift can not be called on a Vector with fixed set to true.')
      return super().pop(0)

   def slice():...

   def some(self, callback, thisObject):
      for i in range(len(self)):
         if callback(self[i], i, self) is True:
            return True
      return False

   def sort():...
   def splice():...
   def toLocaleString():...
   def toString():...

   def unshift(self, *args):
      if self.fixed:
         raise RangeError('unshift can not be called on a Vector with fixed set to true.')
      argsOK = True
      if self.__superclass:
         for i in args:
            if not isinstance(i, (self._type, null)):
               argsOK = False
               break
      else:
         for i in args:
            if not (isinstance(i, null) or type(i) is self._type):
               argsOK = False
               break
      if not argsOK:
         raise TypeError('One or more args is not of the Vector\'s base type.')
      tempVect = (*args, *self)
      self.clear()
      self.extend(tempVect)
      return len(self)
