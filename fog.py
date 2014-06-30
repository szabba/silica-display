# -*- coding: utf-8 -*-

__all__ = ['Fog']


class Fog(object):
    """The glass (or it's visible part)"""

    def __init__(self, config, cam):

        self.__config = config
        self.__cam = cam
