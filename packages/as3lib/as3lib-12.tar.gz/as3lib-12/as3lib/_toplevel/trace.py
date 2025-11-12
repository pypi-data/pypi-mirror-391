from as3lib import as3state


def _traceFileOutput(output):
   if as3state.TraceOutputFileName.exists() and as3state.TraceOutputFileName.is_file():
      with open(as3state.TraceOutputFileName, 'a') as f:
         f.write(output + '\n')
   else:
      with open(as3state.TraceOutputFileName, 'w') as f:
         f.write(output + '\n')


def trace(*args):
   if as3state.as3DebugEnable:
      output = ' '.join((str(i) for i in args))
      print(output)
      if as3state.TraceOutputFileEnable:
         _traceFileOutput(output)


def errorTrace(*args):
   output = ' '.join(str(i) for i in args)
   print(output)
   if as3state.as3DebugEnable and as3state.ErrorReportingEnable and not as3state.MaxWarningsReached:
      if as3state.CurrentWarnings < as3state.MaxWarnings or as3state.MaxWarnings == 0:
         as3state.CurrentWarnings += 1
      else:
         output = 'Maximum number of errors has been reached. All further errors will be suppressed.'
         as3state.MaxWarningsReached = True
      _traceFileOutput(output)
