import as3lib as as3
from as3lib import metaclasses
from copy import copy


# BaseEvent
class _AS3_BASEEVENT:
   @property
   def bubbles(self):
      return self._bubbles

   @property
   def cancelable(self):
      return self._cancelable

   @property
   def currentTarget(self):
      return self._currentTarget

   @property
   def eventPhase(self):
      return self._eventPhase

   @property
   def target(self):
      return self._target

   @property
   def type(self):
      return self._type

   def __init__(self, type, bubbles=False, cancelable=False):
      if type not in self._INTERNAL_allowedTypes:
         raise Exception('Provided event type is not valid for this object')
      self._type = type
      self._bubbles = bubbles
      self._cancelable = cancelable
      self._currentTarget = None
      self._target = None
      self._eventPhase = None
      self._preventDefault = False

   def __eq__(self, value):
      return self.type == value

   def __str__(self):
      return self.type

   def getEventProperties(self):
      return (self.type, self.bubbles, self.cancelable, self.currentTarget, self.eventPhase, self.target)

   def clone(self):
      return copy(self)

   def formatToString(self, className, *arguements):
      return ''.join(['[', className] + [f' {i}={getattr(self, i)}' for i in arguements] + [']'])

   def isDefaultPrevented(self):
      return self._preventDefault

   def preventDefault(self):
      if self.cancelable:
         self._preventDefault = True

   def stopImmediatePropagation(self):...

   def stopPropagation(self):...

   def toString(self):
      return self.formatToString('Event', 'type', 'bubbles', 'cancelable')


# Interfaces
class IEventDispatcher:
   def __init__(self):
      self.eventobjects = {}

   def addEventListener(self, type, listener, useCapture=False, priority=0, useWeakReference=False):...

   def dispatchEvent(self, event):...

   def hasEventListener(self, type):...

   def removeEventListener(self, type, listener, useCapture=False):...

   def willTrigger(self, type):...


# Classes
class Event(_AS3_BASEEVENT):
   ACTIVATE = 'activate'  # bubbles=False, cancelable=False
   ADDED = 'added'  # bubbles=True, cancelable=False
   ADDED_TO_STAGE = 'addedToStage'  # bubbles=False, cancelable=False
   BROWSER_ZOOM_CHANGE = 'browerZoomChange'  # bubbles=False, cancelable=False
   CANCEL = 'cancel'  # bubbles=False, cancelable=False
   CHANGE = 'change'  # bubbles=True, cancelable=False
   CHANNEL_MESSAGE = 'channelMessage'  # bubbles=False, cancelable=False
   CHANNEL_STATE = 'channelState'  # bubbles=False, cancelable=False
   CLEAR = 'clear'  # bubbles=False, cancelable=False
   CLOSE = 'close'  # bubbles=False, cancelable=False
   CLOSING = 'closing'  # bubbles=False, cancelable=True
   COMPLETE = 'complete'  # bubbles=False, cancelable=False
   CONNECT = 'connect'  # bubbles=False, cancelable=False
   CONTEXT3D_CREATE = 'context3DCreate'  # ?
   COPY = 'copy'  # bubbles=False, cancelable=False
   CUT = 'cut'  # bubbles=False, cancelable=False
   DEACTIVATE = 'deactivate'  # bubbles=False, cancelable=False
   DISPLAYING = 'displaying'  # bubbles=False, cancelable=False
   ENTER_FRAME = 'enterFrame'  # bubbles=False, cancelable=False
   EXIT_FRAME = 'exitFrame'  # bubbles=False, cancelable=False
   EXITING = 'exiting'  # bubbles=False, cancelable=True
   FRAME_CONSTRUCTED = 'frameConstructed'  # bubbles=False, cancelable=False
   FRAME_LABEL = 'frameLabel'  # bubbles=False, cancelable=False
   FULLSCREEN = 'fullscreen'  # bubbles=False, cancelable=False
   HTML_BOUNDS_CHANGE = 'htmlBoundsChange'  # bubbles=False, cancelable=False
   HTML_DOM_INITIALIZE = 'htmlDOMInitialize'  # bubbles=False, cancelable=False
   HTML_RENDER = 'htmlRender'  # bubbles=False, cancelable=False
   ID3 = 'id3'  # bubbles=False, cancelable=False
   INIT = 'init'  # bubbles=False, cancelable=False
   LOCATION_CHANGE = 'locationChange'  # bubbles=False, cancelable=False
   MOUSE_LEAVE = 'mouseLeave'  # bubbles=False, cancelable=False
   NETWORK_CHANGE = 'networkChange'  # bubbles=False, cancelable=False
   OPEN = 'open'  # bubbles=False, cancelable=False
   PASTE = 'paste'  # bubbles=(platformDependant), cancelable=False
   PREPARING = 'preparing'  # bubbles=False, cancelable=False
   REMOVED = 'removed'  # bubbles=True, cancelable=False
   REMOVED_FROM_STAGE = 'removeFromStage'  # bubbles=False, cancelable=False
   RENDER = 'render'  # bubbles=False, cancelable=False
   RESIZE = 'resize'  # bubbles=False, cancelable=False
   SCROLL = 'scroll'  # bubbles=False, cancelable=False
   SELECT = 'select'  # bubbles=False, cancelable=False
   SELECT_ALL = 'selectAll'  # bubbles=False, cancelable=False
   SOUND_COMPLETE = 'soundComplete'  # bubbles=False, cancelable=False
   STANDARD_ERROR_CLOSE = 'standardErrorClose'  # bubbles=False, cancelable=False
   STANDARD_INPUT_CLOSE = 'standardInputClose'  # bubbles=False, cancelable=False
   STANDARD_OUTPUT_CLOSE = 'standardOutputClose'  # bubbles=False, cancelable=False
   SUSPEND = 'suspend'  # bubbles=False, cancelable=False
   TAB_CHILDREN_CHANGE = 'tabChildrenChange'  # bubbles=True, cancelable=False
   TAB_ENABLE_CHANGE = 'tabEnableChange'  # bubbles=True, cancelable=False
   TAB_INDEX_CHANGE = 'tabIndexChange'  # bubbles=True, cancelable=False
   TEXT_INTERACTION_MODE_CHANGE = 'textInteractionModeChange'  # bubbles=False, cancelable=False
   TEXTURE_READY = 'textureReady'  # ?
   UNLOAD = 'unload'  # bubbles=False, cancelable=False
   USER_IDLE = 'userIdle'  # bubbles=False, cancelable=False
   USER_PRESENT = 'userPresent'  # bubbles=False, cancelable=False
   VIDEO_FRAME = 'videoFrame'  # bubbles=False, cancelable=False
   WORKER_STATE = 'workerState'  # bubbles=False, cancelable=False
   _INTERNAL_allowedTypes = {'activate', 'added', 'addedToStage', 'browerZoomChange', 'cancel', 'change', 'channelMessage', 'channelState', 'clear', 'close', 'closing', 'complete', 'connect', 'context3DCreate', 'copy', 'cut', 'deactivate', 'displaying', 'enterFrame', 'exitFrame', 'exiting', 'frameConstructed', 'frameLabel', 'fullscreen', 'htmlBoundsChange', 'htmlDOMInitialize', 'htmlRender', 'id3', 'init', 'locationChange', 'mouseLeave', 'networkChange', 'open', 'paste', 'preparing', 'removed', 'removeFromStage', 'render', 'resize', 'scroll', 'select', 'selectAll', 'soundComplete', 'standardErrorClose', 'standardInputClose', 'standardOutputClose', 'suspend', 'tabChildrenChange', 'tabEnableChange', 'tabIndexChange', 'textInteractionModeChange', 'textureReady', 'unload', 'userIdle', 'userPresent', 'videoFrame', 'workerState'}


class EventDispatcher:
   # TODO: Implement priority, weakReference

   def __init__(self, target: IEventDispatcher = None):
      # TODO: Implement target
      self.activate = Event('activate', False, False)
      self.deactivate = Event('deactivate', False, False)
      self._events = {}
      self._eventsCapture = {}

   def addEventListener(self, type: str, listener, useCapture: as3.allBoolean = False, priority: as3.allInt = 0, useWeakReference: as3.allBoolean = False):
      # TODO: Add error
      if useCapture is False:
         if self._events.get(type) is None:
            self._events[type] = [listener]
         elif listener not in self._events[type]:
            self._events[type].append(listener)
      else:
         if self._eventsCapture.get(type) is None:
            self._eventsCapture[type] = [listener]
         elif listener not in self._eventsCapture[type]:
            self._eventsCapture[type].append(listener)

   def dispatchEvent(self, event):
      # TODO: Implement useCapture
      # TODO: Implement bubbles
      if not event.isDefaultPrevented():
         if self._events.get(event.type) is not None:
            e = event.clone()
            for i in self._events[event.type]:
               e._currentTarget = i
               i(e)
            return True
      return False

   def hasEventListener(self, type):
      return self._events.get(type) is not None or self._eventsCapture.get(type) is not None

   def removeEventListener(self, type: str, listener, useCapture: as3.allBoolean = False):
      if useCapture is False:
         if self._events.get(type) is not None:
            try:
               self._events[type].remove(listener)
            except Exception:
               pass
      else:
         if self._eventsCapture.get(type) is not None:
            try:
               self._eventsCapture[type].remove(listener)
            except Exception:
               pass

   def willTrigger(self, type: str):...


class TextEvent(_AS3_BASEEVENT):
   LINK = 'link'  # bubbles=True, cancelable=False
   TEXT_INPUT = 'textInput'  # bubbles=True, cancelable=True
   _INTERNAL_allowedTypes = {'link', 'textInput'}

   @property
   def text(self):
      return self._text

   @text.setter
   def text(self, value):
      self._text = value

   def __init__(self, type, bubbles=False, cancelable=False, text=''):
      self._text = text
      super().__init__(type, bubbles, cancelable)

   def toString(self):
      return self.formatToString('TextEvent', 'type', 'bubbles', 'cancelable', 'text')


class ErrorEvent(TextEvent):
   ERROR = 'error'
   _INTERNAL_allowedTypes = {'error',}

   @property
   def errorID(self):
      return self._errorID

   def __init__(self, type, bubbles=False, cancelable=False, text='', id=0):
      self._errorID = id
      super().__init__(type, bubbles, cancelable, text)

   def toString(self):
      return self.formatToString('ErrorEvent', 'type', 'bubbles', 'cancelable', 'text', 'errorID')


class AccelerometerEvent(_AS3_BASEEVENT):
   UPDATE = 'update'
   _INTERNAL_allowedTypes = {'update',}

   @property
   def accelerationX(self):
      return self._accelX

   @accelerationX.setter
   def accelerationX(self, value):
      self._accelX = value

   @property
   def accelerationY(self):
      return self._accelY

   @accelerationY.setter
   def accelerationY(self, value):
      self._accelY = value

   @property
   def accelerationZ(self):
      return self._accelZ

   @accelerationZ.setter
   def accelerationZ(self, value):
      self._accelZ = value

   @property
   def timestamp(self):
      return self._timestamp

   @timestamp.setter
   def timestamp(self, value):
      self._timestamp = value

   def __init__(self, type, bubbles=False, cancelable=False, timestamp=0, accelerationX=0, accelerationY=0, accelerationZ=0):
      self._accelX = accelerationX
      self._accelY = accelerationY
      self._accelZ = accelerationZ
      self._timestamp = timestamp
      super().__init__(type, bubbles, cancelable)

   def toString(self):
      return self.formatToString('AccelerometerEvent', 'type', 'bubbles', 'cancelable', 'timestamp', 'accelerationX', 'accelerationY', 'accelerationZ')


class ActivityEvent(_AS3_BASEEVENT):
   ACTIVITY = 'activity'
   _INTERNAL_allowedTypes = {'activity',}

   @property
   def activating(self):
      return self.activating

   @activating.setter
   def activating(self, value):
      self._activating = value

   def __init__(self, type, bubbles=False, cancelable=False, activating=False):
      self._activating = activating
      super().__init__(type, bubbles, cancelable)

   def toString(self):
      return self.formatToString('ActivityEvent', 'type', 'bubbles', 'cancelable', 'activating')


class AsyncErrorEvent(ErrorEvent):
   ASYNC_ERROR = 'asyncError'
   _INTERNAL_allowedTypes = {'asyncError',}

   @property
   def error(self):
      return self._error

   @error.setter
   def error(self, value):
      self._error = value

   def __init__(self, type, bubbles=False, cancelable=False, text='', error=None):
      self._error = error
      id = 0 if error is None else error.errorID
      super().__init__(type, bubbles, cancelable, text, id)

   def toString(self):
      return self.formatToString('AsyncErrorEvent', 'type', 'bubbles', 'cancelable', 'text', 'error', 'errorID')


class AudioOutputChangeEvent(_AS3_BASEEVENT):
   AUDIO_OUTPUT_CHANGE = 'audioOutputChange'
   _INTERNAL_allowedTypes = {'audioOutputChange',}

   @property
   def reason(self):
      return self._reason

   def __init__(self, type, bubbles=False, cancelable=False, reason=None):
      self._reason = reason


class AVDictionaryDataEvent(_AS3_BASEEVENT):
   # TODO: Make _dictionary init as a flash.utils.Dictionary object
   AV_DICTIONARY_DATA = 'avDictionaryData'
   _INTERNAL_allowedTypes = {'avDictionaryData',}

   @property
   def dictionary(self):
      return self._dictionary

   @property
   def time(self):
      return self._time

   def __init__(self, type, bubbles=False, cancelable=False, init_dictionary=None, init_dataTime=0):
      self._dictionary = {} if init_dictionary is None else init_dictionary
      self._time = init_dataTime
      super().__init__(type, bubbles, cancelable)


class AVHTTPStatusEvent(_AS3_BASEEVENT):
   AV_HTTP_RESPONSE_STATUS = 'avHttpResponseStatus'
   _INTERNAL_allowedTypes = {'avHttpResponseStatus',}

   @property
   def responseHeaders(self):
      return self._responseHeaders

   @responseHeaders.setter
   def responseHeaders(self, value):
      self._responseHeaders = value

   @property
   def responseUrl(self):
      return self._responseUrl

   @responseUrl.setter
   def responseUrl(self, value):
      self._responseUrl = value

   @property
   def status(self):
      return self._status

   def __init__(self, type, bubbles=False, cancelable=False, status=0, responseUrl=None, responseHeaders=None):
      self._status = status
      self._responseUrl = responseUrl
      self._responseHeaders = responseHeaders
      super().__init__(type, bubbles, cancelable)

   def toString(self):
      return self.formatToString('AVHTTPStatusEvent', 'type', 'bubbles', 'cancelable', 'status')


class AVPauseAtPeriodEndEvent(_AS3_BASEEVENT):
   AV_PAUSE_AT_PERIOD_END = 'avPauseAtPeriodEnd'
   _INTERNAL_allowedTypes = {'avPauseAtPeriodEnd',}

   @property
   def userData(self):
      return self._userData

   def __init__(self, type, bubbles=False, cancelable=False, userData=0):
      self._userData = userData
      super().__init__(type, bubbles, cancelable)


class BrowserInvokeEvent(_AS3_BASEEVENT):
   BROWSER_INVOKE = 'browserInvoke'
   _INTERNAL_allowedTypes = {'browserInvoke',}

   @property
   def arguements(self):
      return self._arguements

   @property
   def isHTTPS(self):
      return self._isHTTPS

   @property
   def isUserEvent(self):
      return self._isUserEvent

   @property
   def sandboxType(self):
      return self._sandboxType

   @property
   def securityDomain(self):
      return self._securityDomain

   def __init__(self, type, bubbles, cancelable, arguements, sandboxType, securityDomain, isHTTPS):
      self._arguements = arguements
      self._isHTTPS = isHTTPS
      self._isUserEvent = False
      self._sandboxType = sandboxType
      self._securityDomain = securityDomain
      super().__init__(type, bubbles, cancelable)


class ContextMenuEvent(_AS3_BASEEVENT):
   MENU_ITEM_SELECT = 'menuItemSelect'
   MENU_SELECT = 'menuSelect'
   _INTERNAL_allowedTypes = {'menuItemSelect', 'menuSelect'}

   @property
   def contextMenuOwner(self):
      return self._cmOwner

   @property
   def isMouseTargetInaccessible(self):
      return self._mTarget is None

   @property
   def mouseTarget(self):
      return self._mTarget

   def __init__(self, type, bubbles=False, cancelable=False, mouseTarget=None, contextMenuOwner=None):
      self._cmOwner = contextMenuOwner
      self._mTarget = mouseTarget
      super().__init__(type, bubbles, cancelable)

   def toString(self):
      return self.formatToString('ContextMenuEvent', 'type', 'bubbles', 'cancelable', 'mouseTarget', 'isMouseTargetInaccessible', 'contextMenuOwner')


class DataEvent(TextEvent):
   DATA = 'data'
   UPLOAD_COMPLETE_DATA = 'uploadCompleteData'
   _INTERNAL_allowedTypes = {'data', 'uploadCompleteData'}

   @property
   def data(self):
      return self._data

   @data.setter
   def data(self, value):
      self._data = value

   def __init__(self, type, bubbles=False, cancelable=False, data=''):
      self._data = data
      super().__init__(type, bubbles, cancelable)

   def toString(self):
      return self.formatToString('DataEvent', 'type', 'bubbles', 'cancelable', 'data')


class DatagramSocketDataEvent:...


class DeviceRotationEvent:...


class DNSResolverEvent:...


class DRMAuthenticateEvent:...


class DRMAuthenticateCompleteEvent:...


class DRMAuthenticateErrorEvent:...


class DRMDeviceGroupErrorEvent:...


class DRMErrorEvent:...


class DRMLicenseRequestEvent:...


class DRMMetadataEvent:...


class DRMReturnVoucherCompleteEvent:...


class DRMStatusEvent:...


class EventPhase(metaclass=metaclasses._AS3_CONSTANTSOBJECT):
   AT_TARGET = 2
   BUBBLING_PHASE = 3
   CAPTURING_PHASE = 1


class FileListEvent(_AS3_BASEEVENT):
   DIRECTORY_LISTING = 'directoryListing'
   SELECT_MULTIPLE = 'selectMultiple'
   _INTERNAL_allowedTypes = {'directoryListing', 'selectMultiple'}

   @property
   def files(self):
      return self._files

   @files.setter
   def files(self, value):
      self._files = value

   def __init__(self, type, bubbles=False, cancelable=False, files=None):
      self._files = as3.Array() if files is None else files
      super().__init__(type, bubbles, cancelable)


class FocusEvent(_AS3_BASEEVENT):
   # TODO: Implement isRelatedObjectInaccessible
   FOCUS_IN = 'focusIn'
   FOCUS_OUT = 'focusOut'
   KEY_FOCUS_CHANGE = 'keyFocusChange'
   MOUSE_FOCUS_CHANGE = 'mouseFocusChange'
   _INTERNAL_allowedTypes = {'focusIn', 'focusOut', 'keyFocusChange', 'mouseFocusChange'}

   @property
   def direction(self):
      return self._direction

   @direction.setter
   def direction(self, value):
      self._direction = value

   @property
   def isRelatedObjectInaccessible(self):...

   @isRelatedObjectInaccessible.setter
   def isRelatedObjectInaccessible(self, value):...

   @property
   def keyCode(self):
      return self._keyCode

   @keyCode.setter
   def keyCode(self, value):
      self._keyCode = value

   @property
   def relatedObject(self):
      return self._relatedObject

   @relatedObject.setter
   def relatedObject(self, value):
      self._relatedObject = value

   @property
   def shiftKey(self):
      return self._shiftKey

   @shiftKey.setter
   def shiftKey(self, value):
      self._shiftKey = value

   def __init__(self, type, bubbles=False, cancelable=False, relatedObject=None, shiftKey=False, keyCode=0, direction='none'):
      self._direction = direction
      self._keyCode = keyCode
      self._relatedObject = relatedObject
      self._shiftKey = shiftKey
      super().__init__(type, bubbles, cancelable)

   def toString(self):
      return self.formatToString('FocusEvent', 'type', 'bubbles', 'cancelable', 'relatedObject', 'shiftKey', 'keyCode')


class FullScreenEvent(ActivityEvent):
   FULL_SCREEN = 'fullScreen'
   FULL_SCREEN_INTERACTIVE_ACCEPTED = 'fullScreenInteractiveAccepted'
   _INTERNAL_allowedTypes = {'fullScreen', 'fullScreenInteractiveAccepted'}

   @property
   def fullScreen(self):
      return self._fullscreen

   @property
   def interactive(self):
      return self._interactive

   def __init__(self, type, bubbles=False, cancelable=False, fullScreen=False, interactive=False):
      self._fullscreen = fullScreen
      self._interactive = interactive
      super().__init__(type, bubbles, cancelable, False)

   def toString(self):
      return self.formatToString('FullScreenEvent', 'type', 'bubbles', 'cancelable', 'activating')


class GameInputEvent:...


class GeolocationEvent:...


class GestureEvent:...


class GesturePhase(metaclass=metaclasses._AS3_CONSTANTSOBJECT):
   ALL = 'all'
   BEGIN = 'begin'
   END = 'end'
   UPDATE = 'update'


class HTMLUncaughtScriptExceptionEvent:...


class HTTPStatusEvent(_AS3_BASEEVENT):
   HTTP_RESPONSE_STATUS = 'httpResponseStatus'
   HTTP_STATUS = 'httpStatus'
   _INTERNAL_allowedTypes = {'httpResponseStatus', 'httpStatus'}

   @property
   def redirected(self):
      return self._redirected

   @redirected.setter
   def redirected(self, value):
      self._redirected = value

   @property
   def responseHeaders(self):
      return self._responseHeaders

   @responseHeaders.setter
   def responseHeaders(self, value: list):
      self._responseHeaders = value

   @property
   def responseURL(self):
      return self._responseURL

   @responseURL.setter
   def responseURL(self, value):
      self._responseURL = value

   @property
   def status(self):
      return self._status

   def __init__(self, type, bubbles=False, cancelable=False, status=0, redirected=False):
      self._status = status
      self._redirected = redirected
      self._responseHeaders = as3.Array()
      self._responseURL = ''
      super().__init__(type, bubbles, cancelable)

   def toString(self):
      return self.formatToString('HTTPStatusEvent', 'type', 'bubbles', 'cancelable', 'status')


class IMEEvent:...


class InvokeEvent:...


class IOErrorEvent(ErrorEvent):
   IO_ERROR = 'ioError'
   STANDARD_ERROR_IO_ERROR = 'standardErrorIoError'
   STANDARD_INPUT_IO_ERROR = 'standardInputIoError'
   STANDARD_OUTPUT_IO_ERROR = 'standardOutputIoError'
   _INTERNAL_allowedTypes = {'ioError', 'standardErrorIoError', 'standardInputIoError', 'standardOutputIoError'}

   def toString(self):
      return self.formatToString('IOErrorEvent', 'type', 'bubbles', 'cancelable', 'text', 'errorID')


class KeyboardEvent(_AS3_BASEEVENT):
   KEY_DOWN = 'keyDown'
   KEY_UP = 'keyUp'
   _INTERNAL_allowedTypes = {'keyDown', 'keyUp'}

   @property
   def altKey(self):
      return self._altKey

   @altKey.setter
   def altKey(self, value):
      self._altKey = value

   @property
   def charCode(self):
      return self._charCode

   @charCode.setter
   def charCode(self, value):
      self._charCode = value

   @property
   def commandKey(self):
      return self._commandKey

   @commandKey.setter
   def commandKey(self, value):
      self._commandKey = value

   @property
   def controlKey(self):
      return self._controlKey

   @controlKey.setter
   def controlKey(self, value):
      self._controlKey = value

   @property
   def ctrlKey(self):...  # TODO

   @ctrlKey.setter
   def ctrlKey(self, value):...

   @property
   def keyCode(self):
      return self._keyCode

   @keyCode.setter
   def keyCode(self, value):
      self._keyCode = value

   @property
   def keyLocation(self):
      return self._keyLocation

   @keyLocation.setter
   def keyLocation(self, value):
      self._keyLocation = value

   @property
   def shiftKey(self):
      return self._shiftKey

   @shiftKey.setter
   def shiftKey(self, value):
      self._shiftKey = value

   def __init__(self, type, bubbles=False, cancelable=False, charCodeValue=0, keyCodeValue=0, keyLocationValue=0, ctrlKeyValue=False, altKeyValue=False, shiftKeyValue=False, controlKeyValue=False, commandKeyValue=False):
      self._altKey = altKeyValue
      self._charCode = charCodeValue
      self._commandKey = commandKeyValue
      self._controlKey = controlKeyValue
      self._ctrlKey = ctrlKeyValue
      self._keyCode = keyCodeValue
      self._keyLocation = keyLocationValue
      self._shiftKey = shiftKeyValue
      super().__init__(type, bubbles, cancelable)

   def toString(self):
      return self.formatToString('KeyboardEvent', 'type', 'bubbles', 'cancelable', 'altKey', 'charCode', 'commandKey', 'controlKey', 'ctrlKey', 'keyCode', 'keyLocation', 'shiftKey')

   def updateAfterEvent(self):...


class LocationChangeEvent:...


class MediaEvent:...


class MouseEvent:...


class NativeDragEvent:...


class NativeProcessExitEvent:...


class NativeWindowBoundsEvent:...


class NativeWindowDisplayStateEvent:...


class NetDataEvent:...


class NetMonitorEvent:...


class NetStatusEvent:...


class OutputProgressEvent:...


class PermissionEvent(_AS3_BASEEVENT):
   # TODO: figure out where permission information is stored
   PERMISSION_STATUS = 'permissionStatus'
   _INTERNAL_allowedTypes = {'permissionStatus',}

   @property
   def status(self):
      return self._status

   def __init__(self, type, bubbles=False, cancelable=False, status='denied'):
      self._status = status
      super().__init__(type, bubbles, cancelable)

   def toString(self):
      return f'[PermissionEvent type={self.type} bubbles={self.bubbles} cancelable={self.cancelable} permission= status={self.status}]'


class PressAndTapGestureEvent:...


class ProgressEvent(_AS3_BASEEVENT):
   PROGRESS = 'progress'
   SOCKET_DATA = 'socketData'
   STANDARD_ERROR_DATA = 'standardErrorData'
   STANDARD_INPUT_PROGRESS = 'standardInputProgress'
   STANDARD_OUTPUT_DATA = 'standardOutputData'
   _INTERNAL_allowedTypes = {'progress', 'socketData', 'standardErrorData', 'standardInputProgress', 'standardOutputData'}

   @property
   def bytesLoaded(self):
      return self._bytesLoaded

   @bytesLoaded.setter
   def bytesLoaded(self, value):
      self._bytesLoaded = value

   @property
   def bytesTotal(self):
      return self._bytesTotal

   @bytesTotal.setter
   def bytesTotal(self, value):
      self._bytesTotal = value

   def __init__(self, type, bubbles=False, cancelable=False, bytesLoaded=0, bytesTotal=0):
      self._bytesLoaded = bytesLoaded
      self._bytesTotal = bytesTotal
      super().__init__(type, bubbles, cancelable)

   def toString(self):
      return self.formatToString('ProgressEvent', 'type', 'bubbles', 'cancelable', 'bytesLoaded', 'bytesTotal')


class RemoteNotificationEvent:...


class SampleDataEvent:...


class ScreenMouseEvent:...


class SecurityErrorEvent(ErrorEvent):
   SECURITY_ERROR = 'securityError'
   _INTERNAL_allowedTypes = {'securityError',}

   def toString(self):
      return self.formatToString('SecurityErrorEvent', 'type', 'bubbles', 'cancelable', 'text', 'errorID')


class ServerSocketConnectEvent:...


class ShaderEvent:...


class SoftKeyboardEvent:...


class SoftKeyboardTrigger(metaclass=metaclasses._AS3_CONSTANTSOBJECT):
   CONTENT_TRIGGERED = 'contentTriggered'
   USER_TRIGGERED = 'userTriggered'


class SQLEvent:...


class SQLUpdateEvent:...


class StageOrientationEvent(_AS3_BASEEVENT):
   ORIENTATION_CHANGE = 'orientationChange'
   ORIENTATION_CHANGING = 'orientationChanging'
   _INTERNAL_allowedTypes = {'orientationChange', 'orientationChanging'}

   @property
   def afterOrientation(self):
      return self._afterOrientation

   @property
   def beforeOrientation(self):
      return self._beforeOrientation

   def __init__(self, type, bubbles=False, cancelable=False, beforeOrientation=None, afterOrientation=None):
      self._afterOrientation = afterOrientation
      self._beforeOrientation = beforeOrientation
      super().__init__(type, bubbles, cancelable)
      
   def toString(self):...


class StageVideoAvailabilityEvent:...


class StageVideoEvent:...


class StatusEvent:...


class StorageVolumeChangeEvent:...


class SyncEvent:...


class ThrottleEvent(_AS3_BASEEVENT):
   THROTTLE = 'throttle'
   _INTERNAL_allowedTypes = {'throttle',}

   @property
   def state(self):
      return self._state

   @property
   def targetFrameRate(self):
      return self._targetFrameRate

   def __init__(self, type, bubbles=False, cancelable=False, state=None, targetFrameRate=0):
      self._state = state
      self._targetFrameRate = targetFrameRate
      super().__init__(type, bubbles, cancelable)

   def toString(self):
      return self.formatToString('ThrottleEvent', 'type', 'bubbles', 'cancelable', 'state', 'targetFrameRate')


class ThrottleType(metaclass=metaclasses._AS3_CONSTANTSOBJECT):
   PAUSE = 'pause'
   RESUME = 'resume'
   THROTTLE = 'throttle'


class TimerEvent(_AS3_BASEEVENT):
   TIMER = 'timer'  # bubbles=False, cancelable=False
   TIMER_COMPLETE = 'timerComplete'  # bubbles=False, cancelable=False
   _INTERNAL_allowedTypes = {'timer', 'timerComplete'}

   def __init__(self, type, bubbles=False, cancelable=False):
      super().__init__(type, bubbles, cancelable)

   def toString(self):
      return self.formatToString('TimerEvent', 'type', 'bubbles', 'cancelable')

   def updateAfterEvent(self):...


class TouchEvent:...


class TouchEventIntent:...


class TransformGestureEvent:...


class UncaughtErrorEvent:...


class UncaughtErrorEvents:...


class VideoEvent:...


class VideoTextureEvent:...


class VsyncStateChangeAvailabilityEvent:...
