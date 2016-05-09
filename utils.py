# encoding: utf-8

from contextlib import contextmanager
import os.path
import re
import subprocess

ROOTDIR = os.path.dirname(os.path.abspath(__file__))


# ======================= GENERAL UTILILITIES =======================

def extract_column(text, column, start=0, sep=None):
    """ Extracts columns from a formatted text
    :param text:
    :param column: the column number: from 0, -1 = last column
    :param start: the line number to start with (headers removal)
    :param sep: optional separator between words  (default is arbitrary number of blanks)
    :return: a list of words
    """
    lines = text.splitlines() if isinstance(text, basestring) else text
    if start:
        lines = lines[start:]
    values = []
    for line in lines:
        elts = line.split(sep) if sep else line.split()
        if elts and column < len(elts):
            values.append(elts[column].strip())
    return values


def filter_column(text, column, sep=None, **kwargs):
    """ Filters (like grep) lines of text according to a specified column and operator/value
    :param text: a string
    :param column: integer >=0
    :param sep: optional separator between words  (default is arbitrary number of blanks)
    :param kwargs: operator=value eg eq='exact match', contains='substring', startswith='prefix' etc...
    :return:
    """
    if len(kwargs) != 1:
        raise TypeError("Missing or too many keyword parameter in filter_column")
    op, value = kwargs.items()[0]
    if op in ('eq', 'equals'):
        op = '__eq__'
    elif op in ('contains', 'includes'):
        op = '__contains__'
    elif not op in ('startswith', 'endswith'):
        raise ValueError("Unknown filter_column operator: {}".format(op))
    if isinstance(text, basestring):
        text = text.splitlines()
    values = []
    for line in text:
        elts = line.split(sep) if sep else line.split()
        if elts and column < len(elts):
            elt = elts[column]
            if getattr(elt, op)(value):
                values.append(line.strip())
    return values


# ======================= OS RELATED UTILITIES =======================

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


class Command(object):
    """ Use this class if you want to wait and get shell command output
    """
    def __init__(self, cmd):
        self.p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.p.wait()
        self.returncode = self.p.returncode

    @property
    def stdout(self):
        return self.p.stdout.read()

    @property
    def stderr(self):
        return self.p.stderr.read()

    def stdout_column(self, column, start=0):
        return extract_column(self.stdout, column, start)


def command(cmd):
    """ Use this function if you only want the return code
        you can't retrieve stdout nor stdin
    """
    return subprocess.call(cmd, shell=True)


def ssh(user, host, cmd):
    with cd(ROOTDIR):
        return Command('ssh -o StrictHostKeyChecking=no -i images/keys/unsecure_key '
                       '{user}@{host} {cmd}'.format(**locals())).stdout.strip()


def scp(source, dest, host, user):
    """ source and dest must be absolute paths
    """
    with cd(ROOTDIR):
        command('scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -i images/keys/unsecure_key '
                 '{source} {user}@{host}:{dest}'.format(**locals()))


# =================== REMOTE HOSTS RELATED UTILITIES =======================

pattern = re.compile('/srv/kraken/(.+?)/kraken')


def get_running_krakens(platform, host):
    cols = extract_column(platform.ssh('ps ax | grep kraken | grep -v grep', host=host), -1)
    return [pattern.findall(col)[0] for col in cols]


def get_version(app, host):
    text = ssh('root', host, 'apt-cache policy {}'.format(app))
    try:
        return extract_column(filter_column(text, 0, startswith='Install'), 1, sep=':')[0]
    except IndexError:
        return None


def python_requirements_compare(freeze, requirements):
    missing = []
    fre_lines = freeze.strip().splitlines()
    req_lines = requirements.strip().splitlines()
    for req in req_lines:
        if '==' in req and req not in fre_lines:
            missing.append(req)
    return missing
