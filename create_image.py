# encoding: utf-8

from clingon import clingon
clingon.DEBUG = True

from docker_integration import PlatformManager
from fabric_integration import FabricManager


@clingon.clize
def factory(
        image,
        platform,
        command,
):
    images = {'host': image}
    platform_obj = PlatformManager(platform, images)
    platform_obj.setup()
    fabric = FabricManager(platform_obj)
    fabric.set_platform().execute(command)
    platform_obj.commit_containers()
