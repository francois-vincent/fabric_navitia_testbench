# encoding: utf-8

from contextlib import contextmanager
import os
import subprocess

ROOTDIR = os.path.dirname(os.path.abspath(__file__))


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


@contextmanager
def cd(folder):
    old_folder = os.getcwd()
    try:
        yield os.chdir(folder)
    finally:
        os.chdir(old_folder)


def extract_column(text, column, start=0):
    values = []
    lines = text.splitlines()[start:]
    for line in lines:
        elts = line.split()
        if elts and column < len(elts):
            values.append(elts[column])
    return values


class Command(object):
    """ Use this class if you want to wait and get shell command output
    """
    def __init__(self, cmd):
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.stdout = p.stdout.read()
        self.stderr = p.stderr.read()
        self.returncode = p.returncode

    def stdout_column(self, column, start=0):
        return extract_column(self.stdout, column, start)


def command(cmd):
    """ Use this function if you only want the return code
    """
    return subprocess.call(cmd, shell=True)


def ssh(user, host, cmd):
    with cd(os.path.join(ROOTDIR)):
        return Command('ssh -i images/keys/unsecure_key {user}@{host} {cmd}'.format(**locals())).stdout.strip()


def put(source, dest, user, host):
    """ source and dest must be absolute paths
    """
    with cd(os.path.join(ROOTDIR)):
        command(('scp -i images/keys/unsecure_key {source} {user}@{host}:{dest}'.format(**locals())))
