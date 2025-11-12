import tkinter
from tkinter import filedialog
from tkinter.ttk import Combobox, Notebook
import tkhtmlview
import PIL
from io import BytesIO
import as3lib as as3
try:
   from as3lib import cmath
except Exception:
   from as3lib.cfail import cmath
from as3lib import helpers, as3state, Error
'''
Temporary interface to get things working. A bit slow when too many things are defined. Even after this module is no longer needed, it will probably stay for compatibility purposes.
Notes:
- When setting commands, they must be accessible from the scope of where they are called
- If using wayland, windows made using tkinter.Tk() will not group with windows made using tkinter.Toplevel(). This will hopefully be fixed if the ext-zones protocol is merged (tcl/tk would have to support it as well).
'''

as3state.interfaceType = 'Tkinter'


def _idGen():
   i = 1
   while True:
      yield i
      i += 1


_windowID = _idGen()


def help():
   print("If you are confused about how to use this module, please run this module by itself and look at the test code at the bottom. This is more of a test module so don't expect it to make any sense.")


def _nullFunc(*args):
   pass


class itkBaseWidget:
   _intName = None

   def __init__(self, cls, master, **kwargs):
      self._x = kwargs.pop('x', None)
      self._y = kwargs.pop('y', None)
      self._width = kwargs.pop('width', None)
      self._height = kwargs.pop('height', None)
      self._anchor = kwargs.pop('anchor', 'nw')
      tempfont = kwargs.pop('font', ('TkTextFont', 12, ''))
      self._font = tempfont[0]
      self._fontSize = tempfont[1]
      self._fontStyle = tempfont[2] if len(tempfont) == 3 else ''
      self._bg = kwargs.pop('background', kwargs.pop('bg', '#FFFFFF'))
      self._fg = kwargs.pop('foreground', kwargs.pop('fg', '#000000'))
      self._state = kwargs.pop('state', 'normal')
      self._window = kwargs.pop('itkWindow', None)
      cls.__init__(self, master, **kwargs)
      self.updateBackground()
      self.updateForeground()

   def update(self):
      nm = self._window.mult
      self.place(x=self._x*nm, y=self._y*nm, width=self._width*nm, height=self._height*nm, anchor=self._anchor)

   def updateText(self):
      self['font'] = (self._font, cmath.resizefont(self._fontSize, self._window.fontmult), self._fontStyle)

   def updateBackground(self):
      self['background'] = self._bg

   def updateForeground(self):
      self['foreground'] = self._fg

   def updateState(self):
      self['state'] = self._state

   def resize(self, *e):
      self.update()
      self.updateText()

   @property
   def background(self):
      return self._bg

   @background.setter
   def background(self, color):
      self._bg = color
      self.updateBackground()

   @property
   def foreground(self):
      return self._fg

   @foreground.setter
   def foreground(self, color):
      self._fg = color
      self.updateForeground()

   @property
   def font(self):
      return (self._font, self._fontSize, self._fontStyle)

   @font.setter
   def font(self, font):
      self._font = font[0]
      self._fontSize = font[1]
      self._fontStyle = font[2] if len(font) == 3 else ''
      self.updateText()

   @property
   def x(self):
      return self._x

   @x.setter
   def x(self, x):
      self._x = x
      self.update()

   @property
   def y(self):
      return self._y

   @y.setter
   def y(self, y):
      self._y = y
      self.update()

   @property
   def width(self):
      return self._width

   @width.setter
   def width(self, w):
      self._width = w
      self.resize()

   @property
   def height(self):
      return self._height

   @height.setter
   def height(self, h):
      self._height = h
      self.resize()

   @property
   def anchor(self):
      return self._anchor

   @anchor.setter
   def anchor(self, a):
      self._anchor = a
      self.update()

   @property
   def state(self):
      return self._state

   @state.setter
   def state(self, state):
      self._state = state
      self.updateState()

   text = property(fset=_nullFunc, fget=_nullFunc)
   bold = property(fset=_nullFunc, fget=_nullFunc)
   border = property(fset=_nullFunc, fget=_nullFunc)
   mult = property(fset=_nullFunc, fget=_nullFunc)


class itkFrame(itkBaseWidget, tkinter.Frame):
   _intName = 'Frame'

   def __init__(self, master=None, **kwargs):
      super().__init__(tkinter.Frame, master, **kwargs)

   def updateBackground(self):
      self['bg'] = self._bg

   updateText = _nullFunc
   updateForeground = _nullFunc
   foreground = property(fset=_nullFunc, fget=_nullFunc)
   font = property(fset=_nullFunc, fget=_nullFunc)


class itkLabel(itkBaseWidget, tkinter.Label):
   _intName = 'Label'

   def __init__(self, master=None, **kwargs):
      super().__init__(tkinter.Label, master, **kwargs)

   @property
   def text(self):
      return self['text']

   @text.setter
   def text(self, text):
      self['text'] = text


class itknwhLabel(itkLabel):
   _intName = 'nwhLabel'

   def update(self):
      nm = self._window.mult
      self.place(x=self._x*nm, y=self._y*nm, anchor=self._anchor)

   width = property(fset=_nullFunc, fget=_nullFunc)
   height = property(fset=_nullFunc, fget=_nullFunc)


class itkButton(itkBaseWidget, tkinter.Button):
   _intName = 'Button'

   def __init__(self, master=None, **kwargs):
      super().__init__(tkinter.Button, master, **kwargs)

   @property
   def text(self):
      return self['text']

   @text.setter
   def text(self, text):
      self['text'] = text


class itkHTMLScrolledText(itkBaseWidget, tkhtmlview.HTMLScrolledText):
   _intName = 'HTMLScrolledText'

   def __init__(self, master=None, **kwargs):
      self._sbscaling = kwargs.pop('sbscaling', True)
      self._sbwidth = kwargs.pop('sbwidth', 12)
      self._text = ''
      text = kwargs.pop('text', '')
      border = kwargs.pop('border', False)
      self._bold = False
      self._textCache = ''
      super().__init__(tkhtmlview.HTMLScrolledText, master, **kwargs)
      self.border = border
      self.text = text

   def update(self):
      nm = self._window.mult
      if self._sbscaling:
         self.vbar['width'] = self._sbwidth*nm
      self.place(x=self._x*nm, y=self._y*nm, width=self._width*nm, height=self._height*nm, anchor=self._anchor)

   def updateText(self):
      self['state'] = 'normal'
      temp = ('<b>', '</b>') if self.bold else ('', '')
      self.set_html(f'{temp[0]}<pre style="color: {self._fg}; background-color: {self._bg}; font-size: {cmath.resizefont(self._fontSize, self._window.fontmult)}px; font-family: {self._font}">{self._textCache}</pre>{temp[1]}')
      self['state'] = 'disabled'

   def updateBackground(self):
      self['background'] = self._bg
      self.updateText()

   def updateForeground(self):
      self['foreground'] = self._bg
      self.updateText()

   def processText(self, text):
      '''
      An overridable method to control text preprocessing.
      
      This method should:
         1) Set self._text. This is what is returned by the text property and
            is used by the default implementation of this method to check
            whether the text has been modified.
         2) Set self._textCache to the processed text. This is the text that is
            actually displayed.
      '''
      if self._text != text:
         self._text = text
         self._textCache = text.replace('\t', '    ')

   @property
   def text(self):
      return self._text

   @text.setter
   def text(self, text):
      self.processText(text)
      self.updateText()

   @property
   def bold(self):
      return self._bold

   @bold.setter
   def bold(self, value):
      self._bold = value
      self.updateText()

   @property
   def border(self):
      return self._border

   @border.setter
   def border(self, value: bool):
      self._border = value
      if value:
         self.configure(borderwidth=1, highlightthickness=1)
      else:
         self.configure(borderwidth=0, highlightthickness=0)

   @property
   def sbscaling(self):
      return self._sbscaling

   @sbscaling.setter
   def sbscaling(self, value):
      self._sbscaling = value
      self.update()

   @property
   def sbwidth(self):
      return self._sbwidth

   @sbwidth.setter
   def sbwidth(self, value):
      self._sbwidth = value
      self.update()

   def destroy(self):
      super().destroy()
      self.frame.destroy()


class itkEntry(itkBaseWidget, tkinter.Entry):
   _intName = 'Entry'

   def __init__(self, master=None, **kwargs):
      self._text = kwargs.pop('textvariable', tkinter.StringVar())
      super().__init__(tkinter.Entry, master, textvariable=self._text, **kwargs)

   def updateBackground(self):
      self['insertbackground'] = self._bg
      self['background'] = self._bg

   @property
   def text(self):
      return self._text.get()

   @text.setter
   def text(self, text):
      self._text.set(text)


class itkNotebook(itkBaseWidget, Notebook):
   _intName = 'Notebook'

   def __init__(self, master=None, **kwargs):
      super().__init__(Notebook, master, **kwargs)

   def update(self):
      if not (self._x is None or self._y is None or self._width is None or self._height is None):
         nm = self._window.mult
         self.place(x=self._x*nm, y=self._y*nm, width=self._width*nm, height=self._height*nm, anchor=self._anchor)
      else:
         self.pack(expand=True)

   updateBackground = _nullFunc
   updateText = _nullFunc
   updateForeground = _nullFunc


class itkNBFrame(itkFrame):
   _intName = 'NBFrame'

   def __init__(self, master, **kwargs):
      self._text = kwargs.pop('text', '')
      super().__init__(master, **kwargs)
      master.add(self, text=self._text)

   def update(self):
      nm = self._window.mult
      self['width'] = self._width*nm
      self['height'] = self._height*nm

   @property
   def text(self):
      return self._text

   x = property(fset=_nullFunc, fget=_nullFunc)
   y = property(fset=_nullFunc, fget=_nullFunc)
   anchor = property(fset=_nullFunc, fget=_nullFunc)


class itkImageLabel(itkLabel):
   _intName = 'ImageLabel'

   def __init__(self, master, **kwargs):
      temp = kwargs.pop('image_name', '')
      self._imgname = ''
      super().__init__(master, **kwargs)
      self.image_name = temp

   def updateText(self):
      self['image'] = self._window.images[self._imgname].img

   @property
   def image_name(self):
      return self._imgname

   @image_name.setter
   def image_name(self, name):
      if name in self._window.images:
         self._imgname = name
         self['image'] = self._window.images[name].img


# ----------------------------------------------------
# This section contains code that is a modification of code from tkhtmlview
class ScrolledListbox(tkinter.Listbox):
   # Uses HTMLScrolledText as a reference but uses a listbox instead of HTMLText
   def __init__(self, master=None, **kwargs):
      self.frame = tkinter.Frame(master)
      self.vbar = tkinter.Scrollbar(self.frame)

      kwargs['yscrollcommand'] = self.vbar.set
      self.vbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
      self.vbar['command'] = self.yview

      tkinter.Listbox.__init__(self, self.frame, **kwargs)
      self.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)

      text_meths = vars(tkinter.Text).keys()
      methods = vars(tkinter.Pack).keys() | vars(tkinter.Grid).keys() | vars(tkinter.Place).keys()
      methods = methods.difference(text_meths)

      for m in methods:
         if m[0] != '_' and m != 'config' and m != 'configure':
            setattr(self, m, getattr(self.frame, m))

   def __str__(self):
      return str(self.frame)

   def destroy(self):
      super().destroy()
      self.frame.destroy()


class HTMLText(itkHTMLScrolledText):
   # Modified to have no borders by default
   def __init__(self, *args, html=None, **kwargs):
      super().__init__(*args, html=None, **kwargs)
      self.configure(borderwidth=0, highlightthickness=0)

   def _w_init(self, kwargs):
      super()._w_init(kwargs)
      self.vbar.pack_forget()

   def fit_height(self):
      super().fit_height()
      self.vbar.pack_forget()
# ----------------------------------------------------


class itkScrolledListBox(itkBaseWidget, ScrolledListbox):
   _intName = 'ScrolledListBox'

   def __init__(self, master=None, **kwargs):
      self._sbscaling = kwargs.pop('sbscaling', True)
      self._sbwidth = kwargs.pop('sbwidth', 12)
      super().__init__(ScrolledListbox, master, **kwargs)

   def update(self):
      nm = self._window.mult
      if self._sbscaling:
         self.vbar['width'] = self._sbwidth*nm
      self.place(x=self._x*nm, y=self._y*nm, width=self._width*nm, height=self._height*nm, anchor=self._anchor)

   @property
   def sbscaling(self):
      return self._sbscaling

   @sbscaling.setter
   def sbscaling(self, value):
      self._sbscaling = value
      self.update()

   @property
   def sbwidth(self):
      return self._sbwidth

   @sbwidth.setter
   def sbwidth(self, value):
      self._sbwidth = value
      self.update()


class _ComboLabelWithRadioButtons(tkinter.Label):
   def __init__(self, master=None, **kwargs):
      numOptions = kwargs.pop('numOptions', 2)
      self.frame = tkinter.Frame(master)
      self.radiobuttons = []
      self.rbvar = tkinter.IntVar()
      tkinter.Label.__init__(self, self.frame, anchor='nw', **kwargs)
      self.pack(side='top', fill='both')
      for i in range(numOptions):
         self.radiobuttons.append(tkinter.Radiobutton(self.frame, variable=self.rbvar, anchor='nw', value=i))
         self.radiobuttons[i].pack(side='top', fill='both')
      text_meths = vars(tkinter.Label).keys()
      methods = vars(tkinter.Pack).keys() | vars(tkinter.Grid).keys() | vars(tkinter.Place).keys()
      methods = methods.difference(text_meths)
      for m in methods:
         if m[0] != '_' and m != 'config' and m != 'configure':
            setattr(self, m, getattr(self.frame, m))


class ComboLabelWithRadioButtons(itkBaseWidget, tkinter.Label):
   _intName = 'ComboLabelWithRadioButtons'

   def __init__(self, master=None, **kwargs):
      # TODO: Add a Label widget for every radiobutton because radiobutton.foreground also changes the button colour
      super().__init__(_ComboLabelWithRadioButtons, master, **kwargs)

   def updateText(self):
      temp = (self._font, cmath.resizefont(self._fontSize, self._window.fontmult), self._fontStyle)
      self['font'] = temp
      for i in self.radiobuttons:
         i['font'] = temp

   @property
   def selected(self):
      return self.rbvar.get()

   @selected.setter
   def selected(self, value: int):
      self.rbvar.set(value)

   def updateBackground(self):
      self.frame['bg'] = self._bg
      self['background'] = self._bg
      for i in self.radiobuttons:
         i.configure(background=self._bg, highlightbackground=self._bg)

   def updateForeground(self):
      self['foreground'] = self._fg
      for i in self.radiobuttons:
         i.configure(foreground=self._fg)

   def updateState(self):
      self['state'] = self._state
      for i in self.radiobuttons:
         i.configure(state=self._state)

   def _setText(self, text):
      if isinstance(text, (list, tuple)) and len(text) == 2:
         self.radiobuttons[text[0]]['text'] = text[1]
      else:
         self['text'] = text

   text = property(fset=_setText)  # This can not have a get method because get does not accept arguements


class CheckboxWithLabel(itkBaseWidget, tkinter.Label):
   _intName = 'CheckboxWithLabel'

   def __init__(self, master=None, **kwargs):
      self.frame = tkinter.Frame(master)
      self._cbvar = tkinter.BooleanVar()
      self.cb = tkinter.Checkbutton(self.frame, variable=self._cbvar)
      super().__init__(tkinter.Label, self.frame, **kwargs)
      self['anchor'] = 'w'  # Right align text

   def update(self):
      nm = self._window.mult
      h = self._height*nm
      self.frame.place(x=self._x*nm, y=self._y*nm, width=self._width*nm, height=h, anchor=self._anchor)
      self.cb.place(x=0, y=0, width=h, height=h, anchor='nw')
      self.place(x=h, y=0, width=(self._width-self._height)*nm, height=h, anchor='nw')

   def updateText(self):
      self['font'] = (self._font, cmath.resizefont(self._fontSize, self._window.fontmult), self._fontStyle)

   def updateState(self):
      self['state'] = self._state
      self.cb['state'] = self._state

   def select(self):
      self.cb.select()

   def deselect(self):
      self.cb.deselect()

   def getcb(self):
      return self._cbvar.get()

   def updateBackground(self):
      self.frame['bg'] = self._bg
      self['background'] = self._bg
      self.cb['background'] = self._bg
      self.cb['highlightbackground'] = self._bg


class CheckboxWithEntry(itkBaseWidget, tkinter.Entry):
   _intName = 'CheckboxWithEntry'

   def __init__(self, master=None, **kwargs):
      self._indent = kwargs.pop('indent', 0)
      self._cbvar = tkinter.BooleanVar()
      self._entryvar = tkinter.StringVar()
      self.frame = tkinter.Frame(master)
      self.cb = tkinter.Checkbutton(self.frame, variable=self._cbvar, command=self.checkCB)
      self.l1 = tkinter.Label(self.frame, text=kwargs.pop('text', ''), anchor='w')
      self.l2 = tkinter.Label(self.frame, anchor='w')
      self._entrytextwidth, self.l2['text'] = kwargs.pop('entrytext', (0, ''))
      super().__init__(tkinter.Entry, self.frame, textvariable=self._entryvar, **kwargs)
      self['state'] = 'disabled'

   def update(self):
      nm = self._window.mult
      h = self._height*nm
      self.frame.place(x=self._x*nm, y=self._y*nm, width=self._width*nm, height=h*2, anchor=self._anchor)
      self.cb.place(x=0, y=0, width=h, height=h, anchor='nw')
      self.l1.place(x=h, y=0, width=(self._width-self._height)*nm, height=h, anchor='nw')
      self.l2.place(x=self._indent*nm, y=h, width=self._entrytextwidth*nm, height=h, anchor='nw')
      self.place(x=(self._indent+self._entrytextwidth)*nm, y=h, width=(self._width-self._indent-self._entrytextwidth)*nm, height=h, anchor='nw')

   def updateText(self):
      temp = (self._font, cmath.resizefont(self._fontSize, self._window.fontmult), self._fontStyle)
      self['font'] = temp
      self.l1['font'] = temp
      self.l2['font'] = temp

   def updateState(self):
      self['state'] = self._state
      self.l1['state'] = self._state
      self.l2['state'] = self._state
      self.cb['state'] = self._state

   def checkCB(self):
      if self._cbvar.get():
         self._enable()
      else:
         self._disable()

   def _enable(self):
      self['state'] = 'normal'

   def _disable(self):
      self['state'] = 'disabled'

   def select(self):
      self.cb.select()
      self._enable()

   def deselect(self):
      self.cb.deselect()
      self._disable()

   def get(self):
      return self._entryvar.get()

   def set(self, value):
      self._entryvar.set(value)

   def getcb(self):
      return self._cbvar.get()

   def updateBackground(self):
      self.frame['bg'] = self._bg
      self.cb['background'] = self._bg
      self.cb['highlightbackground'] = self._bg
      self.l1['background'] = self._bg
      self.l2['background'] = self._bg

   def updateForeground(self):
      self.l1['foreground'] = self._fg
      self.l2['foreground'] = self._fg


class CheckboxWithCombobox(itkBaseWidget, Combobox):
   _intName = 'CheckboxWithCombobox'

   def __init__(self, master=None, **kwargs):
      self._indent = kwargs.pop('indent', 0)
      self._cbvar = tkinter.BooleanVar()
      self.frame = tkinter.Frame(master)
      self.cb = tkinter.Checkbutton(self.frame, variable=self._cbvar, command=self.checkCB)
      self.l1 = tkinter.Label(self.frame, text=kwargs.pop('text', ''), anchor='w')
      self.l2 = tkinter.Label(self.frame, anchor='w')
      self._readonly = kwargs.pop('readonly', True)
      self._entrytextwidth, self.l2['text'] = kwargs.pop('entrytext', (0, ''))
      super().__init__(Combobox, self.frame, **kwargs)
      self.checkCB()

   def update(self):
      nm = self._window.mult
      h = self._height*nm
      self.frame.place(x=self._x*nm, y=self._y*nm, width=self._width*nm, height=h*2, anchor=self._anchor)
      self.cb.place(x=0, y=0, width=h, height=h, anchor='nw')
      self.l1.place(x=h, y=0, width=(self._width-self._height)*nm, height=h, anchor='nw')
      self.l2.place(x=self._indent*nm, y=h, width=self._entrytextwidth*nm, height=h, anchor='nw')
      self.place(x=(self._indent+self._entrytextwidth)*nm, y=h, width=(self._width-self._indent-self._entrytextwidth)*nm, height=h, anchor='nw')

   def updateText(self):
      temp = (self._font, cmath.resizefont(self._fontSize, self._window.fontmult), self._fontStyle)
      self.l1['font'] = temp
      self.l2['font'] = temp
      self['font'] = temp

   def _getState(self):
      if self._state == 'normal':
         return 'readonly' if self._readonly else 'normal'
      return 'disabled'

   def updateState(self):
      self['state'] = self._getState()
      self.l1['state'] = self._state
      self.l2['state'] = self._state
      self.cb['state'] = self._state

   def checkCB(self):
      if self._cbvar.get():
         self._enable()
      else:
         self._disable()

   def _enable(self):
      self['state'] = 'readonly' if self._readonly else 'normal'

   def _disable(self):
      self['state'] = 'disabled'

   def select(self):
      self.cb.select()
      self._enable()

   def deselect(self):
      self.cb.deselect()
      self._disable()

   def getcb(self):
      return self._cbvar.get()

   def updateBackground(self):
      self.frame['bg'] = self._bg
      self.l1['background'] = self._bg
      self.l2['background'] = self._bg
      self.cb['background'] = self._bg
      self.cb['highlightbackground'] = self._bg

   def updateForeground(self):
      self.l1['foreground'] = self._fg
      self.l2['foreground'] = self._fg


class FileEntryBox(itkBaseWidget, tkinter.Entry):
   _intName = 'FileEntryBox'

   def __init__(self, master=None, **kwargs):
      self.filetype = kwargs.pop('filetype', 'dir')
      self.fileaction = kwargs.pop('fileaction', 'open')
      self.initdir = kwargs.pop('initdir', None)
      self.initfile = kwargs.pop('initfile', None)
      self._indent = kwargs.pop('indent', 0)
      self._entryvar = tkinter.StringVar()
      self.frame = tkinter.Frame(master)
      self.l1 = tkinter.Label(self.frame, text=kwargs.pop('text', ''), anchor='w')
      self.l2 = tkinter.Label(self.frame, anchor='w')
      self._entrytextwidth, self.l2['text'] = kwargs.pop('entrytext', (0, ''))
      self.filebutton = tkinter.Button(self.frame, command=self.selectfile)
      super().__init__(tkinter.Entry, self.frame, textvariable=self._entryvar, **kwargs)

   def update(self):
      nm = self._window.mult
      h = self._height*nm
      self.frame.place(x=self._x*nm, y=self._y*nm, width=self._width*nm, height=h*2, anchor=self._anchor)
      self.l1.place(x=0, y=0, width=(self._width-self._height)*nm, height=h, anchor='nw')
      self.l2.place(x=self._indent*nm, y=h, width=self._entrytextwidth*nm, height=h, anchor='nw')
      self.place(x=(self._indent+self._entrytextwidth)*nm, y=h, width=(self._width-self._indent-self._entrytextwidth-self._height)*nm, height=h, anchor='nw')
      self.filebutton.place(x=(self._width-self._height)*nm, y=h, width=h, height=h, anchor='nw')

   def updateText(self):
      temp = (self._font, cmath.resizefont(self._fontSize, self._window.fontmult), self._fontStyle)
      self.l1['font'] = temp
      self.l2['font'] = temp
      self['font'] = temp

   def selectfile(self):
      if self.filetype == 'dir':
         file = filedialog.askdirectory(initialdir=self.initdir)
      elif self.filetype == 'file':
         if self.fileaction == 'open':
            file = filedialog.askopenfilename(initialdir=self.initdir, initialfile=self.initfile)
         elif self.fileaction == 'save':
            file = filedialog.asksaveasfilename(initialdir=self.initdir, initialfile=self.initfile)
      if not (isinstance(file, tuple) or file == ''):
         self._entryvar.set(file)

   def get(self):
      return self._entryvar.get()

   def set(self, value):
      self._entryvar.set(value)

   def updateBackground(self):
      self.frame['bg'] = self._bg
      self.l1['background'] = self._bg
      self.l2['background'] = self._bg
      self.filebutton['background'] = self._bg

   def updateForeground(self):
      self.l1['foreground'] = self._fg
      self.l2['foreground'] = self._fg


class ComboEntryBox(itkBaseWidget, tkinter.Button):
   _intName = 'ComboEntryBox'

   def __init__(self, master=None, **kwargs):
      self._textwidth = kwargs.pop('textwidth')
      self._buttonwidth = kwargs.pop('buttonwidth')
      self._rows = kwargs.pop('rows', 1)
      self._buttontext = kwargs.pop('buttontext', 'Ok')
      text = list(kwargs.pop('text'))
      if len(text) != self._rows:
         raise Error()
      self.frame = tkinter.Frame(master)
      if self._rows < 1:
         raise Exception(f'ComboEntryBox; rows must be greater than or equal to 1, got {self._rows}')
      self.labels = [tkinter.Label(self.frame, text=text[i], anchor='w') for i in range(self._rows)]
      self.entries = [tkinter.Entry(self.frame) for i in range(self._rows)]
      super().__init__(tkinter.Button, self.frame, text=self._buttontext, **kwargs)

   def update(self):
      nm = self._window.mult
      self.frame.place(x=self._x*nm, y=self._y*nm, width=self._width*nm, height=(self._height*self._rows)*nm, anchor=self._anchor)
      for i, item in enumerate(self.labels):
         item.place(x=-2*nm, y=i*self._height*nm, width=(self._textwidth+2)*nm, height=self._height*nm, anchor='nw')
      for i, item in enumerate(self.entries):
         item.place(x=self._textwidth*nm, y=i*self._height*nm, width=(self._width-(self._textwidth+self._buttonwidth)-1)*nm, height=self._height*nm, anchor='nw')
      self.place(x=(self._textwidth+(self._width-(self._textwidth+self._buttonwidth)))*nm, y=((self._rows-1)*self._height)*nm if self._rows > 1 else 0, width=self._buttonwidth*nm, height=self._height*nm, anchor='nw')

   def updateText(self):
      temp = (self._font, cmath.resizefont(self._fontSize, self._window.fontmult), self._fontStyle)
      for i in self.labels:
         i['font'] = temp
      for i in self.entries:
         i['font'] = temp
      self['font'] = temp

   def updateBackground(self):
      self.frame['bg'] = self._bg
      for i in self.labels:
         i['background'] = self._bg
      self['background'] = self._bg

   def updateForeground(self):
      for i in self.labels:
         i['foreground'] = self._fg
      self['foreground'] = self._fg

   def getEntry(self, number, *args):
      return self.entries[number].get()

   def getEntries(self, *args):
      return [i.get() for i in self.entries]

   def destroy(self):
      super().destroy()
      self.frame.destroy()


class itkDisplay(itkFrame):
   _intName = 'display'

   def update(self):
      nm = self._window.mult
      self.place(x=self._window.width//2, y=self._window.height//2, width=self._window._startwidth*nm, height=self._window._startheight*nm, anchor='center')


class itkImage:
   _intName = 'Image'

   def __init__(self, window, data, size):
      self._window = window
      self._data = data
      self.img = ''
      if size is None:
         size = PIL.Image.open(BytesIO(data)).size
      self._size = [size[0], size[1]]

   def resize(self, *e):
      nm = self._window.mult
      img = PIL.Image.open(BytesIO(self._data))
      img.thumbnail((self._size[0]*nm, self._size[1]*nm))
      self.img = PIL.ImageTk.PhotoImage(img)


class itkBlankImage:
   _intName = 'BlankImage'
   img = ''
   __init__ = _nullFunc
   resize = _nullFunc


class itkAboutWindow:
   '''
   Example implementation of About Window
   '''
   def __init__(self, itkWindow):
      self._open = False
      self._text = 'placeholdertext'
      self._window = itkWindow

   def open(self, *e):
      if self._open:
         self.toplevel.lift()
      else:
         self.toplevel = tkinter.Toplevel()
         self.toplevel.geometry('350x155')
         self.toplevel.resizable(False, False)
         self.toplevel.transient(self._window)
         self.toplevel.bind('<Destroy>', self.close)
         self.label = tkinter.Label(self.toplevel, font=('TkTextFont', 9), anchor='w', justify='left', text=self._text)
         self.label.place(x=7, y=9, anchor='nw')
         self.okButton = tkinter.Button(self.toplevel, text='OK', command=self.close)
         self.okButton.place(x=299, y=115, width=29, height=29, anchor='nw')
         self._open = True

   def close(self, *e):
      if self._open:
         self.toplevel.destroy()
         self._open = False

   @property
   def text(self):
      return self._text

   @text.setter
   def text(self, text):
      self._text = text
      if self._open:
         self.label['text'] = text

   @property
   def isOpen(self):
      return self._open


DefaultIcon = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00d\x00\x00\x00d\x08\x06\x00\x00\x00p\xe2\x95T\x00\x00\x01\x84iCCPICC profile\x00\x00(\x91}\x91=H\xc3@\x1c\xc5_[\xa5R*\n\x16\x11q\xc8P\x9d\xecbE\x1ck\x15\x8aP!\xd4\n\xad:\x98\\\xfa\x05M\x1a\x92\x14\x17G\xc1\xb5\xe0\xe0\xc7b\xd5\xc1\xc5YW\x07WA\x10\xfc\x00qvpRt\x91\x12\xff\x97\x14Z\xc4xp\xdc\x8fw\xf7\x1ew\xef\x00\x7f\xb3\xcaT\xb3\'\x01\xa8\x9aedRI!\x97_\x15\x82\xaf\x08a\x10\xc3\x88#&1S\x9f\x13\xc54<\xc7\xd7=||\xbd\x8b\xf1,\xefs\x7f\x8e~\xa5`2\xc0\'\x10\'\x98nX\xc4\x1b\xc43\x9b\x96\xcey\x9f8\xc2\xca\x92B|N<i\xd0\x05\x89\x1f\xb9.\xbb\xfc\xc6\xb9\xe4\xb0\x9fgF\x8clf\x9e8B,\x94\xbaX\xeebV6T\xe2i\xe2\xa8\xa2j\x94\xef\xcf\xb9\xacp\xde\xe2\xacV\xeb\xac}O\xfe\xc2pA[Y\xe6:\xcd1\xa4\xb0\x88%\x88\x10 \xa3\x8e\n\xaa\xb0\x10\xa3U#\xc5D\x86\xf6\x93\x1e\xfeQ\xc7/\x92K&W\x05\x8c\x1c\x0b\xa8A\x85\xe4\xf8\xc1\xff\xe0w\xb7f1>\xe5&\x85\x93@\xef\x8bm\x7f\x8c\x03\xc1]\xa0\xd5\xb0\xed\xefc\xdbn\x9d\x00\x81g\xe0J\xeb\xf8kM`\xf6\x93\xf4FG\x8b\x1e\x01\x03\xdb\xc0\xc5uG\x93\xf7\x80\xcb\x1d`\xe4I\x97\x0c\xc9\x91\x024\xfd\xc5"\xf0~F\xdf\x94\x07\x86n\x81\xd0\x9a\xdb[{\x1f\xa7\x0f@\x96\xbaJ\xdf\x00\x07\x87\xc0D\x89\xb2\xd7=\xde\xdd\xd7\xdd\xdb\xbfg\xda\xfd\xfd\x00\x05xr\xe1\xf0a\xe0\x07\x00\x00\x00\x06bKGD\x00\xff\x00\xff\x00\xff\xa0\xbd\xa7\x93\x00\x00\x00\tpHYs\x00\x00\x0fa\x00\x00\x0fa\x01\xa8?\xa7i\x00\x00\x00\x07tIME\x07\xe8\n\x10\x164\x05\xff\x81\xa4\xcb\x00\x00\x07nIDATx\xda\xed\xddkP\x94U\x18\x07\xf0\xff^`wA\x04aq\x11\xc6\x15\r\xb1`0\xc7\x0b:\xa2\x94\x95]Dq\xfcP*\xe3P\xe9\x989YF^\xc6\x19\xbb\xd9\xe8\xe8\x98a\xa3ejcN\x9a\xd0\xa81~\xc84\t\x99Ra\x08\xc4\xcb\x98\xa6\x90\x86\x88\x97PP\x89\xe5\xba\x9c>,\x97].\xc9\xbb\xbb\xe7\xbc\xe7=\xbc\xe7\xd3\xb2\x03\xbb\xcf\xf2\x9bs\x9es_MN\xcc(\x82>P\x08\x00B\x00\x02\xe2x\xdc\xfa\xa4\xe3q\xc7s\x84\xb4\xfd>q\xfa\x9b\xd6\xdf\xef\xe69\xd2\xfa"\x1d?\x03\x84\x10\x10\xe7\xf7\xed\xee\xb9N\xef\xdd\xf6\x1aZ\x15\x83\x1f\x8c>\x01\xa2$\x0c\x02"6\x88\xd20\x84\xae!J\xc4 DP\x10\xa5b@\xc4\x1a\xa2d\x0c\xe1\x9a,\xa5c\x08\x95\xd4E\xc0\x10&\x87\x88\x82!D\x93%\x12\x86\xe2AD\xc3Pt/KD\x0cB\x14\x9a\xd4E\xc5Pd\x93%2\x86\xe2@D\xc7P\x14H_\xc0 \x00\xf4*FW\x0c\xe8t\xe8?\xc4\x8a~\x91V\x18\x82\x83a2\x9b\xe1\x13\xd0\x0f\xa77\xa6S\xc5\x00!\xfc\x83\xb0\xc2\x08\x8a\x8dA\xf8\x94DX&\x8c\x87\xf9\xc98\xe8\x8c\xc6.\xb1\x14mL\xa7\x8a\xc1}\r\xa1\x8da\x08\t\xc6\xb0\xb9\xb3\x119s:\x02"\x87<:\x1e\xca\x18\\\x83\xd0\xc4\xf0\x8f\x88@\xcc[obHr\x12\xb4\xbe\xbe\xd2b\xa2\x88\xc1-\x08-\x0c\x9d\x9f\t#\x16\xbc\x86\xc7\xdfX\x00\x9d\xc1\xe0F\\t1\x08\xe1\x10\x84\x16\x86%1\x01\xf1\xeb\xd7\xc2\x18j\xf6(6\x9a\x18\x04\x9c%u\x1a\x18Z\x83\x01q+\xd30|^\n\xa0\xd1x\x1c M\x0c\xf0\xd4d\xd1\xc0\xf0\t\x0cD\xc2\xf6-0\x8f\x19\xed\xbd\x18)bp\x93Ch`\xf8E\x84c\xf2\xae\xed\x08\x186\xd4\xbbqR\xc4\xe0"\x87\xd0\xc0\xf0\xb7\x0e\xc6\x94\xccoa\x0c\r\xf5r\xact1d\x9f:\xa1\x81\xe1;`\x00&}\xbd\xcd\xeb\x18\xe8\x12\x8b\xf71d]S\xa7\x92\xc0\x8d\x06L\xfcj\x0b\x02\x86F\xd2\x89\x992\x86l9\x84V\xd7v\xec\xba50\x8f\x1e\xe5\xf5x\x9b\xeb\xea\x1ds\\\x941d\xe9e\xd1\xc2\xb0&\'\xc1:#\xc9\xe3\xf8\xea\xab\xabq\xed\xc81\xdc)>\x8b\xca\x0b\x7f\xa0\xba\xf4/\xd8\x9b\xedL0\x98\'uZ\x18\xa6\xf00\x8c\xfep\xb5G\xb1U\x97\x94\xe2\xec\x97;p\xf5\xf0Q\xd8\x9b\x9b\x99$\xf0\xce\x18L\x9b,\x9asS\xf1\x1b\xd6\xc1\xa7\x7f\x80[q5\xd5\xd6\xa2h\xd3\xe7\xb8\xb8\'\x03---L\xba\xb6=a0\x03\xa1\x89\x111\xf5Y\x0c\x9c\x10\xefV\\U\x97\xfeD\xf6\xa2%\xa8)\xaf`2\xe8{\x14\x06\x93\xa9\x13\x9a\x18\x1a\xad\x0e#\x97\xa7\xb9\x15WYv\x0er\xd3V\xa0\xb9\xb6\x8e\x1b\x0c\xea9\x84\xf6z\xc6\xb09/\xbb\xd5\xc5\xbd\xf1\xdbI\x1c\x7f\xfb=\xd8\x1b\x1a\xb9\xc2\x00\xcd\x81!m\x0c\xad\xd1\x80\xd8%\x8b%\xc7u\xbb\xa0\x10\xd9\x8b\x96p\x89Am\xa4\xceb\xd9\xd5:#\tFs\x88\xa4\xb8\xea\xee\xde\xc3\xf1\xa5\xcb`\xafo\xe0\x12\x83\n\x08\xab5\xf0\xa8\xb9\xb3\xa5\xc5e\xb7\xe3\xf8\xd2e\xb0\xdd\xa9\xe4\x16\xc3\xebS\'\xac0\x82G\xc6!8.VRl\x972\xf7\xe3V^\x01\xd7\x18^=\x8e\xc0r\xabNT\x8a\xb4\xda\xd1p\xff\x01\x8a\xd3\xb7r\x8f\xe1\xb5&\x8b%\x86\xceh\x80u\xda\x8b\x92\xe2+\xfct3\xea\xaa\xab\xb9\xc7\xf0J/\x8b\xf5&6K\xc2D\xe8M\xc6^\xc7W{\xfb6.\x1f\xc8R\x04\x86\xc7#u9\xb6wF<\xf3\x94\xb4\x01\xe0/\xb9\x08\x8b\x1f\xeb\xf2\xa1\xe1\xfc\xde\x9d0\xda\xfe\xf1e\'\xf3\x98c\x10B\xa0q\xf7\xae\x13Y\xf6\xdaj4\x98u2\x07~\x16\x0b\xf5\xe9\x9etk4s\x0c\xb7s\x88\\\x1b\x9f\x07\xc4\xc60\xc1\x80\x0c5\xc3\xedq\x88\x9c\xbb\xd0\xa56W\x9e.\x0f\xb2\xc6\x90\x9c\xd4\xe5>\x12\x10\x918\x99\xed\xda\rc\x0cI\xe3\x10\xb91|\x03\xfb#D\xe2`\xd0+ \x0c1z=R\xe7\xe1\xb0\xcc\xa0I\t\xd0\xe8t\xb2\xacn\xb2\xc2\xe8U\x0e\xe1\xe5\xe4Rxb\x02\xdb\xb5\x7f\x190\x1e\t\xc2\x0b\x86F\xa7c\x9a?:\xa2f\x8b\xf1\xbf <\x9d\xe9\xb3\x8c\x1f\x07\x93\x07\xbb\xd6=o\xb6\xd8`\xa0\xa7\xa4\xce\xdb\x01\xcb\xa1\xd3\xa7\xf5\t\x8cn\x93:o\x18\x1a\xbd\x0f\x86\xbc0\x95=\x88\x0c\x18]\x9a,\x1e\x8f\x1e\x0f~\xe6i\x18\x82\x02\xe5\xa9!\x8c1\\&\x17y=\x07\xfeDj\x8a\xa4\x7f\xe4\xe9m;q\xfdT~\xb7\xa3m\xe7t\xdd\xf93\xa2\x87\xcf\xcc\x12\xa3}\xd7\t\xaf\x18A\xd1Q\x18$e\xcf\x15!8\xbb{\x0fj\xff\xa9\x94u\n\xdd]\x0c\x02@\xcb\xf3\r\t\xb1\xaf\xa7J:\x86v\xaf\xa4T\xd1\x18\x00\x81\x96W\x0c\xff\x88pD\xcdJ\x96\xd4\\\x95\xfe\xf4\xb3\xa21Zk\x08\x9fw\x87\x8cI{\x07:\tg\xc8A\x08.\xfdpH\xd1\x18\x84\xb45Y\x9ca\x04GG#j\xe6tI\xb5\xe3fQ1\xee\x97]W4F{\x0e\xe1\tC\xa3\xd1"a\xedG\x92\'\x12/\x1e\xccR<\x86c\x1c\xc2\xd9\x15G\xb1\xf3Sa\x19+\xed\x18s\xe3\xbf\xb5\xb8\xf2\xe3Q\xc5c\x10\x90\xb6&\x8b\x0f\x0c\xf3\xc88\x8c[\xfe\xae\xe4A\xdc\xb9\xbd\xfbP_S\xa3x\x0ctN\xearb\x98\x06\x86b\xea\x8e\xad\x92\xef i\xb2\xd5\xa1h\xe77B`\xb8$u91\x8c\xe6\x10\xbc\xb4w\x17\xfc\xc3,n\xd4\x8e\x0c\xd8\xeeU\t\x81\xe120\x94\x0b#h\xf8cH>\x98\x81\xe0\xe8\xe1\x921\x1ajjP\xb8c\x970\x18\x04\x80^.\x0c\xadV\x87\x11)\xaf`\xfc\xaa\x15\xd0\xfb\x99\xdc\x9a\x00<\xb1\xe13\xd8*+\x85\xc1h\x9f\\d\x89\xe1\x17\x16\x86\xc8\xe7\x9fCLj\n\x02=\xb8\x87\xa4\xa2\xa8\x18\xe7\xbf\xcb\x14\n\x83\x10\x02=\x0b\x8c9\xbf\x9f@\xb3\xcd\x06\xbd\xbf\x1fL!!\xf0\xb4\xd8\x1b\x1b\x91\xbdr\xb5\xd3\xa9Y10\x00@\xcf\xa2f\x98\xcc!\x00<\x87h+9\xef\xaf\xc1\xdd\x92R\xe10\x1cI\x9dA3\xe5\xcdrf\xf7\x1e\x9c\xcf\xdc/$\x06\xe0<\x97E\xb37\xe5\xa5Rv"\x0f\xb9\x9f\xac\x17\x16\xa3\x1d\x84v\xd7\xd6\x1b\xe5FA!\x0e-\\\xdcz\xed\x85\x98\x18p\xac\xa9\xd3\xbf~\xdb\xf3\x9aq\n\x07\xe7\xcdGc\xadMh\x0c\xb8\xae\x18\xd2\xbb\x0b\xdd\x93r~\xdf\xf7\xc8zu!\x9a\xea\xeb\x85\xc7@\xdb\xc0\x90\xf6\xc5\xf4\xee\x94\xa6\xba:\xe4\xac\xfe\x18\x17\x0ed\t\x9d3\xba\x82P\xc6p\x87\xa3<\xbf\x00\xd9\xab>@\xd5\xd5k}\n\xc3\t\x84\xfeW6\xf4\xa6\xdc\xbd|\x05\xf9\x9b\xbf\xc0\x95\xc3G\x84\x1b\x81\xf7\xb6\x7f\xa3\x97\x1b\x83\xb4\xb4\xa0<\xbf\x00\xe7\xf6f\xa0\xe4h6\x88\xdd\xdeg1\x00@\xcf\xe2\xcbL\xba[\xc3\xb8U|\x06\x7f\xe7\xfe\x8a\x92#\xc7\xf0\xe0F\x850\xeb\x19\x9e`t\xca!\xf4\xbeY&o\xc3&4\xd9\xea\xf0\xb0\xe2&\x1e\x96\x97\xa3\xaa\xf5\x1eC\x11\xd6\xc0\xbd\x89\x01\x00\x9a\xcc\xa8X"\xf7\xd7\xfc\xa8\x18]\xc6!*\x06\x0f\x18\x0e\x10\x15\x83\x1b\x0c\xa7\xb9,\x15\x83\x07\x8c\xd6\xb9,\x15\x83\x17\x0c\x97\xe9w\x15C~\x8c\x9e\x93\xba\x8a!\x0bF\xf7I]\xc5\x90\r\xa3kRW1d\xc5pM\xea*\x86\xec\x18\xdd,P\xa9\x18rb\xc0u\xd7\x89\x8a!7\x86S\xb7W\xc5\xe0\x01\xa3\x15D\xc5\xe0\x05\xa3\xa3\x97\xa5bp\x81\xe1\xe8e\xa9\x18\xdc`\xb8N\x9d\xa8\x18\xb2c\x00\xc0\x7f\xe7\x06\xe8\xb1iL\xc9O\x00\x00\x00\x00IEND\xaeB`\x82'


class itkWorkaroundWindow(tkinter.Tk):
   _intName = 'itkWorkaroundWindow'

   def __init__(self):
      self._destroyed = False
      super().__init__()
      self.withdraw()

   wm_deiconify = _nullFunc
   deiconify = _nullFunc

   def destroy(self, *e):
      if not self._destroyed:
         self._destroyed = True
         super().destroy()
         del as3state.windows[0]


class itkRoot(tkinter.Toplevel):
   '''
   This is a subclass of tkinter.Toplevel that provides extra functionality.

   Notes:
      Calling mainloop() on this window will raise an Error. Use itkRootMain
      for that.

      Tkinter requires one window, and only one window, to be of class
      tkinter.Tk. This window is automatically created when the first
      interface_tk window is created and destroyed when the last interface_tk
      is destroyed. It lives at as3state.windows[0] and should not be used as a
      window. It's only purpose is to be the required tkinter.Tk window.
   '''
   _intName = 'Window'

   def __init__(self, **kwargs):
      self._id = next(_windowID)
      self._startwidth = kwargs.pop('defaultWidth', kwargs.pop('width'))
      self._startheight = kwargs.pop('defaultHeight', kwargs.pop('height'))
      self._title = kwargs.pop('title', 'Python')
      self._color = kwargs.pop('background', kwargs.pop('bg', '#FFFFFF'))
      self._menu = kwargs.pop('menu', True)
      self._defaultMenu = kwargs.pop('defaultMenu', True)  # Use default menu items
      self._fullscreen = False
      self._resizable = False
      self._children = {}
      self.menubar = {}
      self.images = {'': itkBlankImage()}
      ico = kwargs.pop('icon', DefaultIcon)
      if not as3state.windows:
         as3state.windows[0] = itkWorkaroundWindow()
      tkinter.Toplevel.__init__(self, **kwargs)
      self._mult = 1
      self._fontmult = 100
      self.geometry(f'{self._startwidth}x{self._startheight}')
      self.title(self._title)
      if as3state.width not in {-1, None} and as3state.height not in {-1, None}:
         self.maxsize(as3state.width, as3state.height)
      self.bind('<Configure>', self.doResize)
      self.bind('<Escape>', self.outfullscreen)
      self.icon = ico
      if self._menu:
         if self._defaultMenu:
            self.menubar['root'] = tkinter.Menu(self, bd=1)
            self.menubar['filemenu'] = tkinter.Menu(self.menubar['root'], tearoff=0)
            self.menubar['filemenu'].add_command(label='Quit', font=('Terminal', 8), command=self.close)
            self.menubar['root'].add_cascade(label='File', font=('Terminal', 8), menu=self.menubar['filemenu'])
            self.menubar['viewmenu'] = tkinter.Menu(self.menubar['root'], tearoff=0)
            self.menubar['viewmenu'].add_command(label='Full Screen', font=('Terminal', 8), command=self.togglefullscreen)
            self.menubar['viewmenu'].add_command(label='Reset Size', font=('Terminal', 8), command=self.resetSize)
            self.menubar['root'].add_cascade(label='View', font=('Terminal', 8), menu=self.menubar['viewmenu'])
            self.menubar['controlmenu'] = tkinter.Menu(self.menubar['root'], tearoff=0)
            self.menubar['controlmenu'].add_command(label='Controls', font=('Terminal', 8))
            self.menubar['root'].add_cascade(label='Control', font=('Terminal', 8), menu=self.menubar['controlmenu'])
            self.config(menu=self.menubar['root'])
         else:
            self.menubar['root'] = tkinter.Menu(self, bd=1)
            self.config(menu=self.menubar['root'])
      self._children['display'] = itkDisplay(self, itkWindow=self, background=self._color)
      self._children['display'].update()
      as3state.windows[self._id] = self
      self._destroyed = False  # Variable to prevent destroy being called more than once

   def resetSize(self):
      self.geometry(f'{self._startwidth}x{self._startheight}')

   def forceFocus(self, child: str):
      self._children[child].focus_force()

   def togglefullscreen(self, *e):
      self.fullscreen = not self._fullscreen

   def gofullscreen(self, *e):
      self.fullscreen = True

   def outfullscreen(self, *e):
      self.fullscreen = False

   def _setIcon2(self, img):
      self.iconphoto(True, PIL.ImageTk.PhotoImage(PIL.Image.open(img)))

   def _setIcon(self, fileorbytes):
      if isinstance(fileorbytes, bytes):
         with BytesIO(fileorbytes) as i:  # This doesn't need to stay open as far as I can tell
            self._setIcon2(i)
      elif isinstance(fileorbytes, (str, BytesIO)):
         self._setIcon2(fileorbytes)
      else:
         raise Error('interface_tk.window.setIcon; called but no icon specified')

   icon = property(fset=_setIcon)

   @property
   def fullscreen(self):
      return self._fullscreen

   @fullscreen.setter
   def fullscreen(self, value: bool):
      self._fullscreen = value
      self.attributes('-fullscreen', value)

   @property
   def resizable(self):
      return self._resizable

   @resizable.setter
   def resizable(self, value):
      super().resizable(value, value)
      self._resizable = value

   @property
   def mult(self):
      return self._mult
   
   @mult.setter
   def mult(self, value):
      self._fontmult = value*100
      self._mult = value
      self.resizeChildren()
   
   @property
   def fontmult(self):
      return self._fontmult

   @property
   def width(self):
      return self.winfo_width()

   @width.setter
   def width(self, value):
      self.geometry(f'{value}x{self.width}')

   @property
   def height(self):
      return self.winfo_height()

   @height.setter
   def height(self, value):
      self.geometry(f'{self.width}x{value}')

   def addWidget(self, widget, master: str, name: str, **kwargs):
      if not as3.isXMLName(master):
         raise Error('interface_tk.window.addWidget; Invalid Master')
      if not as3.isXMLName(name):
         raise Error('interface_tk.window.addWidget; Invalid Name')
      self._children[name] = widget(self._children[master], itkWindow=self, **kwargs)
      self._children[name].resize()

   def addButton(self, master: str, name: str, **kwargs):
      self.addWidget(itkButton, master, name, **kwargs)

   def addLabel(self, master: str, name: str, **kwargs):
      self.addWidget(itkLabel, master, name, **kwargs)

   def addnwhLabel(self, master: str, name: str, **kwargs):
      self.addWidget(itknwhLabel, master, name, **kwargs)

   def addFrame(self, master: str, name: str, **kwargs):
      self.addWidget(itkFrame, master, name, **kwargs)

   def addHTMLScrolledText(self, master: str, name: str, **kwargs):
      self.addWidget(itkHTMLScrolledText, master, name, **kwargs)

   def addHTMLText(self, master: str, name: str, **kwargs):
      self.addWidget(HTMLText, master, name, **kwargs)

   def addImage(self, name: str, data, size: tuple = None):
      '''
      size - the target (display) size of the image before resizing
      if size is not defined it is assumed to be the actual image size
      '''
      if name == '':
         raise Error('interface_tk.window.addImage; image_name can not be empty string')
      self.images[name] = itkImage(self, data, size)
      self.images[name].resize()

   def addImageLabel(self, master: str, name: str, **kwargs):
      self.addWidget(itkImageLabel, master, name, **kwargs)

   def addScrolledListbox(self, master: str, name: str, **kwargs):
      self.addWidget(itkScrolledListBox, master, name, **kwargs)

   def addEntry(self, master: str, name: str, **kwargs):
      self.addWidget(itkEntry, master, name, **kwargs)

   def addCheckboxWithLabel(self, master: str, name: str, **kwargs):
      self.addWidget(CheckboxWithLabel, master, name, **kwargs)

   def addCheckboxWithEntry(self, master: str, name: str, **kwargs):
      self.addWidget(CheckboxWithEntry, master, name, **kwargs)

   def addCheckboxWithCombobox(self, master: str, name: str, **kwargs):
      self.addWidget(CheckboxWithCombobox, master, name, **kwargs)

   def addFileEntryBox(self, master: str, name: str, **kwargs):
      self.addWidget(FileEntryBox, master, name, **kwargs)

   def addNotebook(self, master: str, name: str, **kwargs):
      self.addWidget(itkNotebook, master, name, **kwargs)

   def addNBFrame(self, master: str, name: str, **kwargs):
      self.addWidget(itkNBFrame, master, name, **kwargs)

   def addLabelWithRadioButtons(self, master: str, name: str, **kwargs):
      self.addWidget(ComboLabelWithRadioButtons, master, name, **kwargs)

   def resizeChildren(self):
      for i in self.images.values():
         i.resize()
      for i in self._children.values():
         i.resize()

   def bindChild(self, child: str, event, function):
      self._children[child].bind(event, function)

   def configureChildren(self, children: list | tuple, **kwargs):
      for attr, value in kwargs.items():
         if attr == 'textadd':
            for child in children:
               self._children[child].text = self._children[child].text + value
         elif attr in {'x', 'y', 'width', 'height', 'font', 'anchor', 'background', 'text', 'foreground', 'image_name', 'bold', 'sbwidth'}:
            for child in children:
               setattr(self._children[child], attr, value)
         else:
            for child in children:
               self._children[child][attr] = value

   def configureChild(self, child: str, **args):
      for attr, value in args.items():
         if attr == 'textadd':
            value = self._children[child].text + value
            attr = 'text'
         if attr in {'x', 'y', 'width', 'height', 'font', 'anchor', 'background', 'text', 'foreground', 'image_name', 'bold', 'sbwidth'}:
            setattr(self._children[child], attr, value)
         else:
            self._children[child][attr] = value

   def destroyChild(self, child: str):
      if child == 'display':
         return
      self._children[child].destroy()
      self._children.pop(child)

   def getChildAttribute(self, child: str, attribute: str):
      if child in self._children:
         try:
            return getattr(self._children[child], attribute)
         except:
            return self._children[child].cget(attribute)

   def getChildAttributes(self, child: str, *args):
      return {i: self.getChildAttribute(child, i) for i in args}

   def doResize(self, event):
      if event.widget == self:
         mult = cmath.calculate(self.width, self.height, self._startwidth, self._startheight)
         if mult == self.mult:
            self._children['display'].update()
         else:
            self.mult = mult

   def minimumSize(self, **kwargs):
      '''
      kwargs: width, height

      If width or height is missing, it will be calculated based on the one
      that is present and the aspect ratio of the starting dimensions.
      '''
      w = kwargs.pop('width', None)
      h = kwargs.pop('height', None)
      if w is not None and h is not None:
         self.minsize(w, h)
      elif w is not None:
         self.minsize(w, int((w*self._startheight)/self._startwidth))
      elif h is not None:
         self.minsize(int((self._startwidth*h)/self._startheight), h)
      else:
         as3.trace('Invalid type')

   def mainloop(self):
      raise Error('interface_tk.window.mainloop; Can not run mainloop on a child window.')

   def close(self, *e):
      self.destroy()

   def destroy(self, *e):
      if not self._destroyed:
         self._destroyed = True
         super().destroy()
         del as3state.windows[self._id]
         if len(as3state.windows) == 1:
            as3state.windows[0].destroy()


class itkRootMain(itkRoot):
   '''
   This is a subclass of itkRoot providing the following aditional
   capabilities:
      mainloop() can be called on this object.
      This object can have an about window attached to it
   '''
   _intName = 'WindowMain'

   def __init__(self, **kwargs):
      aw = kwargs.pop('aboutWindow', itkAboutWindow)
      super().__init__(**kwargs)
      self.aboutwindow = aw(self)
      if self._menu and self._defaultMenu:
         self.menubar['helpmenu'] = tkinter.Menu(self.menubar['root'], tearoff=0)
         self.menubar['helpmenu'].add_command(label='About', font=('Terminal', 8), command=self.aboutwindow.open)
         self.menubar['root'].add_cascade(label='Help', font=('Terminal', 8), menu=self.menubar['helpmenu'])

   def mainloop(self):
      self.mult = 1
      as3state.windows[0].mainloop()


def window(**kwargs):
   '''
   Returns a window class based on the arguements given. Provided for backwards
   compatibility. All arguements not used by this function will be passed to
   the window's constructor.

   Arguements:
      main = True -> itkRootMain
      main = False -> itkRoot
   '''
   if kwargs.pop('main', False):
      return itkRootMain(**kwargs)
   return itkRoot(**kwargs)


if __name__ == '__main__':
   # Test
   from platform import python_version

   testcolor = 0
   fontBold = False

   def test_changebold():
      global fontBold
      fontBold = not fontBold
      return fontBold

   def test_cyclecolor():
      global testcolor
      testcolorlist = ('#FFFFFF', '#8F2F9F', '#AAAAAA')
      testcolor += 1
      if testcolor >= 3:
         testcolor = 0
      return testcolorlist[testcolor]

   testfont = ('Times New Roman', 12)

   root = window(width=1176, height=662, title='Adobe Flash Projector-like Window Demo', main=True)
   root.aboutwindow.text = f'Adobe Flash Projector-like window demo.\n\nPython {python_version()}'
   root.addButton('display', 'testbutton1', x=130, y=0, width=130, height=30, font=testfont, command=lambda: setattr(root._children['testtext'], 'background', test_cyclecolor()), text='st_colourtest')
   root.addLabel('display', 'testlabel1', x=0, y=30, width=100, height=20, font=testfont, text='TestLabel')
   root.addHTMLScrolledText('display', 'testtext', x=0, y=50, width=600, height=400, font=testfont, text='TestTextpt1\n\nTestTextpt2', cursor='arrow', wrap='word')
   root.addHTMLText('display', 'testtext2', x=601, y=50, width=400, height=400, font=testfont, text='HTMLTextTest\n\ntext', cursor='arrow', wrap='word')
   secondwindow = window(width=400, height=400, title='Second Window', main=False, menu=False)
   secondwindow.group(root)
   root.addButton('display', 'testbutton2', x=0, y=0, width=130, height=30, font=testfont, command=lambda: secondwindow.lift(), text='liftsecondwindow')
   root.addButton('display', 'testbutton3', x=260, y=0, width=130, height=30, font=testfont, command=lambda: setattr(root._children['testtext'], 'bold', test_changebold()), text='st_boldtest')
   root.addScrolledListbox('display', 'testslb', x=0, y=450, width=150, height=150, font=testfont)
   for i in range(1, 21):
      root._children['testslb'].insert('end', i)
   root.mainloop()
