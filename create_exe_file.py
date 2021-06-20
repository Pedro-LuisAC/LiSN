# A simple setup script to create an executable using PyQt5. This also
# demonstrates the method for creating a Windows executable that does not have
# an associated console.
#
# PyQt5app.py is a very simple type of PyQt5 application
#
# Run the build process by running the command 'python setup.py build'
#
# If everything works well you should find a subdirectory in the build
# subdirectory that contains the files needed to run the application

import sys
import os
from cx_Freeze import setup, Executable

base = "Win32GUI"
if sys.platform == "win32":
    base = "Win32GUI"
audio_files = os.listdir('audio_files')
audio_files_aux = []
for audio_file in audio_files:
    audio_files_aux.append("audio_files/" + audio_file)
includefiles = ["main_window.ui", "mplwidget.py", "audio_files", "unicamp_logo.svg", "editable_init_variables.txt", "generate_report.py", "report_template.html", "Reports", "template"]

#includefiles = includefiles + audio_files_aux

options = {"build_exe": {"includes": "atexit"}}

executables = [Executable("main.py", base="Win32GUI")]

setup(
    name="simple_PyQt5",
    version="0.1",
    description="Sample cx_Freeze PyQt5 script",
    #options=options,
    options={"build_exe": {"include_files": includefiles}},
    executables=executables,
)