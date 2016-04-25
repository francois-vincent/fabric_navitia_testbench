# encoding: utf-8


def pytest_addoption(parser):
    parser.addoption('--dev', action='store_true',
                     help="run only non decorated tests (default: run all tests")


