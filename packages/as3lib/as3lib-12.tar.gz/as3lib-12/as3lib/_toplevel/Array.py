import builtins
from functools import cmp_to_key
from inspect import isfunction
from types import NoneType
from as3lib.helpers import textObject, recursionDepth
from as3lib._toplevel.int import int
from as3lib._toplevel.Constants import undefined
from as3lib._toplevel.Errors import RangeError, Error
from as3lib._toplevel.Object import Object
from as3lib._toplevel.Boolean import Boolean
from as3lib._toplevel.Number import Number
from as3lib._toplevel.uint import uint
from as3lib._toplevel.trace import trace


class Array(list, Object):
   # !Arrays are sparse arrays, meaning there might be an element at index 0 and another at index 5, but nothing in the index positions between those two elements. In such a case, the elements in positions 1 through 4 are undefined, which indicates the absence of an element, not necessarily the presence of an element with the value undefined.
   __slots__ = ('filler')
   CASEINSENSITIVE = 1
   DESCENDING = 2
   UNIQUESORT = 4
   RETURNINDEXEDARRAY = 8
   NUMERIC = 16

   def __init__(self, *args, numElements: builtins.int | int = None, sourceArray: list | tuple = None):
      self.filler = undefined()
      if sourceArray is not None:
         super().__init__(sourceArray)
      elif numElements is None:
         super().__init__(args)
      else:
         if numElements < 0:
            raise RangeError(f'Array; numElements can not be less than 0. numElements is {numElements}')
         else:
            super().__init__([self.filler for i in range(numElements)])

   def __getitem__(self, item):
      if isinstance(item, slice):
         return Array(*[self[i] for i in range(*item.indices(len(self)))])
      else:
         try:
            value = super().__getitem__(item)
            return value if value is not None else undefined()
         except Exception:
            return ''

   def __setitem__(self, item, value):
      if isinstance(item, (builtins.int, int, uint, Number)) and item+1 > self.length:
         '''
         When you assign a value to an array element (for example, my_array[index] = value), if index is a number, and index+1 is greater than the length property, the length property is updated to index+1.
         '''
         self.length = item+1
      super().__setitem__(item, value)

   @property
   def length(self):
      return len(self)

   @length.setter
   def length(self, value: builtins.int | int):
      if value < 0:
         raise RangeError(f'Array.length can not be negative. got {value}')
      elif value == 0:
         self.clear()
      elif len(self) > value:
         while len(self) > value:
            self.pop()
      elif len(self) < value:
         while len(self) < value:
            self.append(self.filler)

   def __add__(self, item):
      if isinstance(item, (list, tuple)):
         return Array(*super().__add__(item))
      return Array(*super().__add__([item]))

   def __iadd__(self, item):
      if isinstance(item, (list, tuple)):
         self.extend(item)
      else:
         self.append(item)
      return self

   def __str__(self):
      return self.toString()

   def __repr__(self):
      return f'as3lib.Array({self.toString()})'

   def setFiller(self, newFiller):
      self.filler = newFiller

   def concat(self, *args):
      '''
      Concatenates the elements specified in the parameters with the elements in an array and creates a new array. If the parameters specify an array, the elements of that array are concatenated. If you don't pass any parameters, the new array is a duplicate (shallow clone) of the original array.
      Parameters:
         *args — A value of any data type (such as numbers, elements, or strings) to be concatenated in a new array.
      Returns:
         Array — An array that contains the elements from this array followed by elements from the parameters.
      '''
      if len(args) == 0:
         return Array(*self)
      if len(args) == 1 and isinstance(args[0], (list, tuple)):  # !check whether this should be "if any element is array" or if it is only one
         return self+list(args[0])
      return self+list(args)

   def every(self, callback: callable):
      '''
      Executes a test function on each item in the array until an item is reached that returns False for the specified function. You use this method to determine whether all items in an array meet a criterion, such as having values less than a particular number.
      Parameters:
         callback:Function — The function to run on each item in the array. This function can contain a simple comparison (for example, item < 20) or a more complex operation, and is invoked with three arguments; the value of an item, the index of an item, and the Array object:
         - function callback(item:*, index:int, array:Array)
      Returns:
         Boolean — A Boolean value of True if all items in the array return True for the specified function; otherwise, False.
      '''
      for i in range(len(self)):
         if callback(self[i], i, self) is False:
            return False
      return True

   def filter(self, callback: callable):
      '''
      Executes a test function on each item in the array and constructs a new array for all items that return True for the specified function. If an item returns False, it is not included in the new array.
      Parameters:
         callback:Function — The function to run on each item in the array. This function can contain a simple comparison (for example, item < 20) or a more complex operation, and is invoked with three arguments; the value of an item, the index of an item, and the Array object:
         - function callback(item:*, index:int, array:Array)
      Returns:
         Array — A new array that contains all items from the original array that returned True.
      '''
      tempArray = Array()
      for i in range(len(self)):
         if callback(self[i], i, self) is True:
            tempArray.push(self[i])
      return tempArray

   def forEach(self, callback: callable):
      '''
      Executes a function on each item in the array.
      Parameters:
         callback:Function — The function to run on each item in the array. This function can contain a simple command (for example, a trace() statement) or a more complex operation, and is invoked with three arguments; the value of an item, the index of an item, and the Array object:
         - function callback(item:*, index:int, array:Array)
      '''
      for i in range(len(self)):
         callback(self[i], i, self)

   def indexOf(self, searchElement, fromIndex: builtins.int | int = 0):
      '''
      Searches for an item in an array using == and returns the index position of the item.
      Parameters:
         searchElement — The item to find in the array.
         fromIndex:int (default = 0) — The location in the array from which to start searching for the item.
      Returns:
         index:int — A zero-based index position of the item in the array. If the searchElement argument is not found, the return value is -1.
      '''
      if fromIndex < 0:
         fromIndex = 0
      for i in range(fromIndex, len(self)):
         if self[i] == searchElement:
            return i
      return -1

   def insertAt(self, index: builtins.int | int, element):
      '''
      Insert a single element into an array.
      Parameters
         index:int — An integer that specifies the position in the array where the element is to be inserted. You can use a negative integer to specify a position relative to the end of the array (for example, -1 is the last element of the array).
         element — The element to be inserted.
      '''
      self.insert(index, element)

   def join(self, sep: str = ',', interpretation: int | builtins.int = 0, _Array=None):
      '''
      Warining: Due to how this works, this will fail if you nest more Arrays than python's maximum recursion depth. If this becomes a problem, you should consider using a different programming language for your project.

      Converts the elements in an array to strings, inserts the specified separator between the elements, concatenates them, and returns the resulting string. A nested array is always separated by a comma (,), not by the separator passed to the join() method.
      Parameters:
         sep (default = ",") — A character or string that separates array elements in the returned string. If you omit this parameter, a comma is used as the default separator.
         interpretation (default = 0) — Which interpretation of the documentation you choose to use. This is an addition parameter added in as3lib because the original documentation isn't clear
               0 — [1,2,3,[4,5,6],7,8,9], sep(+) -> "1+2+3+4,5,6+7+8+9"
               1 — [1,2,3,[4,5,6],7,8,9], sep(+) -> "1+2+3,4,5,6,7+8+9"
      Returns:
         String — A string consisting of the elements of an array converted to strings and separated by the specified parameter.
      '''
      lsep = len(sep)
      result = ''
      if _Array is None:
         _Array = self
      if interpretation == 0:
         for i in _Array:
            if isinstance(i, (list, tuple)):
               result += f'{self.join(_Array=i)}{sep}'
            elif isinstance(i, (undefined, NoneType)):
               result += sep
            else:
               result += f'{i}{sep}'
      elif interpretation == 1:
         for i in _Array:
            if isinstance(i, (list, tuple)):
               if result[-lsep:] == sep:
                  result = result[:-lsep] + ','
               result += f'{self.join(_Array=i)},'
            elif isinstance(i, (undefined, NoneType)):
               result += sep
            else:
               result += f'{i}{sep}'
      if result[-lsep:] == sep:
         return result[:-lsep]
      if result[-1:] == ',':
         return result[:-1]
      return result

   def lastIndexOf(self, searchElement, fromIndex: builtins.int | int = None):
      '''
      Searches for an item in an array, working backward from the last item, and returns the index position of the matching item using ==.
      Parameters:
         searchElement — The item to find in the array.
         fromIndex:int (default = 99*10^99) — The location in the array from which to start searching for the item. The default is the maximum value allowed for an index. If you do not specify fromIndex, the search starts at the last item in the array.
      Returns:
         int — A zero-based index position of the item in the array. If the searchElement argument is not found, the return value is -1.
      '''
      if fromIndex is None:
         fromIndex = len(self)
      elif fromIndex < 0:
         raise RangeError(f'Array.lastIndexOf; fromIndex can not negative. got {fromIndex}')
      index = self[::-1].indexOf(searchElement, len(self)-1-fromIndex)
      return index if index == -1 else len(self)-1-index

   def map(self, callback: callable):
      '''
      Executes a function on each item in an array, and constructs a new array of items corresponding to the results of the function on each item in the original array.
      Parameters:
         callback:Function — The function to run on each item in the array. This function can contain a simple command (such as changing the case of an array of strings) or a more complex operation, and is invoked with three arguments; the value of an item, the index of an item, and the Array object:
         - function callback(item:*, index:int, array:Array)
      Returns:
         Array — A new array that contains the results of the function on each item in the original array.
      '''
      return Array(*[callback(self[i], i, self) for i in range(len(self))])

   def pop(self):
      '''
      Removes the last element from an array and returns the value of that element.
      Returns:
         * — The value of the last element (of any data type) in the specified array.
      '''
      return super().pop(-1)

   def push(self, *args):
      '''
      Adds one or more elements to the end of an array and returns the new length of the array.
      Parameters:
         *args — One or more values to append to the array.
      '''
      self.extend(args)

   def removeAt(self, index: builtins.int | int):
      '''
      Remove a single element from an array. This method modifies the array without making a copy.
      Parameters:
         index:int — An integer that specifies the index of the element in the array that is to be deleted. You can use a negative integer to specify a position relative to the end of the array (for example, -1 is the last element of the array).
      Returns:
         * — The element that was removed from the original array.
      '''
      return super().pop(index)

   def reverse(self):
      '''
      Reverses the array in place.
      Returns:
         Array — The new array.
      '''
      super().reverse()
      return self

   def shift(self):
      '''
      Removes the first element from an array and returns that element. The remaining array elements are moved from their original position, i, to i-1.
      Returns:
         * — The first element (of any data type) in an array.
      '''
      return super().pop(0)

   def slice(self, startIndex: builtins.int | int = 0, endIndex: builtins.int | int = 99*10^99):
      '''
      Returns a new array that consists of a range of elements from the original array, without modifying the original array. The returned array includes the startIndex element and all elements up to, but not including, the endIndex element.
      If you don't pass any parameters, the new array is a duplicate (shallow clone) of the original array.
      Parameters:
         startIndex:int (default = 0) — A number specifying the index of the starting point for the slice. If startIndex is a negative number, the starting point begins at the end of the array, where -1 is the last element.
         endIndex:int (default = 99*10^99) — A number specifying the index of the ending point for the slice. If you omit this parameter, the slice includes all elements from the starting point to the end of the array. If endIndex is a negative number, the ending point is specified from the end of the array, where -1 is the last element.
      Returns:
         Array — An array that consists of a range of elements from the original array.
      '''
      if startIndex < 0:
         startIndex = len(self)+startIndex
      if endIndex < 0:
         endIndex = len(self)+endIndex
      return self[startIndex: endIndex]

   def some(self, callback: callable):
      '''
      Executes a test function on each item in the array until an item is reached that returns True. Use this method to determine whether any items in an array meet a criterion, such as having a value less than a particular number.
      Parameters:
         callback:Function — The function to run on each item in the array. This function can contain a simple comparison (for example item < 20) or a more complex operation, and is invoked with three arguments; the value of an item, the index of an item, and the Array object:
         - function callback(item:*, index:int, array:Array)
      Returns:
         Boolean — A Boolean value of True if any items in the array return True for the specified function; otherwise False.
      '''
      for i in range(len(self)):
         if callback(self[i], i, self) is True:
            return True
      return False

   def sort(self, *args):
      '''
      Warning: Maximum element length is 100000
      '''
      if len(args) == 0:
         '''
         Sorting is case-sensitive (Z precedes a).
         Sorting is ascending (a precedes b).
         The array is modified to reflect the sort order; multiple elements that have identical sort fields are placed consecutively in the sorted array in no particular order.
         All elements, regardless of data type, are sorted as if they were strings, so 100 precedes 99, because "1" is a lower string value than "9".
         '''
         def s(x, y):
            trace('Array.sort: BROKEN: Using Array.sort with no arguements doesn\'t work as intended because the documentation does not include the entire sort order')
            sortorder = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'  # 123456789 #!Where numbers and symbols?
            x, y = str(x), str(y)
            if sortorder.index(x[0]) > sortorder.index(y[0]):
               return 1
            if sortorder.index(x[0]) < sortorder.index(y[0]):
               return -1
            if sortorder.index(x[0]) == sortorder.index(y[0]):
               if len(x) > 1 and len(y) > 1:
                  return s(x[1:], y[1:])
               if len(x) > 1:
                  return 1
               if len(y) > 1:
                  return -1
               return 0
         with recursionDepth(100000):
            super().sort(key=cmp_to_key(s))
      elif len(args) == 1:
         if isinstance(args[0], (bool, Boolean)) and args[0] is True:
            super().sort()
         elif isfunction(args[0]):
            super().sort(key=lambda: cmp_to_key(args[0]))
         elif isinstance(args[0], (builtins.int, float, int, uint, Number)):
            if args[0] == 1:  # CASEINSENSITIVE
               raise NotImplementedError('Array.sort(1)')
            elif args[0] == 2:  # DESCENDING
               raise NotImplementedError('Array.sort(2)')
            elif args[0] == 4:  # UNIQUESORT
               raise NotImplementedError('Array.sort(4)')
            elif args[0] == 8:  # RETURNINDEXEDARRAY
               raise NotImplementedError('Array.sort(8)')
            elif args[0] == 16:  # NUMERIC
               def s(x, y):
                  try:
                     x, y = float(x), float(y)
                  except Exception:
                     raise Error('Array.sort; Can not use Array.NUMERIC (16) when array doesn\'t only contain numbers or strings that convert to numbers')
                  if x > y:
                     return 1
                  if x < y:
                     return -1
                  if x == y:
                     return 0
               super().sort(key=cmp_to_key(s))
            else:
               raise NotImplementedError(f'Array.sort({args[0]})')
         elif type(args[0]) in (tuple, list, Array):
            raise NotImplementedError('Array.sort with multiple sortOptions')
      else:
         raise NotImplementedError('Array.sort with more than one arguement')

   def sortOn():...

   def splice(self, startIndex: builtins.int | int, deleteCount: builtins.int | int, *values):
      '''
      Adds elements to and removes elements from an array. This method modifies the array without making a copy.
      Parameters:
         startIndex:int — An integer that specifies the index of the element in the array where the insertion or deletion begins. You can use a negative integer to specify a position relative to the end of the array (for example, -1 is the last element of the array).
         deleteCount:int — An integer that specifies the number of elements to be deleted. This number includes the element specified in the startIndex parameter. If you do not specify a value for the deleteCount parameter, the method deletes all of the values from the startIndex element to the last element in the array. If the value is 0, no elements are deleted.
         *values — An optional list of one or more comma-separated values to insert into the array at the position specified in the startIndex parameter. If an inserted value is of type Array, the array is kept intact and inserted as a single element. For example, if you splice an existing array of length three with another array of length three, the resulting array will have only four elements. One of the elements, however, will be an array of length three.
      Returns:
         Array — An array containing the elements that were removed from the original array.
      '''
      if startIndex < 0:
         startIndex = len(self) + startIndex
      if deleteCount < 0:
         raise RangeError(f'Array.splice; deleteCount can not negative. got {deleteCount}')
      removedValues = self[startIndex: startIndex+deleteCount]
      self[startIndex: startIndex+deleteCount] = values
      return removedValues

   def toList(self):
      return list(self)

   def toLocaleString(self):
      '''
      Returns a string that represents the elements in the specified array. Every element in the array, starting with index 0 and ending with the highest index, is converted to a concatenated string and separated by commas. In the ActionScript 3.0 implementation, this method returns the same value as the Array.toString() method.
      Returns:
         String — A string of array elements.
      '''
      return self.toString()

   def __listtostr(self, l):
      with textObject() as res:
         for i in l:
            if isinstance(i, (list, tuple)):
               res.write(self.__listtostr(i) + ',')
               continue
            if isinstance(i, (undefined, NoneType)):
               res.write(',')
               continue
            res.write(f'{i},')
         return res.get()[:-1]

   def toString(self, formatLikePython: bool | Boolean = False, interpretation=1):
      '''
      Returns a string that represents the elements in the specified array. Every element in the array, starting with index 0 and ending with the highest index, is converted to a concatenated string and separated by commas. To specify a custom separator, use the Array.join() method.
      Returns:
         String — A string of array elements.
      '''
      if formatLikePython is True:
         return super().__str__(self)
      if interpretation == 1:
         return self.__listtostr(self)
      return super().__str__(self)[1:-1].replace(', ', ',')

   def unshift(self, *args):
      '''
      Adds one or more elements to the beginning of an array and returns the new length of the array. The other elements in the array are moved from their original position, i, to i+1.
      Parameters:
         *args — One or more numbers, elements, or variables to be inserted at the beginning of the array.
      Returns:
         int — An integer representing the new length of the array.
      '''
      tempArray = [*args, *self]
      self.clear()
      self.extend(tempArray)
      return len(self)
