_NaN_value = 1e300000 / -1e300000
_NegInf_value = -1e300000
_PosInf_value = 1e300000
true = True
false = False


class NInfinity:...
class Infinity:...


class NInfinity:
   __slots__ = ("__value")

   def __init__(self):
      self.__value = _NegInf_value

   def __str__(self):
      return "-Infinity"

   def __repr__(self):
      return self.__value

   def __lt__(self, value):
      return not isinstance(value, NInfinity)

   def __le__(self, value):
      return not isinstance(value, NInfinity)

   def __eq__(self, value):
      return isinstance(value, NInfinity)

   def __ne__(self, value):
      return isinstance(value, NInfinity)

   def __gt__(self, value):
      return False

   def __ge__(self, value):
      return not isinstance(value, NInfinity)

   def __bool__(self):
      return True

   def __add__(self, value):
      return self

   def __radd__(self, value):
      return self

   def __iadd__(self, value):
      return self

   def __sub__(self, value):
      return self

   def __mul__(self, value):
      return self

   def __matmul__(self, value):
      return self

   def __truediv__(self, value):
      return self

   def __floordiv__(self, value):
      return self

   def __mod__(self, value):
      return self

   def __divmod__(self, value):
      return self

   def __pow__(self, value):
      return self

   def __lshift__(self, value):
      return self

   def __rshift__(self, value):
      return self

   def __and__(self, value):
      return True and value

   def __or__(self, value):
      return True

   def __xor__(self, value):
      return not value

   def __neg__(self):
      return self

   def __pos__(self):
      return NInfinity()

   def __abs__(self):
      return Infinity()

   def __invert__(self):
      return Infinity()

   def __complex__(self):
      return self

   def __int__(self):
      return self

   def __float__(self):
      return self

   def __round__(self):
      return self

   def __floor__(self):
      return self

   def __ceil__(self):
      return self


class Infinity:
   __slots__ = ("__value")

   def __init__(self):
      self.__value = _PosInf_value

   def __str__(self):
      return "Infinity"

   def __repr__(self):
      return self.__value

   def __lt__(self, value):
      return False

   def __le__(self, value):
      return isinstance(value, Infinity)

   def __eq__(self, value):
      return isinstance(value, Infinity)

   def __ne__(self, value):
      return not isinstance(value, Infinity)

   def __gt__(self, value):
      return not isinstance(value, Infinity)

   def __ge__(self, value):
      return True

   def __bool__(self):
      return True

   def __add__(self, value):
      return self

   def __radd__(self, value):
      return self

   def __iadd__(self, value):
      return self

   def __sub__(self, value):
      return self

   def __mul__(self, value):
      return self

   def __matmul__(self, value):
      return self

   def __truediv__(self, value):
      return self

   def __floordiv__(self, value):
      return self

   def __mod__(self, value):
      return self

   def __divmod__(self, value):
      return self

   def __pow__(self, value):
      return self

   def __lshift__(self, value):
      return self

   def __rshift__(self, value):
      return self

   def __and__(self, value):
      return True and value

   def __or__(self, value):
      return True

   def __xor__(self, value):
      return not value

   def __neg__(self):
      return NInfinity()

   def __pos__(self):
      return self

   def __abs__(self):
      return self

   def __invert__(self):
      return NInfinity()

   def __complex__(self):
      return self

   def __int__(self):
      return self

   def __float__(self):
      return self

   def __round__(self):
      return self

   def __floor__(self):
      return self

   def __ceil__(self):
      return self


class NaN:
   __slots__ = ("__value")

   def __init__(self):
      self.__value = _NaN_value

   def __str__(self):
      return "NaN"

   def __repr__(self):
      return f"{self.__value}"

   def __lt__(self, value):
      return False

   def __le__(self, value):
      return False

   def __eq__(self, value):
      return False

   def __ne__(self, value):
      return True

   def __gt__(self, value):
      return False

   def __ge__(self, value):
      return False

   def __bool__(self):
      return False

   def __contains__(self, value):
      return False

   def __add__(self, value):
      return self

   def __radd__(self, value):
      return self

   def __iadd__(self, value):
      return self

   def __sub__(self, value):
      return self

   def __mul__(self, value):
      return self

   def __matmul__(self, value):
      return self

   def __truediv__(self, value):
      return self

   def __floordiv__(self, value):
      return self

   def __mod__(self, value):
      return self

   def __divmod__(self, value):
      return self

   def __pow__(self, value):
      return self

   def __lshift__(self, value):
      return self

   def __rshift__(self, value):
      return self

   def __and__(self, value):
      return False

   def __xor__(self, value):
      return False

   def __or__(self, value):
      return False

   def __neg__(self):
      return self

   def __pos__(self):
      return self

   def __abs__(self):
      return self

   def __invert__(self):
      return

   def __complex__(self):
      return self

   def __int__(self):
      return self

   def _uint(self):
      return 0

   def __float__(self):
      return self

   def __round__(self):
      return self

   def __trunc__(self):
      return self

   def __floor__(self):
      return self

   def __ceil__(self):
      return self


class undefined:
   __slots__ = ("value")

   def __init__(self):
      self.value = None

   def __str__(self):
      return "undefined"

   def __repr__(self):
      return "as3lib.undefined"


class null:
   __slots__ = ("value")

   def __init__(self):
      self.value = None

   def __str__(self):
      return "null"

   def __repr__(self):
      return "as3lib.null"
