# encoding: utf-8


from ..utils import extract_column


def get_running_krakens(platform, host):
    return extract_column(platform.ssh('ps aux | grep kraken | grep -v grep', host=host), -1)
