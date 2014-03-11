# -*- coding: utf-8 -*-

__all__ = ['numpy_to_c']


def numpy_to_c(array, t):
    """numpy_to_c(array, t) -> ctypes array

    `t` is the ctypes type of the arrays elements. The array is flattened.
    """

    return (array.size * t)(*array.flat)
