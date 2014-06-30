# -*- coding: utf-8 -*-

__all__ = ['Fog']


class Fog(object):
    """Semi-transparent fog approximating ambient occlusion in the glass."""

    def __init__(self, config, cam):

        self.__config = config
        self.__cam = cam
