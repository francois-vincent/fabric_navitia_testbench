# encoding: utf-8

from definitions import PlatformManager, FabricManager


class TestBaseScenario:

    def test_debian8_simple(self):
        platform = PlatformManager('simple', 'debian8')
        platform.setup(True)
        fabric = FabricManager('simple')
        fabric.execute('tasks.deploy_from_scratch')
        platform.test_diff()


    def test_debian7_simple(self):
        platform = PlatformManager('simple', 'debian7')
        platform.setup(True)
