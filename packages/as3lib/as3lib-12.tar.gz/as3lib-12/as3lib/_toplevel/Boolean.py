from types import NoneType
from as3lib._toplevel.int import int
from as3lib._toplevel.Constants import undefined, null, NaN
from as3lib._toplevel.Object import Object
from as3lib._toplevel.Number import Number
from as3lib._toplevel.uint import uint


class Boolean(Object):
   __slots__ = ('_value')

   def __init__(self, expression=False):
      self._value = self._Boolean(expression)

   def __str__(self):
      return str(self._value).lower()

   def __repr__(self):
      return f'as3lib.Boolean({self._value})'

   def __getitem__(self):
      return self._value

   def __setitem__(self, value):
      self._value = value

   def __bool__(self):
      return self._value

   def __float__(self):
      return float(self._value)

   def __int__(self):
      return int(self._value)

   def _Boolean(self, expression=None):
      if isinstance(expression, bool):
         return expression
      if isinstance(expression, (uint, Number)):
         return expression != 0
      if isinstance(expression, (NaN, null, undefined, NoneType)):
         return False
      if hasattr(expression, '__bool__'):
         return bool(expression)

   def toString(self):
      return str(self._value).lower()

   def valueOf(self):
      return self._value
