from as3lib import as3state


class Linux:
   def mouseButtonNameToTkNumber(name: str):
      if name == 'Left':
         return 1
      elif name == 'Middle':
         return 2
      elif name == 'Right':
         return 3

   def mouseButtonNameToTkname(name: str):
      if name == 'Left':
         return '<Button-1>'
      elif name == 'Middle':
         return '<Button-2>'
      elif name == 'Right':
         return '<Button-3>'

   def tkeventToMouseButtonName(event):
      if event.num == 1:
         return 'Left'
      elif event.num == 2:
         return 'Middle'
      elif event.num == 3:
         return 'Right'

   def tkeventToJavascriptKeycode(event):
      return {9: 27, 10: 49, 11: 50, 12: 51, 13: 52, 14: 53, 15: 54, 16: 55, 17: 56, 18: 57, 19: 48, 20: 189, 21: 187, 22: 8, 23: 9, 24: 81, 25: 87, 26: 69, 27: 82, 28: 84, 29: 89, 30: 85, 31: 73, 32: 79, 33: 80, 34: 219, 35: 221, 36: 13, 37: 17, 38: 65, 39: 83, 40: 68, 41: 70, 42: 71, 43: 72, 44: 74, 45: 75, 46: 76, 47: 186, 48: 222, 49: 192, 50: 16, 51: 220, 52: 90, 53: 88, 54: 67, 55: 86, 56: 66, 57: 78, 58: 77, 59: 188, 60: 190, 61: 191, 62: 16, 63: 106, 64: 18, 65: 32, 66: 20, 67: 112, 68: 113, 69: 114, 70: 115, 71: 116, 72: 117, 73: 118, 74: 119, 75: 120, 76: 121, 77: 144, 78: 145, 79: 103, 80: 104, 81: 105, 82: 109, 83: 100, 84: 101, 85: 102, 86: 107, 87: 97, 88: 98, 89: 99, 90: 96, 91: 110, 95: 122, 96: 123, 104: 13, 105: 17, 106: 111, 108: 18, 110: 36, 111: 38, 112: 33, 113: 37, 114: 39, 115: 35, 116: 40, 117: 34, 118: 45, 119: 46, 127: 19}.get(event.keycode, None)


class Windows:
   def mouseButtonNameToTkNumber(name: str):
      if name == 'Left':
         return 1
      elif name == 'Middle':
         return 2
      elif name == 'Right':
         return 3

   def mouseButtonNameToTkname(name: str):
      if name == 'Left':
         return '<Button-1>'
      elif name == 'Middle':
         return '<Button-2>'
      elif name == 'Right':
         return '<Button-3>'

   def tkeventToMouseButtonName(event):
      if event.num == 1:
         return 'Left'
      elif event.num == 2:
         return 'Middle'
      elif event.num == 3:
         return 'Right'

   def tkeventToJavascriptKeycode(event):
      # !This could possibly just be "return event.keycode" because all values are the same
      return {8: 8, 9: 9, 13: 13, 16: 16, 17: 17, 18: 18, 19: 19, 20: 20, 27: 27, 32: 32, 33: 33, 34: 34, 35: 35, 36: 36, 37: 37, 38: 38, 39: 39, 40: 40, 45: 45, 46: 46, 48: 48, 49: 49, 50: 50, 51: 51, 52: 52, 53: 53, 54: 54, 55: 55, 56: 56, 57: 57, 65: 65, 66: 66, 67: 67, 68: 68, 69: 69, 70: 70, 71: 71, 72: 72, 73: 73, 74: 74, 75: 75, 76: 76, 77: 77, 78: 78, 79: 79, 80: 80, 81: 81, 82: 82, 83: 83, 84: 84, 85: 85, 86: 86, 87: 87, 88: 88, 89: 89, 90: 90, 91: 91, 96: 96, 97: 97, 98: 98, 99: 99, 100: 100, 101: 101, 102: 102, 103: 103, 104: 104, 105: 105, 106: 106, 107: 107, 109: 109, 110: 110, 111: 111, 112: 112, 113: 113, 114: 114, 115: 115, 116: 116, 117: 117, 118: 118, 119: 119, 120: 120, 121: 121, 144: 144, 145: 145, 186: 186, 187: 187, 188: 188, 189: 189, 190: 190, 191: 191, 192: 192, 219: 219, 220: 220, 221: 221, 222: 222}.get(event.keycode, None)


class Darwin:
   def mouseButtonNameToTkNumber(name: str):
      if name == 'Left':
         return 1
      elif name == 'Middle':
         return 3
      elif name == 'Right':
         return 2

   def mouseButtonNameToTkname(name: str):
      if name == 'Left':
         return '<Button-1>'
      elif name == 'Middle':
         return '<Button-3>'
      elif name == 'Right':
         return '<Button-2>'

   def tkeventToMouseButtonName(event):
      if event.num == 1:
         return 'Left'
      elif event.num == 2:
         return 'Right'
      elif event.num == 3:
         return 'Middle'

   def tkeventToJavascriptKeycode(event):...


if as3state.platform == 'Linux':
   mouseButtonNameToTkNumber = Linux.mouseButtonNameToTkNumber
   mouseButtonNameToTkname = Linux.mouseButtonNameToTkname
   tkeventToMouseButtonName = Linux.tkeventToMouseButtonName
   tkeventToJavascriptKeycode = Linux.tkeventToJavascriptKeycode
elif as3state.platform == 'Windows':
   mouseButtonNameToTkNumber = Windows.mouseButtonNameToTkNumber
   mouseButtonNameToTkname = Windows.mouseButtonNameToTkname
   tkeventToMouseButtonName = Windows.tkeventToMouseButtonName
   tkeventToJavascriptKeycode = Windows.tkeventToJavascriptKeycode
elif as3state.platform == 'Darwin':
   mouseButtonNameToTkNumber = Darwin.mouseButtonNameToTkNumber
   mouseButtonNameToTkname = Darwin.mouseButtonNameToTkname
   tkeventToMouseButtonName = Darwin.tkeventToMouseButtonName
   tkeventToJavascriptKeycode = Darwin.tkeventToJavascriptKeycode
