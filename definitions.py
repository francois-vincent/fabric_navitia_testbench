# encoding: utf-8

from collections import Mapping

from fabric import api, operations, context_managers, tasks

from fabfile import tasks


class PlatformManager(object):
    """
    class in charge of bringing up a running platform and performing other docker magic
    Check existence or creates the images,
    then check existence or runs the containers.
    Optionally, stops and commits the containers.
    """
    def __init__(self, platform, images, parameters=()):
        """
        :param platform: string
        :param images: dictionary/pair iterable of container-name:image
        :param parameters: dictionary/pair iterable of container-name:iterable of strings
        """
        self.platform = platform
        self.images = images if isinstance(images, Mapping) else dict(images)
        self.parameters = parameters if isinstance(parameters, Mapping) else dict(parameters)

    def setup(self, reset=False):
        """
        1- ensures images are created, otherwise, creates them
        2- ensures containers are created and started otherwise creates and/or starts them
        :param reset: boolean, if True, images and containers are deleted before processing
        """
        if reset:
            pass

    def test_diff(self, reference):
        """
        check docker diff against an external reference
        :param reference: string, a reference text to be checked
        """

    def create_image(self, image):
        pass

    def run_container(self, container, parameters=None):
        pass

    def commit_containers(self):
        """
        commited container have a convention naming: image_platform_container-name
        """
        containers = {k: v + self.platform + k for k, v in self.images.iteritems()}

    def image_delete(self, image):
        pass

    def container_stop(self, container):
        pass

    def container_delete(self, container):
        pass


class FabricManager(object):
    """
    class in charge of running fabric_navitia tasks on a running platform
    """
    def __init__(self, platform):
        self.platform = platform

    def execute(self, cmd):
        pass
