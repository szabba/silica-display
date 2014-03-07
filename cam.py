# -*- coding: utf-8 -*-

__all__ = ['Cam']


import numpy


class Cam(object):
    """The camera"""

    def __init__(self, config):

        self.__config = config

        self.__matrix = numpy.eye(4)

    def matrix(self):
        """C.matric() -> camera matrix"""

        return self.__matrix
