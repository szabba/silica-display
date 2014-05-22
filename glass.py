# -*- coding: utf-8 -*-

__all__ = ['Glass']


class Glass(object):
    """The glass (or it's visible part)"""

    def __init__(self, config, cam):

        self.__config = config
        self.__cam = cam
