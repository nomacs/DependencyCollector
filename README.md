# DependencyCollector
Searches the dependencies (dlls) needed for an executable or library and copies it to the correct directory. This is done recursively, so all dependencies of a library needed are also copied.

## Usage
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
create_release = True
mapping_debug = Debug
create_debug = True
mapping_relwithdebinfo = Debug
create_relwithdebinfo = True
mapping_minsizerel = Release
create_minsizerel = True
paths_release = C:/Program Files (x86)/Microsoft Visual Studio 14.0/Common7/IDE/Remote Debugger/x64;
paths_debug = C:/Program Files (x86)/Microsoft Visual Studio 14.0/Common7/IDE/Remote Debugger/x64;
blacklist = KERNEL32.dll;VERSION.dll;OpenCL.dll;opengl32.dll;GDI32.dll;USER32.dll;SHELL32.dll;ole32.dll;ADVAPI32.dll;WS2_32.dll;MPR.dll;
```
* mapping_[configuration] must be Release or Debug. Specifies if the paths_release or paths_debug should be used for searching the dependencies-
* create_[configuration] must be True or False. If True the inputfile (and its dependencies) is scanned recursively and the corresponding dll files are copied into the directory of the input files. If False all *.dll files in the directory of the inputfile are searched in the paths for a newer version. If a newer version have been found, it is copied to the directory of the input file. After 'create' has been executed the create flag of the specified release is changed to 'False'
* paths_[debug|release] specifies the paths which are used for finding the dependencies
* blacklist specifies a list of libraries which should not be searched

Minimal usage:
Copy DependencyCollector.py and config.ini into a directory and adapt the paths_release in the config file. Execute the script with --infile and all dependencies found are copied into the directory of the infile

## Usage with CMake
This script is also designed to be used in a cmake build environment. For a working example see [nomacs - ImageLounge](http://github.com/nomacs/nomacs)
Copy DependencyCollector.py and DependencyCollector.config.cmake.in into your directory and in your cmake file use something like
```
set(DC_SCRIPT ${CMAKE_CURRENT_SOURCE_DIR}/cmake/DependencyCollector.py)
set(DC_CONFIG ${CMAKE_BINARY_DIR}/DependencyCollector.ini)

SET(DC_PATHS_RELEASE ${EXIV2_BUILD_PATH}/ReleaseDLL ${LIBRAW_BUILD_PATH}/Release ${OpenCV_DIR}/bin/Release ${QT_QMAKE_PATH})
SET(DC_PATHS_DEBUG ${EXIV2_BUILD_PATH}/DebugDLL ${LIBRAW_BUILD_PATH}/Debug ${OpenCV_DIR}/bin/Debug ${QT_QMAKE_PATH})

configure_file(${NOMACS_SOURCE_DIR}/cmake/DependencyCollector.config.cmake.in ${DC_CONFIG})

add_custom_command(TARGET ${PROJECT_NAME} POST_BUILD COMMAND ${DC_SCRIPT} --infile $<TARGET_FILE:${PROJECT_NAME}> --configfile ${DC_CONFIG} --configuration $<CONFIGURATION>)
```
This will add the build paths of your libaries needed into the config file and add a post build command that the script will be executed after every successful build. Since cmake resets the CREATE_[CONFIGURATION] variables to True every time it is run new dependencies are copied after the first post build command. Otherwise the update method will be used since it is much faster
