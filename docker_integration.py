# encoding: utf-8

from collections import Mapping
import os

import docker_wrapper

ROOTDIR = os.path.dirname(os.path.abspath(__file__))


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
        self.containers = {k: '_'.join((v, self.platform, k)) for k, v in self.images.iteritems()}
        self.hosts = self.images.keys()
        self.images_names = set(self.images.values())

    def setup(self, reset_containers=False, reset_images=False):
        """
        1- ensures images are created, otherwise, creates them
        2- ensures containers are created and started otherwise creates and/or starts them
        :param reset_containers: if True, containers are deleted before processing
        :param reset_images: if True, images are deleted before processing
        """
        if reset_containers:
            self.containers_stop()
            self.containers_delete()
        if reset_images:
            self.images_delete()
        self.build_images()
        self.run_containers()
        return self

    def build_images(self):
        existing = docker_wrapper.get_images(self.images_names)
        for image in self.images_names:
            if image not in existing:
                docker_wrapper.docker_build(os.path.join(ROOTDIR, 'images'), image, image)
        return self

    def run_containers(self):
        running = docker_wrapper.get_containers(self.containers)
        existing = docker_wrapper.get_containers(self.containers, True)
        for k, v in self.images.iteritems():
            container = self.containers[k]
            if container in running:
                continue
            if container in existing:
                docker_wrapper.docker_start(container)
            else:
                docker_wrapper.docker_run(v, container, container, self.parameters.get(k))
        return self

    def images_delete(self):
        docker_wrapper.images_delete(self.images_names)
        return self

    def containers_stop(self):
        print("STOP " + ' '.join(docker_wrapper.get_containers(self.containers.values())))
        docker_wrapper.containers_stop(docker_wrapper.get_containers(self.containers.values()))
        return self

    def containers_delete(self):
        print("DELETE " + ' '.join(docker_wrapper.get_containers(self.containers.values(), True)))
        docker_wrapper.containers_delete(docker_wrapper.get_containers(self.containers.values(), True))
        return self

    def commit_containers(self):
        """
        commited container have a convention naming: image_platform_container-name
        """
        return self

    def docker_diff(self, reference):
        """
        check docker diff against an external reference
        :param reference: string, a reference text to be checked
        """
