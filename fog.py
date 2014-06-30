# -*- coding: utf-8 -*-

__all__ = ['Fog']


class Fog(object):
    """Semi-transparent fog approximating ambient occlusion in the glass."""

    def __init__(self, config, cam):

        self.__config = config
        self.__cam = cam

    def __fog_layers(self):
        """F.__fog_layers() -> list of TriangleListS

        They should all be drawn in order."""

        return []
