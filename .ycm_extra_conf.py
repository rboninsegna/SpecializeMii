import os
import logging
import ycm_core

if not 'DEVKITARM' in os.environ:
    logging.info("Please set $DEVKITARM in your environment.")

flags = [
    '-x',
    'c',
    '-g',

    '-fomit-frame-pointer',
    '-ffunction-sections',

    '-Wall',
    '-Wextra',

    '--sysroot=' + os.path.expandvars('${DEVKITARM}/arm-none-eabi'),
    '-I', os.path.expandvars('${DEVKITARM}/arm-none-eabi/include'),
    '-I', os.path.expandvars('${DEVKITPRO}/libctru/include'),
    '-I', os.path.expandvars('${DEVKITPRO}/portlibs/armv6k/include'),
    '-I', os.path.expandvars('${DEVKITPRO}/portlibs/3ds/include'),

    '-DARM11',
    '-D_3DS',

    '-DAPPLICATION_NAME=""',
    '-DAPPLICATION_REV=""',
    '-DVERSION_MAJOR=0',
    '-DVERSION_MINOR=0',
    '-DVERSION_PATCH=0',
]

source_dir = 'src'


# Set this to the absolute path to the folder (NOT the file!) containing the
# compile_commands.json file to use that instead of 'flags'. See here for
# more details: http://clang.llvm.org/docs/JSONCompilationDatabase.html
#
# You can get CMake to generate this file for you by adding:
#   set( CMAKE_EXPORT_COMPILE_COMMANDS 1 )
# to your CMakeLists.txt file.
#
# Most projects will NOT need to set this to anything; you can just change the
# 'flags' list of compilation flags. Notice that YCM itself uses that approach.
compilation_database_folder = ''

if os.path.exists( compilation_database_folder ):
  database = ycm_core.CompilationDatabase( compilation_database_folder )
else:
  database = None

SOURCE_EXTENSIONS = [ '.cpp', '.cxx', '.cc', '.c', '.m', '.mm' ]

def DirectoryOfThisScript():
  return os.path.dirname( os.path.abspath( __file__ ) )


def MakeRelativePathsInFlagsAbsolute( flags, working_directory ):
  if not working_directory:
    return list( flags )
  new_flags = []
  make_next_absolute = False
  path_flags = [ '-isystem', '-I', '-iquote', '--sysroot=' ]
  for flag in flags:
    new_flag = flag

    if make_next_absolute:
      make_next_absolute = False
      if not flag.startswith( '/' ):
        new_flag = os.path.join( working_directory, flag )

    for path_flag in path_flags:
      if flag == path_flag:
        make_next_absolute = True
        break

      if flag.startswith( path_flag ):
        path = flag[ len( path_flag ): ]
        new_flag = path_flag + os.path.join( working_directory, path )
        break

    if new_flag:
      new_flags.append( new_flag )
  return new_flags


def IsHeaderFile( filename ):
  extension = os.path.splitext( filename )[ 1 ]
  return extension in [ '.h', '.hxx', '.hpp', '.hh' ]


def GetCompilationInfoForFile( filename ):
  # The compilation_commands.json file generated by CMake does not have entries
  # for header files. So we do our best by asking the db for flags for a
  # corresponding source file, if any. If one exists, the flags for that file
  # should be good enough.
  if IsHeaderFile( filename ):
    basename = os.path.splitext( os.path.basename( filename ) )[ 0 ]
    for extension in SOURCE_EXTENSIONS:
      replacement_file = DirectoryOfThisScript() + '/' + source_dir + '/' + basename + extension
      if os.path.exists( replacement_file ):
        logging.info("Replacement is " + replacement_file)
        compilation_info = database.GetCompilationInfoForFile(
          replacement_file )
        if compilation_info.compiler_flags_:
          logging.info("Found compiler flags.")
          return compilation_info
    return None
  return database.GetCompilationInfoForFile( filename )


def FlagsForFile( filename, **kwargs ):
  if database:
    # Bear in mind that compilation_info.compiler_flags_ does NOT return a
    # python list, but a "list-like" StringVec object
    logging.info("Loaded database from " + compilation_database_folder)
    compilation_info = GetCompilationInfoForFile( filename )
    if not compilation_info:
      return None

    final_flags = MakeRelativePathsInFlagsAbsolute(
      compilation_info.compiler_flags_,
      compilation_info.compiler_working_dir_ )

  else:
    logging.info("Getting flags")
    relative_to = DirectoryOfThisScript()
    final_flags = MakeRelativePathsInFlagsAbsolute( flags, relative_to )

  logging.info(final_flags)
  return {
    'flags': final_flags,
    'do_cache': True
  }

