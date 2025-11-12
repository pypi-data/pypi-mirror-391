from numpy import base_repr
import builtins
import math
from as3lib._toplevel.Object import Object
from as3lib._toplevel.Constants import NaN, Infinity, NInfinity
from as3lib._toplevel.Errors import RangeError, TypeError
from as3lib._toplevel.Number import Number
from as3lib._toplevel.uint import uint


class int(Object):
   # !Make this return a Number if the result is a float
   # !Implement checks for max and min value
   __slots__ = ('_value')
   MAX_VALUE = 2147483647
   MIN_VALUE = -2147483648

   def __init__(self, value=0):
      self._value = self._int(value)

   def __str__(self):
      return f'{self._value}'

   def __repr__(self):
      return f'as3lib.int({self._value})'

   def __getitem__(self):
      return self._value

   def __setitem__(self, value):
      self._value = self._int(value)

   def __add__(self, value):
      return int(self._value + self._int(value))

   def __sub__(self, value):
      return int(self._value - self._int(value))

   def __mul__(self, value):
      return int(self._value * self._int(value))

   def __truediv__(self, value):
      if value == 0:
         if self._value == 0:
            return NaN()
         if self._value > 0:
            return Infinity()
         if self._value < 0:
            return NInfinity()
      try:
         return int(self._value / self._int(value))
      except Exception:
         raise TypeError(f'Can not divide int by {type(value)}')

   def __float__(self):
      return float(self._value)

   def __int__(self):
      return self._value

   def __bool__(self):
      return bool(self._value)

   def _int(self, value):
      # !It is unclear if most of this is included here, most is from the Number class
      if isinstance(value, (NaN, Infinity, NInfinity)):
         return value
      if isinstance(value, (builtins.int, int)):
         return value
      if isinstance(value, (float, Number)):
         return math.floor(value)
      if isinstance(value, str):
         try:
            return builtins.int(value)
         except Exception:
            raise TypeError(f'Can not convert string {value} to integer')
      raise TypeError(f'Can not convert type {type(value)} to integer')

   def toExponential(self, fractionDigits: builtins.int | int):
      if fractionDigits < 0 and fractionDigits > 20:
         raise RangeError('fractionDigits is outside of acceptable range')
      temp = str(self._value)
      if temp[0] == '-':
         whole = temp[:2]
         temp = temp[2:]
      else:
         whole = temp[:1]
         temp = temp[1:]
      decpos = temp.find('.')
      if decpos == -1:
         exponent = len(temp)
      else:
         exponent = len(temp[:decpos])
      temp = temp.replace('.', '') + '0'*20
      if fractionDigits > 0:
         return f'{whole}.{"".join([temp[i] for i in range(fractionDigits)])}e+{exponent}'
      return f'{whole}e+{exponent}'

   def toFixed(self, fractionDigits: builtins.int | int):
      if fractionDigits < 0 or fractionDigits > 20:
         raise RangeError('fractionDigits is outside of acceptable range')
      if fractionDigits == 0:
         return f'{self._value}'
      return f'{self._value}.{"0"*fractionDigits}'

   def toPrecision(self, precision: builtins.int | int | uint):
      if precision < 1 or precision > 21:
         raise RangeError('fractionDigits is outside of acceptable range')
      temp = str(self._value)
      length = len(temp)
      if precision < length:
         return self.toExponential(precision-1)
      if precision == length:
         return temp
      return f'{temp}.{"0"*(precision-length)}'

   def toString(self, radix: builtins.int | int | uint = 10):
      if radix <= 36 and radix >= 2:
         return base_repr(self._value, base=radix)

   def valueOf(self):
      return self._value
