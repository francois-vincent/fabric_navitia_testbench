
integration tests project for https://github.com/CanalTP/fabric_navitia

How to launch:
- cd fabric_navitia_tests
- copy navitia packages here
- launch a test set, e.g.
    PYTHONPATH=path/to/fabric_navitia py.test -s test_single/test_kraken.py [--reset] [--dev]
