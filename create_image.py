# encoding: utf-8

from clingon import clingon
clingon.DEBUG = True

from docker import PlatformManager
from fabric_integration import FabricManager


@clingon.clize
def factory(
        image,
        platform,
        command='no',
        hostname='host',
        reset='all'
):
    platform_obj = PlatformManager(platform, {hostname: image})
    platform_obj.setup(reset)
    fabric = FabricManager(platform_obj)
    if command != 'no':
        fabric.set_platform().execute(command)
        platform_obj.commit_containers()
