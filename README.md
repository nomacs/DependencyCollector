# DependencyCollector
Searches the dependencies (dlls) needed for an executable or library and copies it to the correct directory. This is done recursively, so all dependencies of a library needed are also copied.

Usage of this script is
```
DependencyCollector.py --infile [inputfile] --configfile [configfile] --configuration [configuration]
```
additionally --debug can be specified for debug output
* inputfile: specifies the input file which dependencies should be analyzed
* configfile: specifies the configfile, for the content of the file see below (Default: config.ini)
* configuration: specifies the configuration, this is needed for a cmake build environment (default: Release)

The configfile looks like this (here 4 different configurations are used which correspond to the default configuration of cmake with MSVC (release, debug, relwithdebinfo, minsizerel))
```
[DependencyCollector]
mapping_release = Release
create_release = Create
mapping_debug = Debug
create_debug = True
mapping_relwithdebinfo = Debug
create_relwithdebinfo = True
mapping_minsizerel = Release
create_minsizerel = Create
paths_release = C:/Program Files (x86)/Microsoft Visual Studio 14.0/Common7/IDE/Remote Debugger/x64
paths_debug = C:/Program Files (x86)/Microsoft Visual Studio 14.0/Common7/IDE/Remote Debugger/x64
blacklist = KERNEL32.dll;VERSION.dll;OpenCL.dll;opengl32.dll;GDI32.dll;USER32.dll;SHELL32.dll;ole32.dll;ADVAPI32.dll;WS2_32.dll;MPR.dll;
```
* mapping_[configuration] must be Release or Debug. Specifies if the paths_release or paths_debug should be used for searching the dependencies-
* create_[configuration] must be True or False. If True the inputfile (and its dependencies) is scanned recursively and the corresponding dll files are copied into the directory of the input files. If False all *.dll files in the directory of the inputfile are searched in the paths for a newer version. If a newer version have been found, it is copied to the directory of the input file. After 'create' has been executed the create flag of the specified release is changed to 'False' 
* paths_[debug|release] specifies the paths which are used for finding the dependencies
* blacklist specifies a list of libraries which should not be searched
