from as3lib import Object
from as3lib.metaclasses import _AS3_CONSTANTSOBJECT
import math


class ColorTransform:...


class Matrix:...


class Matrix3D:...


class Orientation3D(metaclass=_AS3_CONSTANTSOBJECT):
   AXIS_ANGLE = 'axisAngle'
   EULER_ANGLES = 'eulerAngles'
   QUATERNION = 'quanternion'


class PerspectiveProjection:...


class Point(Object):
   @property
   def length(self):
      return math.sqrt(self.x ** 2 + self.y ** 2)

   @property
   def x(self):
      return self._x

   @x.setter
   def x(self, value):
      self._x = value

   @property
   def y(self):
      return self._y

   @y.setter
   def y(self, value):
      self._y = value

   def __init__(self, x=0, y=0):
      self._x = x
      self._y = y

   def add(self, v: Point):
      return Point(self.x + v.x, self.y + v.y)

   def clone(self):
      return Point(self.x, self.y)

   def copyFrom(self, sourcePoint: Point):...

   @staticmethod
   def distance(pt1: Point, pt2: Point):
      return math.sqrt((pt2.x-pt1.x) ** 2 + (pt2.y-pt1.y) ** 2)

   def equals(self, toCompare: Point):
      return self.x == toCompare.x and self.y == toCompare.y

   @staticmethod
   def interpolate(pt1: Point, pt2: Point, f):...

   def normalize(self, thickness):...

   def offset(self, dx, dy):
      self.x = self.x + dx
      self.y = self.y + dy

   @staticmethod
   def polar(len, angle):
      return Point(len * math.sin(angle), len * math.cos(angle))

   def setTo(self, xa, ya):
      self.x = xa
      self.y = ya

   def subtract(self, v: Point):
      return Point(self.x - v.x, self.y - v.y)

   def toString(self):
      return f'(x={self.x}, y={self.y})'


class Rectangle(Object):
   @property
   def bottom(self):
      return self.y + self.height

   @bottom.setter
   def bottom(self, value):
      self.height = value - self.y

   @property
   def bottomRight(self):...

   @property
   def height(self):
      return self._height

   @height.setter
   def height(self, value):
      self._height = value

   @property
   def left(self):...

   @property
   def right(self):
      return self.x + self.width

   @right.setter
   def right(self, value):
      self.width = value - self.x

   @property
   def size(self):
      return Point(self.width, self.height)

   @size.setter
   def size(self, value: Point):
      self.width = value.x
      self.height = value.y

   @property
   def top(self):...

   @property
   def topLeft(self):
      return Point(self.x, self.y)

   @topLeft.setter
   def topLeft(self, value: Point):
      self.x = value.x
      self.y = value.y

   @property
   def width(self):
      return self._width

   @width.setter
   def width(self, value):
      self._width = value

   @property
   def x(self):
      return self._x

   @x.setter
   def x(self, value):
      self._x = value

   @property
   def y(self):
      return self._y

   @y.setter
   def y(self, value):
      self._y = value

   def __init__(self, x=0, y=0, width=0, height=0):
      self._x = x
      self._y = y
      self._width = width
      self._height = height

   def clone(self):
      return Rectangle(self.x, self.y, self.width, self.height)

   def contains(self, x, y):
      # TODO: Make sure that this is correct. I am unsure if the boundaries are considered inside of the rectangle.
      # If the boundaries are not inside the rectangle, this should be < and > instead of <= and >=.
      return x >= self.x and x <= self.right and y >= self.y and y <= self.bottom

   def containsPoint(self, point: Point):
      return self.contains(point.x, point.y)

   def containsRect(self, rect: Rectangle):...

   def copyFrom(self, sourceRect: Rectangle):
      self.x = sourceRect.x
      self.y = sourceRect.y
      self.width = sourceRect.width
      self.height = sourceRect.height

   def equals(self, toCompare: Rectangle):
      return self.x == toCompare.x and self.y == toCompare.y and self.width == toCompare.width and self.height == toCompare.height

   def inflate(self, dx, dy):...

   def inflatePoint(self, point: Point):...

   def intersection(self, toIntersect: Rectangle):...

   def intersects(self, toIntersect: Rectangle):...

   def isEmpty(self):
      return self.width <= 0 or self.height <= 0

   def offset(self, dx, dy):
      self.x = dx
      self.y = dy

   def offsetPoint(self, point: Point):
      self.x = point.x
      self.y = point.y

   def setEmpty(self):
      self.x = 0
      self.y = 0
      self.width = 0
      self.height = 0

   def setTo(self, xa, ya, widtha, heighta):
      self.x = xa
      self.y = ya
      self.width = widtha
      self.height = heighta

   def toString(self):
      return f'(x={self.x}, y={self.y}, w={self.width}, h={self.height})'

   def union(self, toUnion: Rectangle):
      if self.isEmpty() or toUnion.isEmpty():
         ...  # The documentation says empty rectangles are ignored. I'm not sure what this is supposed to return here
      ...


class Transform:...


class Utils3D:...


class Vector3D:...
