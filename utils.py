# encoding: utf-8

from contextlib import contextmanager
import os
import subprocess


@contextmanager
def cd(folder):
    old_folder = os.getcwd()
    try:
        yield os.chdir(folder)
    finally:
        os.chdir(old_folder)


class Command(object):
    """ Use this class if you want to wait and get shell command output
    """
    def __init__(self, cmd):
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.stdout = p.stdout.read()
        self.stderr = p.stderr.read()
        self.returncode = p.returncode

    def stdout_column(self, column, start=0):
        values = []
        lines = self.stdout.split('\n')[start:]
        for line in lines:
            elts = line.split()
            if elts and column < len(elts):
                values.append(elts[column])
        return values


def command(*args):
    """ Use this function if you only want the return code
    """
    return subprocess.call(*args)


# this is a direct copy from fabric
def _wrap_with(code):

    def inner(text, bold=False):
        c = code
        if bold:
            c = "1;%s" % c
        return "\033[%sm%s\033[0m" % (c, text)
    return inner

red = _wrap_with('31')
green = _wrap_with('32')
yellow = _wrap_with('33')
blue = _wrap_with('34')
magenta = _wrap_with('35')
cyan = _wrap_with('36')
white = _wrap_with('37')
