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
        """Open a document through Windows and request a visible application window."""
        try:
            self.opener(str(path), "open", show_cmd=5)
        except TypeError:
            # Test doubles and non-Windows-compatible openers may expose only
            # the traditional one-argument contract.
            self.opener(str(path))
