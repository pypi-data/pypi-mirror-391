def calculate(neww: float, newh: float, startw: int, starth: int):
   xmult = neww / startw
   ymult = newh / starth
   return ymult if xmult > ymult else xmult


def resizefont(font: int, mult: float):
   return round((font * mult) / 100)


def roundedmultdivide(number, multiplier, diviser):
   return round(number * multiplier) / diviser
