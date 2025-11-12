import builtins
from types import NoneType
from as3lib._toplevel.Object import Object
from as3lib._toplevel.Constants import NaN, null, undefined, Infinity, NInfinity
from as3lib._toplevel.Errors import TypeError


class Number(Object):
   __slots__ = ('_value')
   MAX_VALUE = 1.79e308
   MIN_VALUE = 5e-324
   NaN = NaN()
   NEGATIVE_INFINITY = NInfinity()
   POSITIVE_INFINITY = Infinity()

   def __init__(self, num=None):
      self._value = self._Number(num)

   def __str__(self):
      if isinstance(self._value, (NaN, Infinity, NInfinity)):
         return str(self._value)
      if self._value.is_integer():
         return f'{builtins.int(self._value)}'
      return f'{self._value}'

   def __repr__(self):
      return f'as3lib.Number({self._value})'

   def __getitem__(self):
      return self._value

   def __setitem__(self, value):
      self._value = self._Number(value)

   def __add__(self, value):
      try:
         return Number(self._value + float(value))
      except Exception:
         raise TypeError(f'can not add {type(value)} to Number')

   def __sub__(self, value):
      try:
         return Number(self._value - float(value))
      except Exception:
         raise TypeError(f'can not subtract {type(value)} from Number')

   def __mul__(self, value):
      try:
         return Number(self._value * float(value))
      except Exception:
         raise TypeError(f'can not multiply Number by {type(value)}')

   def __truediv__(self, value):
      if value == 0:
         if self._value == 0:
            return Number(NaN())
         if self._value > 0:
            return Number(Infinity())
         if self._value < 0:
            return Number(NInfinity())
      try:
         return Number(self._value / float(value))
      except Exception:
         raise TypeError(f'Can not divide Number by {type(value)}')

   def __float__(self):
      return float(self._value)

   def __int__(self):
      return builtins.int(self._value)

   def __bool__(self):
      bool(self._value)

   def _Number(self, expression):
      if isinstance(expression, (NInfinity, Infinity, float, Number)):
         return expression
      if isinstance(expression, (NoneType, NaN, undefined)):
         return NaN()
      if isinstance(expression, null):
         return 0.0
      if hasattr(expression, '__float__'):
         return float(expression)
      if isinstance(expression, str):
         if expression == "":
            return 0.0
         try:
            return float(expression)
         except Exception:
            return NaN()

   def toExponential(self):...
   def toFixed(self):...
   def toPrecision():...

   def toString(self, radix=10):  # !Fix this
      return str(self._value)

   def valueOf(self):
      return self._value
