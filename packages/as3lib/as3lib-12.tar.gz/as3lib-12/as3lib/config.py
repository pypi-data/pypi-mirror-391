from as3lib import as3state
from as3lib.as3state import __version__
from io import StringIO
from pathlib import Path
try:
   import tomllib
except Exception:
   import tomli as tomllib
from as3lib._toplevel.Errors import Error


class TOML:
   '''
   A simple TOML writer for as3lib. This class was created out of frustration
   at tomli_w's formatting (mostly the arrays) and only implements things needed
   for this library. It is not guaranteed to work for your use case.
   '''
   def Value(value):
      if isinstance(value, str):
         return f'"{value}"'
      if isinstance(value, bool):
         return 'true' if value else 'false'
      if isinstance(value, (list, tuple)):
         return TOML.Array(value)
      if isinstance(value, dict):
         return TOML.Table(value)
      return f'{value}'

   def Table(value):
      with StringIO() as text:
         text.write('{')
         for k, v in value.items():
            text.write(f'{k} = {TOML.Value(v)},')
         temp = text.getvalue()
         if temp.endswith(','):  # TODO: Make this better
            return temp[:-1] + '}'
         return temp + '}'

   def Array(value):
      with StringIO() as text:
         text.write('[')
         for i in value:
            text.write(f'{TOML.Value(i)},')
         text.write(']')
         return text.getvalue()

   def Return(valDict):
      nontables = []
      tables = []
      for k, v in valDict.items():
         if isinstance(v, dict):
            tables.append(k)
         else:
            nontables.append(k)
      with StringIO() as text:
         for k in nontables:
            text.write(f'{k} = {TOML.Value(valDict[k])}\n')
         for k in tables:
            text.write('\n')  # This doesn't work when combined with next line for some reason
            text.write(f'["{k}"]\n' if str(k).find('.') != -1 else f'[{k}]\n')
            for k2, v2 in valDict[k].items():
               text.write(f'{k2} = {TOML.Value(v2)}\n')
         return text.getvalue()

   def write(file, valDict, mode='w'):
      with open(file, mode) as f:
         f.write(TOML.Return(valDict))

   def readFile(file):
      return tomllib.load(file)

   def readString(string):
      return tomllib.loads(string)


def _dependencyCheck(cfgval):
   if cfgval:
      return True
   from importlib.util import find_spec
   from subprocess import check_output
   hasDeps = True
   if as3state.platform == 'Linux':
      # Running on Wayland is done through XWayland so these are needed there too
      if check_output(('which', 'xwininfo')).decode('utf-8').startswith('which: no'):
         as3state.initerror.append((3, 'Linux: requirement "xwininfo" not found'))
         hasDeps = False
      if check_output(('which', 'xrandr')).decode('utf-8').startswith('which: no'):
         as3state.initerror.append((3, 'Linux: requirement "xrandr" not found'))
         hasDeps = False
   elif as3state.platform == 'Windows':...
   elif as3state.platform == 'Darwin':...
   if find_spec('numpy') is None:  # https://pypi.org/project/numpy
      as3state.initerror.append((3, 'Python: requirement "numpy" not found'))
      hasDeps = False
   if find_spec('PIL') is None:  # https://pypi.org/project/Pillow
      as3state.initerror.append((3, 'Python: requirement "Pillow" not found'))
      hasDeps = False
   if find_spec('tkhtmlview') is None:  # https://pypi.org/project/tkhtmlview
      as3state.initerror.append((3, 'Python: requirement "tkhtmlview" not found'))
      hasDeps = False
   if find_spec('miniamf') is None:
      as3state.initerror.append((3, 'Python: requirement "Mini-AMF" or "as3lib-miniAMF" not found'))
      hasDeps = False
   if find_spec('tomllib') is None and find_spec('tomli') is None:
      as3state.initerror.append((3, 'Python: requirement "tomllib" or "tomli" not found'))
      hasDeps = False
   return hasDeps


def Load():
   if as3state._cfg is not None:
      raise Error('Config has already been loaded')
   # Load config from files
   configpath = as3state.librarydirectory / 'as3lib.toml'
   modified = False
   if configpath.exists():
      with configpath.open('rb') as f:
         temp = tomllib.load(f)
      as3state._cfg = temp
      tempmm = temp.get('mm.cfg', {})
      tempdis = temp.get('display', {})
      cfg = {
         'version': int(temp.get('version', __version__)),
         'migrateOldConfig': bool(temp.get('migrateOldConfig', False)),
         'dependenciesPassed': bool(temp.get('dependenciesPassed', False)),
         'addedFeatures': bool(temp.get('addedFeatures', False)),
         'flashVersion': tuple(temp.get('flashVersion', (32, 0, 0, 371))),
         'mm.cfg': {
            'ErrorReportingEnable': bool(tempmm.get('ErrorReportingEnable', False)),
            'MaxWarnings': int(tempmm.get('MaxWarnings', 100)),
            'TraceOutputFileEnable': bool(tempmm.get('TraceOutputFileEnable', False)),
            'TraceOutputFileName': str(tempmm.get('TraceOutputFileName', '')),
            'ClearLogsOnStartup': bool(tempmm.get('ClearLogsOnStartup', True)),
            'NoClearWarningNumber': int(tempmm.get('NoClearWarningNumber', 0))
         },
         'display': {
            'screenwidth': int(tempdis.get('screenwidth', 0)),
            'screenheight': int(tempdis.get('screenheight', 0)),
            'refreshrate': float(tempdis.get('refreshrate', 0)),
            'colordepth': int(tempdis.get('colordepth', 0))
         }
      }
   else:
      cfg = {
         'version': __version__,
         'migrateOldConfig': True,
         'dependenciesPassed': False,
         'addedFeatures': False,
         'flashVersion': (32, 0, 0, 371),  # I chose this version because it was the last version of flash before adobe's timebomb
         'mm.cfg': {
            'ErrorReportingEnable': False,
            'MaxWarnings': 100,
            'TraceOutputFileEnable': False,
            'TraceOutputFileName': '',
            'ClearLogsOnStartup': True,
            'NoClearWarningNumber': 0
         },
         'display': {
            'screenwidth': 0,
            'screenheight': 0,
            'refreshrate': 0,
            'colordepth': 0
         }
      }
      modified = True
   if cfg['migrateOldConfig']:
      from configparser import ConfigParser, UNNAMED_SECTION
      modified = True
      mmcfgpath = as3state.librarydirectory / 'mm.cfg'
      wlcfgpath = as3state.librarydirectory / 'wayland.cfg'
      oldcfgpath = as3state.librarydirectory / 'as3lib.cfg'
      if mmcfgpath.exists():
         mmcfg = ConfigParser(allow_unnamed_section=True)
         with open(mmcfgpath, 'r') as f:
            mmcfg.read_file(f)
         cfg['mm.cfg'] = {
            'ErrorReportingEnable': True if mmcfg.getint(UNNAMED_SECTION, 'ErrorReportingEnable', fallback=0) == 1 else False,
            'MaxWarnings': mmcfg.getint(UNNAMED_SECTION, 'MaxWarnings', fallback=100),
            'TraceOutputFileEnable': True if mmcfg.getboolean(UNNAMED_SECTION, 'TraceOutputFileEnable', fallback=0) == 1 else False,
            'TraceOutputFileName': mmcfg.get(UNNAMED_SECTION, 'TraceOutputFileName', fallback=''),
            'ClearLogsOnStartup': True,
            'NoClearWarningNumber': 0
         }
         del mmcfg
      if wlcfgpath.exists():
         wlcfg = ConfigParser()
         with open(wlcfgpath, 'r') as f:
            wlcfg.read_file(f)
         cfg['display'] = {
            'screenwidth': wlcfg.getint('Screen', 'screenwidth', fallback=0),
            'screenheight': wlcfg.getint('Screen', 'screenheight', fallback=0),
            'refreshrate': wlcfg.getfloat('Screen', 'refreshrate', fallback=0),
            'colordepth': wlcfg.getint('Screen', 'colordepth', fallback=0)
         }
         wlcfgpath.unlink(missing_ok=True)
         del wlcfg
      if oldcfgpath.exists():
         oldcfg = ConfigParser()
         with open(oldcfgpath, 'r') as f:
            oldcfg.read_file(f)
         cfg = {
            'version': __version__,
            'migrateOldConfig': False,
            'dependenciesPassed': False,
            'addedFeatures': False,
            'flashVersion': (32, 0, 0, 371),
            'mm.cfg': {
               'ErrorReportingEnable': oldcfg.getboolean('mm.cfg', 'ErrorReportingEnable', fallback=False),
               'MaxWarnings': 100,  # Reset value because I messed up the type
               'TraceOutputFileEnable': oldcfg.getboolean('mm.cfg', 'TraceOutputFileEnable', fallback=False),
               'TraceOutputFileName': oldcfg.get('mm.cfg', 'TraceOutputFileName', fallback=''),
               'ClearLogsOnStartup': True if oldcfg.getint('mm.cfg', 'ClearLogsOnStartup', fallback=1) == 1 else False,
               'NoClearWarningNumber': oldcfg.getint('mm.cfg', 'NoClearWarningNumber', fallback=0)
            },
            'display': {
               'screenwidth': oldcfg.getint('wayland', 'screenwidth', fallback=0),
               'screenheight': oldcfg.getint('wayland', 'screenheight', fallback=0),
               'refreshrate': oldcfg.getfloat('wayland', 'refreshrate', fallback=0),
               'colordepth': oldcfg.getint('wayland', 'colordepth', fallback=0)
            }
         }
         oldcfgpath.unlink(missing_ok=True)
      cfg['mm.cfg']['TraceOutputFileName'] = cfg['mm.cfg']['TraceOutputFileName'].strip('\'"')  # Sometimes the value's quotes are left in the string
      cfg['migrateOldConfig'] = False
   # Load some values into global state
   as3state.addedFeatures = cfg['addedFeatures']
   as3state.hasDependencies = _dependencyCheck(cfg['dependenciesPassed'] and cfg['version'] == __version__)
   as3state.flashVersion = cfg['flashVersion']
   as3state.ErrorReportingEnable = cfg['mm.cfg']['ErrorReportingEnable']
   as3state.MaxWarnings = cfg['mm.cfg']['MaxWarnings']
   as3state.TraceOutputFileEnable = cfg['mm.cfg']['TraceOutputFileEnable']
   tempTraceOutputFileName = cfg['mm.cfg']['TraceOutputFileName']
   as3state.ClearLogsOnStartup = cfg['mm.cfg']['ClearLogsOnStartup']
   if not as3state.ClearLogsOnStartup:
      as3state.CurrentWarnings = cfg['mm.cfg']['NoClearWarningNumber']
      if as3state.MaxWarnings != 0 and as3state.CurrentWarnings >= as3state.MaxWarnings:
         as3state.MaxWarningsReached = True
   if tempTraceOutputFileName == '' or Path(tempTraceOutputFileName).is_dir():
      print('as3lib: Using defualt TraceOutputFileName')
      tempTraceOutputFileName = as3state.librarydirectory / 'flashlog.txt'
   as3state.TraceOutputFileName = Path(tempTraceOutputFileName)
   tmpd = cfg['display']
   if tmpd['screenwidth']:
      as3state.width = tmpd['screenwidth']
   if tmpd['screenheight']:
      as3state.height = tmpd['screenheight']
   if tmpd['refreshrate']:
      as3state.refreshrate = tmpd['refreshrate']
   if tmpd['colordepth']:
      as3state.colordepth = tmpd['colordepth']
   Save(modified)


def Save(saveAnyways: bool = False):
   tempcfg = {
      'version': __version__,
      'migrateOldConfig': False,
      'dependenciesPassed': as3state.hasDependencies,
      'addedFeatures': as3state.addedFeatures,
      'flashVersion': as3state.flashVersion,
      'mm.cfg': {
         'ErrorReportingEnable': as3state.ErrorReportingEnable,
         'MaxWarnings': as3state.MaxWarnings,
         'TraceOutputFileEnable': as3state.TraceOutputFileEnable,
         'TraceOutputFileName': str(as3state.TraceOutputFileName),
         'ClearLogsOnStartup': as3state.ClearLogsOnStartup,
         'NoClearWarningNumber': 0 if as3state.ClearLogsOnStartup else as3state.CurrentWarnings
      },
      'display': {
         'screenwidth': as3state.width,
         'screenheight': as3state.height,
         'refreshrate': as3state.refreshrate,
         'colordepth': as3state.colordepth
      }
   }
   if saveAnyways or as3state._cfg != tempcfg:
      TOML.write(as3state.librarydirectory / 'as3lib.toml', tempcfg)
      as3state._cfg = tempcfg
