from as3lib import metaclasses


class PermissionStatus(metaclass=metaclasses._AS3_CONSTANTSOBJECT):
   DENIED = 'denied'
   GRANTED = 'granted'
   ONLY_WHEN_IN_USE = 'onlyWhenInUse'
   UNKNOWN = 'unknown'
