"""Single boundary for ChurchManager child processes and file opening."""

import os
import subprocess
import sys


class ProcessService:
    def __init__(self, popen=subprocess.Popen, opener=os.startfile, python_executable=None):
        self.popen = popen
        self.opener = opener
        self.python_executable = python_executable or sys.executable

    def start(self, command):
        return self.popen(list(command))

    def start_python(self, script, arguments=()):
        return self.start([self.python_executable, script, *arguments])

    def open_file(self, path):
        self.opener(str(path))

