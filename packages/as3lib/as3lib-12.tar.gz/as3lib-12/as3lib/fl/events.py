from as3lib import metaclasses
from as3lib.flash.events import _AS3_BASEEVENT, ErrorEvent


# Classes
class ListEvent(_AS3_BASEEVENT):
   ITEM_CLICK = 'itemClick'
   ITEM_DOUBLE_CLICK = 'itemDoubleClick'
   ITEM_ROLL_OUT = 'itemRollOut'
   ITEM_ROLL_OVER = 'itemRollOver'
   _INTERNAL_allowedTypes = {'itemClick', 'itemDoubleClick', 'itemRollOut', 'itemRollOver'}

   @property
   def columnIndex(self):
      return self._columnIndex

   @property
   def index(self):
      return self._index

   @property
   def item(self):
      return self._item

   @property
   def rowIndex(self):
      return self._rowIndex

   def __init__(self, type, bubbles=False, cancelable=False, columnIndex=-1, rowIndex=-1, index=-1, item=None):
      super().__init__(type, bubbles, cancelable)
      self._columnIndex = columnIndex
      self._index = index
      self._item = item
      self._rowIndex = rowIndex

   def toString(self):
      return self.formatToString('ListEvent', 'type', 'bubbles', 'cancelable', 'columnIndex', 'rowIndex')


class ColorPickerEvent(_AS3_BASEEVENT):
   CHANGE = 'change'
   ENTER = 'enter'
   ITEM_ROLL_OUT = 'itemRollOut'
   ITEM_ROLL_OVER = 'itemRollOver'
   _INTERNAL_allowedTypes = {'change', 'enter', 'itemRollOut', 'itemRollOver'}

   @property
   def color(self):
      return self._color

   def __init__(self, type, color):
      super().__init__(type, True, True)
      self._color = color

   def toString(self):
      return self.formatToString('ColorPickerEvent', 'type', 'bubbles', 'cancelable', 'color')


class ComponentEvent(_AS3_BASEEVENT):
   BUTTON_DOWN = 'buttonDown'  # bubbles=False, cancelable=False
   ENTER = 'enter'  # bubbles=False, cancelable=False
   HIDE = 'hide'  # bubbles=False, cancelable=False
   LABEL_CHANGE = 'labelChange'  # bubbles=False, cancelable=False
   MOVE = 'move'  # bubbles=False, cancelable=False
   RESIZE = 'resize'  # bubbles=False, cancelable=False
   SHOW = 'show'  # bubbles=False, cancelable=False
   _INTERNAL_allowedTypes = {'buttonDown', 'enter', 'hide', 'labelChange', 'move', 'resize', 'show'}

   def toString(self):
      return self.formatToString('ComponentEvent', 'type', 'bubbles', 'cancelable')


class DataChangeEvent(_AS3_BASEEVENT):
   DATA_CHANGE = 'dataChange'
   PRE_DATA_CHANGE = 'preDataChange'
   _INTERNAL_allowedTypes = {'dataChange', 'preDataChange'}

   @property
   def changeType(self):
      return

   @property
   def endIndex(self):
      return

   @property
   def items(self):
      return

   @property
   def startIndex(self):
      return

   def __init__(self, eventType, changeType, items, startIndex=-1, endIndex=-1):
      super().__init__(eventType, False, False)
      self._changeType = changeType
      self._endIndex = endIndex
      self._items = items
      self._startIndex = startIndex

   def toString(self):
      return self.formatToString('DataChangeEvent', 'type', 'changeType', 'startIndex', 'endIndex', 'bubbles', 'cancelable')


class DataChangeType(metaclass=metaclasses._AS3_CONSTANTSOBJECT):
   ADD = 'add'
   CHANGE = 'change'
   INVALIDATE = 'invalidate'
   INVALIDATE_ALL = 'invalidateAll'
   REMOVE = 'remove'
   REMOVE_ALL = 'removeAll'
   REPLACE = 'replace'
   SORT = 'sort'


class DataGridEvent(ListEvent):
   COLUMN_STRETCH = 'columnStretch'
   HEADER_RELEASE = 'headerRelease'
   ITEM_EDIT_BEGIN = 'itemEditBegin'
   ITEM_EDIT_BEGINNING = 'itemEditBeginning'
   ITEM_EDIT_END = 'itemEditEnd'
   ITEM_FOCUS_IN = 'itemFocusIn'
   ITEM_FOCUS_OUT = 'itemFocusOut'
   _INTERNAL_allowedTypes = {'columnStretch', 'headerRelease', 'itemEditBegin', 'itemEditBeginning', 'itemEditEnd', 'itemFocusIn', 'itemFocusOut'}

   @property
   def dataField(self):
      return self._dataField

   @dataField.setter
   def dataField(self, value):
      self._dataField = value

   @property
   def itemRenderer(self):
      return self._itemRenderer

   @property
   def reason(self):
      return self._reason

   def __init__(self, type, bubbles=False, cancelable=False, columnIndex=-1, rowIndex=-1, itemRenderer=None, dataField=None, reason=None):
      super().__init__(type, bubbles, cancelable, columnIndex, rowIndex)
      self._dataField = dataField
      self._itemRenderer = itemRenderer
      self._reason = reason

   def toString(self):
      return self.formatToString('DataGridEvent', 'type', 'bubbles', 'cancelable', 'columnIndex', 'rowIndex', 'itemRenderer', 'dataField', 'reason')


class DataGridEventReason(metaclass=metaclasses._AS3_CONSTANTSOBJECT):
   CANCELED = 'cancelled'
   NEW_COLUMN = 'newColumn'
   NEW_ROW = 'newRow'
   OTHER = 'other'


class InteractionInputType(metaclass=metaclasses._AS3_CONSTANTSOBJECT):
   KEYBOARD = 'keyboard'
   MOUSE = 'mouse'


class RSLErrorEvent(ErrorEvent):
   RSL_LOAD_FAILED = 'rslLoadFailed'
   _INTERNAL_allowedTypes = {'rslLoadFailed', }

   @property
   def failedURLs(self):
      return self._failedURLs

   @property
   def rslsFailed(self):
      return self._rslsFailed

   @property
   def rslsLoaded(self):
      return self._rslsLoaded

   @property
   def rslsTotal(self):
      return self._rslsTotal

   def __init__(self, type, bubbles=False, cancelable=False, rslsLoaded=0, rslsFailed=0, rslsTotal=0, failedURLs=None):
      super().__init__(type, bubbles, cancelable)
      self._failedURLs = failedURLs
      self._rslsFailed = rslsFailed
      self._rslsLoaded = rslsLoaded
      self._rslsTotal = rslsTotal


class RSLEvent(_AS3_BASEEVENT):
   RSL_LOAD_COMPLETE = 'rslLoadComplete'
   RSL_PROGRESS = 'rslProgress'
   _INTERNAL_allowedTypes = {'rslLoadComplete', 'rslProgress'}

   @property
   def bytesLoaded(self):
      return self._bytesLoaded

   @property
   def bytesTotal(self):
      return self._bytesTotal

   @property
   def rslsFailed(self):
      return self._rslsFailed

   @property
   def rslsLoaded(self):
      return self._rslsLoaded

   @property
   def rslsTotal(self):
      return self._rslsTotal

   def __init__(self, type, bubbles=False, cancelable=False, rslsLoaded=0, rslsFailed=0, rslsTotal=0, bytesLoaded=0, bytesTotal=0):
      super().__init__(type, bubbles, cancelable)
      self._bytesLoaded = bytesLoaded
      self._bytesTotal = bytesTotal
      self._rslsFailed = rslsFailed
      self._rslsLoaded = rslsLoaded
      self._rslsTotal = rslsTotal


class ScrollEvent(_AS3_BASEEVENT):
   SCROLL = 'scroll'
   _INTERNAL_allowedTypes = {'scroll', }

   @property
   def delta(self):
      return self._delta

   @property
   def direction(self):
      return self._direction

   @property
   def position(self):
      return self._position

   def __init__(self, direction, delta, position):
      super().__init__('scroll', False, False)
      self._delta = delta
      self._direction = direction
      self._position = position

   def toString(self):
      return self.formatToString('ScrollEvent', 'type', 'bubbles', 'cancelable', 'direction', 'delta', 'position')


class SliderEvent(_AS3_BASEEVENT):
   CHANGE = 'change'
   THUMB_DRAG = 'thumbDrag'
   THUMB_PRESS = 'thumbPress'
   THUMB_RELEASE = 'thumbRelease'
   _INTERNAL_allowedTypes = {'change', 'thumbDrag', 'thumbPress', 'thumbRelease'}

   @property
   def clickTarget(self):
      return self._clickTarget

   @property
   def keyCode(self):
      return self._keyCode

   @property
   def triggerEvent(self):
      return self._triggerEvent

   @property
   def value(self):
      return self._value

   def __init__(self, type, value, clickTarget, triggerEvent, keyCode=0):
      super().__init__(type, False, False)
      self._clickTarget = clickTarget
      self._keyCode = keyCode
      self._triggerEvent = triggerEvent
      self._value = value

   def toString(self):
      return self.formatToString('SliderEvent', 'type', 'value', 'bubbles', 'cancelable', 'keyCode', 'triggerEvent', 'clickTarget')


class SliderEventClickTarget(metaclass=metaclasses._AS3_CONSTANTSOBJECT):
   THUMB = 'thumb'
   TRACK = 'track'
