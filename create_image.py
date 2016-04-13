# encoding: utf-8

from clingon import clingon
clingon.DEBUG = True

from docker import PlatformManager
from fabric_integration import FabricManager


@clingon.clize
def factory(
        image,
        platform,
        command,
        reset='all'
):
    images = {'host': image}
    platform_obj = PlatformManager(platform, images)
    platform_obj.setup(reset)
    fabric = FabricManager(platform_obj)
    fabric.set_platform().execute(command)
    platform_obj.commit_containers()
