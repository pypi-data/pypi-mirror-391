from as3lib import metaclasses
from as3lib.flash.display import MovieClip, Sprite


class ComponentShim(MovieClip):...  # This was included inside of every decompiled flash project I checked but it isn't in the documentation. I have no clue how it's used


class InvalidationType(metaclasses._AS3_CONSTANTSOBJECT):
   All = 'all'
   DATA = 'data'
   RENDERER_STYLES = 'rendererStyles'
   SCROLL = 'scroll'
   SELECTED = 'selected'
   SIZE = 'size'
   STATE = 'state'
   STYLES = 'styles'

class UIComponent(Sprite):...
