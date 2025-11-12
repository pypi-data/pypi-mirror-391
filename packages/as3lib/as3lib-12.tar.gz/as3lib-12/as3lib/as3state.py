'''
Note to self: remove all of the things that could change outside of this library
    Display stuff should not change (as defined by the actionscript documentation)
'''
__version__ = 12

platform = None  # Windows, Linux, or Darwin
displayserver = None  # linux (x11 or wayland) or darwin (x11 or native) only
librarydirectory = None  # full path to as3lib (this library)
pythonversion = None  # version of python currently running
interfaceType = None  # type of interface (Tkinter, or whatever else I decide to use)
startTime = None  # logs start time for flash.utils.getTimer

# Global config
_cfg = None  # DO NOT EDIT THIS. This is for determining if the config needs to be saved.
hasDependencies = False
addedFeatures = False  # Enables features added by this library.
flashVersion = (32, 0, 0, 371)  # This currently doesn't do anything [majorVersion,minorVersion,buildNumber,internalBuildNumber]
ErrorReportingEnable = False  # Enables logging of errors (console output seems to always be active in the debugger)
MaxWarnings = 100  # Number of warnings to log before stopping.
TraceOutputFileEnable = False  # Enables trace logging (console output is always be active in the debugger)
TraceOutputFileName = None  # Path to the log
ClearLogsOnStartup = True  # If True, clears logs on startup. This is the default behavior in flash
width = None  # Maximum width of the display window (not implemented yet)
height = None  # Maximum height of the display window (not implemented yet)
refreshrate = None  # Refresh rate of the display window (not implemented yet)
colordepth = None  # Color depth of the display window (not implemented yet)

# toplevel
as3DebugEnable = False  # State of debug mode
CurrentWarnings = 0  # Current number of warnings
MaxWarningsReached = False  # If the maximum number of warnings has been reached
defaultTraceFilePath_Flash = None  # Default file path for trace output in flash
appdatadirectory = None  # The path to the application specific data directory (must be set by the application, should not be set by other libraries)

# flash.display
windows = {}  # Dictionary containing all of the defined windows (not implemented yet)

# flash.filesystem
separator = None
userdirectory = None
desktopdirectory = None
documentsdirectory = None

# initcheck
initdone = False  # Variable to make sure this module has initialized
initerror = []  # [(errcode:int,errdesc:str),...]
