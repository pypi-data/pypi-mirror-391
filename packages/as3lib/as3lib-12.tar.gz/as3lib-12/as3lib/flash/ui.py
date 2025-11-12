import as3lib as as3
from as3lib import keyConversions, metaclasses
import tkinter


class CMItemList:
   def __init__(self):
      self.itemorder = as3.Array()
      self.itemproperties = {}

   def __str__(self):
      return f'{self.itemorder},{self.itemproperties}'

   def __len__(self):
      return len(self.itemorder)

   def __getitem__(self, item):
      if isinstance(item, int):
         return self.itemorder[item]
      if isinstance(item, str):
         return self.itemproperties[item]

   def __setitem__(self, item, value):
      if isinstance(item, int):
         self.itemorder[item] = value
      elif isinstance(item, str):
         self.itemproperties[item] = value

   def length(self):
      return len(self)

   def indexOfItem(self, item: str):
      return self.itemorder.indexOf(item)

   def addContextMenuItem(self, obj: object, index: int = -1):
      if not isinstance(obj, ContextMenuItem):
         raise as3.TypeError('Item not of type ContextMenuItem')
      tempproperties = {'master': obj.master, 'type': obj.type_, 'command': obj.command, 'caption': obj.caption, 'separatorBefore': obj.separatorBefore, 'enabled': obj.enabled, 'visible': obj.visible}
      if index == -1:
         self.append(obj.name, tempproperties)
      else:
         self.addItemAt(index, obj.name, tempproperties)

   def append(self, name: str, properties: dict):
      self.itemorder.push(name)
      self.itemproperties[name] = properties

   def addItemAt(self, index: int, name: str, properties: dict):
      self.itemorder.insertAt(index, name)
      self.itemproperties[name] = properties

   def removeItem(self, name: str):
      self.itemorder.removeAt(self.itemorder.indexOf(name))
      self.itemproperties.pop(name)

   def removeItemAt(self, index: int):
      self.itemproperties.pop(self.itemorder[index])
      self.itemorder.removeAt(index)

   def removeAllItems(self):
      self.itemorder = as3.Array()
      self.itemproperties = {}

   def propertiesAt(self, index: int):
      return self.itemproperties[self.itemorder[index]]


class ContextMenu:
   def __init__(self, master: object, font=('TkTextFont', 8)):
      self.builtInItems = ContextMenuBuiltInItems()
      self._builtIns: bool = True
      self.clipboardItems = ContextMenuClipboardItems()
      self.clipboardMenu: bool = True
      self.customItems = CMItemList()
      self._itemobjects = {}
      self.isSupported = True
      self.items = None  # TODO: Implement this
      self.font = font
      self.link = None
      self.numItems: int
      self._master = master

   def _createAndBindMenu(self):
      self._itemobjects = {}
      try:
         self._master.unbind()
      except Exception:...
      self.Menu = tkinter.Menu(self._master, tearoff=0)
      if self._builtIns:
         if self.builtInItems.forwardAndBack:
            self.Menu.add_command(label='Forward', font=self.font)
            self.Menu.add_command(label='Backward', font=self.font)
         if self.builtInItems.loop:
            self.Menu.add_command(label='Loop', font=self.font)
         if self.builtInItems.play:
            self.Menu.add_command(label='Play', font=self.font)
         if self.builtInItems.print:
            self.Menu.add_command(label='Print', font=self.font)
         if self.builtInItems.quality:
            self.Menu.add_command(label='Quality', font=self.font)
         if self.builtInItems.rewind:
            self.Menu.add_command(label='Rewind', font=self.font)
         if self.builtInItems.save:
            self.Menu.add_command(label='Save', font=self.font)
         if self.builtInItems.zoom:
            self.Menu.add_command(label='Zoom', font=self.font)
      if self.clipboardMenu:
         self._itemobjects['clipboardMenu'] = tkinter.Menu(self.Menu, tearoff=0)
         self.Menu.add_cascade(label='Clipboard', font=self.font, menu=self._itemobjects['clipboardMenu'])
         if self.clipboardItems.clear:
            self._itemobjects['clipboardMenu'].add_command(label='Clear', font=self.font)
         if self.clipboardItems.copy:
            self._itemobjects['clipboardMenu'].add_command(label='Copy', font=self.font)
         if self.clipboardItems.cut:
            self._itemobjects['clipboardMenu'].add_command(label='Cut', font=self.font)
         if self.clipboardItems.paste:
            self._itemobjects['clipboardMenu'].add_command(label='Paste', font=self.font)
         if self.clipboardItems.selectAll:
            self._itemobjects['clipboardMenu'].add_command(label='Select All', font=self.font)
      for i in range(self.customItems.length()):
         tempprop = self.customItems.propertiesAt(i)
         if tempprop['visible']:
            if tempprop['type'] == 'Menu':
               if tempprop['master'] == 'root':
                  if tempprop['separatorBefore']:
                     self.Menu.add_separator()
                  self._itemobjects[tempprop['name']] = tkinter.Menu(self.Menu, tearoff=0)
                  self.Menu.add_cascade(label=tempprop['caption'], font=self.font, menu=self._itemobjects[tempprop['name']])
               else:
                  if tempprop['separatorBefore']:
                     self._itemobjects[tempprop['master']].add_separator()
                  self._itemobjects[tempprop['name']] = tkinter.Menu(self._itemobjects[tempprop['master']], tearoff=0)
                  self._itemobjects[tempprop['master']].add_cascade(label=tempprop['caption'], font=self.font, menu=self._itemobjects[tempprop['name']])
            else:
               if tempprop['master'] == 'root':
                  if tempprop['separatorBefore']:
                     self.Menu.add_separator()
                  self.Menu.add_command(label=tempprop['caption'], font=self.font, command=tempprop['command'])
                  if not tempprop['enabled']:
                     self.Menu.entryconfigure(tempprop['caption'], state='disabled')
               else:
                  if tempprop['separatorBefore']:
                     self._itemobjects[tempprop['master']].add_separator()
                  self._itemobjects[tempprop['master']].add_command(label=tempprop['caption'], font=self.font, command=tempprop['command'])
                  if not tempprop['enabled']:
                     self._itemobjects[tempprop['master']].entryconfigure(tempprop['caption'], state='disabled')
      self._master.bind(keyConversions.mouseButtonNameToTkname('Right'), self._popupMenu)

   def _popupMenu(self, e):
      try:
         self.Menu.tk_popup(e.x_root, e.y_root)
      finally:
         self.Menu.grab_release()

   def addItemAt(self, item: object, index: int = -1):
      if not isinstance(item, ContextMenuItem):
         raise as3.TypeError('Item not of type ContextMenuItem')
      self.customItems.addContextMenuItem(item, index)
      self._createAndBindMenu()

   def clone(self):
      return self

   def containsItem(self, item: object):
      if not isinstance(item, ContextMenuItem):
         raise as3.TypeError('Item not of type ContextMenuItem')
      temp = self.customItems.idexOfItem(item.name)
      return temp != -1

   def display(self, stage: object, stageX, stageY):...

   def getItemAt(self, item: object):
      if not isinstance(item, ContextMenuItem):
         raise as3.TypeError('Item not of type ContextMenuItem')
      return self.customItems.indexOfItem(item.name)

   def getItemAt_Name(self, item: str):
      return self.customItems.indexOfItem(item)

   def hideBuiltInItems(self):
      self._builtIns = False
      self._createAndBindMenu()

   def removeAllItems(self):
      self.customItems.removeAllItems()
      self._builtIns = False
      self.clipboardMenu = False
      self._createAndBindMenu()

   def removeItemAt(self, index: int):
      '''
      Removes and returns the menu item at the specified index.
      Parameters
         index:int — The (zero-based) position of the item to remove.
      Returns
         ContextMenuItem — The item that was removed.
      '''
      temp = self.customItems[index]
      tempprop = self.customItems[temp]
      self.customItems.removeItemAt(index)
      self._createAndBindMenu()
      return ContextMenuItem(master=tempprop['master'], caption=tempprop['caption'], name=temp, separatorBefore=tempprop['separatorBefore'], enabled=tempprop['enabled'], visible=tempprop['visible'], type_=tempprop['type'], command=tempprop['command'])


class ContextMenuBuiltInItems:
   def __init__(self):
      self.forwardAndBack: bool
      self.loop: bool = True
      self.play: bool = True
      self.print: bool = True
      self.quality: bool = True
      self.rewind: bool = True
      self.save: bool = True
      self.zoom: bool = True

   def get(self, item: str):
      if item == 'forwardAndBack':
         return self.forwardAndBack
      if item == 'loop':
         return self.loop
      if item == 'play':
         return self.play
      if item == 'print':
         return self.print
      if item == 'quality':
         return self.quality
      if item == 'rewind':
         return self.rewind
      if item == 'save':
         return self.save
      if item == 'zoom':
         return self.zoom

   def set(self, item: str, value: bool):
      if item == 'forwardAndBack':
         self.forwardAndBack = value
      elif item == 'loop':
         self.loop = value
      elif item == 'play':
         self.play = value
      elif item == 'print':
         self.print = value
      elif item == 'quality':
         self.quality = value
      elif item == 'rewind':
         self.rewind = value
      elif item == 'save':
         self.save = value
      elif item == 'zoom':
         self.zoom = value


class ContextMenuClipboardItems:
   def __init__(self):
      self.clear: bool = True
      self.copy: bool = True
      self.cut: bool = True
      self.paste: bool = True
      self.selectAll: bool = True

   def get(self, item: str):
      if item == 'clear':
         return self.clear
      if item == 'copy':
         return self.copy
      if item == 'cut':
         return self.cut
      if item == 'paste':
         return self.paste
      if item == 'selectAll':
         return self.selectAll

   def set(self, item: str, value: bool):
      if item == 'clear':
         self.clear = value
      elif item == 'copy':
         self.copy = value
      elif item == 'cut':
         self.cut = value
      elif item == 'paste':
         self.paste = value
      elif item == 'selectAll':
         self.selectAll = value


class ContextMenuItem:
   def __init__(self, master: str, caption: str, name: str, separatorBefore: bool = False, enabled: bool = True, visible: bool = True, type_: str = 'Item', command: object = ''):
      self.caption = caption
      self.separatorBefore = separatorBefore
      self.enabled = enabled
      self.visible = visible
      self.master = master
      self.name = name
      if type_ == 'Item':
         self.command = command
      if type_ not in {'Item', 'Menu'}:
         self.type_ = 'Item'
         self.command = ''
         raise as3.TypeError('Invalid menu type. Must be "Item" or "Menu". Making type the default ("Item").')
      self.type_ = type_


class GameInput:...


class GameInputControl:...


class GameInputDevice:...


class Keyboard:...


class KeyboardType:...


class KeyLocation:...


class Mouse:...


class MouseCursor(metaclass=metaclasses._AS3_CONSTANTSOBJECT):
   ARROW = 'arrow'
   AUTO = 'auto'
   BUTTON = 'button'
   HAND = 'hand'
   IBEAM = 'ibeam'


class MouseCursorData:...


class Multitouch:...


class MultitouchInputMode:...
