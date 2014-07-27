# -*- coding: utf-8 -*-

__all__ = ['Transform']


class Transform(object):
    '''A linear transform of homogeneous coordinates.'''

    def __init__(self):

        self.__used_by = set()
        self.__matrix = None
        self.__gl_matrix = None
