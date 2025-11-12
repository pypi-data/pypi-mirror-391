import math
import random
from as3lib._toplevel.Object import Object


class Math(Object):
   E = 2.71828182845905
   LN10 = 2.302585092994046
   LN2 = 0.6931471805599453
   LOG10E = 0.4342944819032518
   LOG2E = 1.442695040888963387
   PI = 3.141592653589793
   SQRT1_2 = 0.7071067811865476
   SQRT2 = 1.4142135623730951

   @staticmethod
   def abs(val):
      return abs(val)

   @staticmethod
   def acos(val):
      return math.acos(val)

   @staticmethod
   def asin(val):
      return math.asin(val)

   @staticmethod
   def atan(val):
      return math.atan(val)

   @staticmethod
   def atan2(y, x):
      return math.atan2(y, x)

   @staticmethod
   def ceil(val):
      return math.ceil(val)

   @staticmethod
   def cos(angleRadians):
      return math.cos(angleRadians)

   @staticmethod
   def exp(val):
      return math.exp(val)

   @staticmethod
   def floor(val):
      return math.floor(val)

   @staticmethod
   def log(val):
      return math.log(val)

   @staticmethod
   def max(*values):
      return values[0] if len(values) == 1 else max(values)

   @staticmethod
   def min(*values):
      return values[0] if len(values) == 1 else min(values)

   @staticmethod
   def pow(base, power):
      return math.pow(base, power)

   @staticmethod
   def random():
      return random.random()

   @staticmethod
   def round(val):
      return round(val)

   @staticmethod
   def sin(angleRadians):
      return math.sin(angleRadians)

   @staticmethod
   def sqrt(val):
      return math.sqrt(val)

   @staticmethod
   def tan(angleRadians):
      return math.tan(angleRadians)
