# -*- coding: utf-8 -*-

__all__ = ['BaseArgsParser']

import argparse


class BaseArgsParser(argparse.ArgumentParser):
    """An argument parser accepting the common options to pyglet-based
    visualizations.
    """

    def __init__(self):

        super(BaseArgsParser, self).__init__()

        self.add_argument(
                '-F', '--fps', '--frame-rate',
                help='number of particle animation frames to play per second',
                type=float, default=3.0)


class SlicedGridArgsParser(BaseArgsParser):
    """An argument parser for things that display cubical grids that may be
    sliced.
    """

    def __init__(self):

        super(SlicedGridArgsParser, self).__init__()

        self.add_argument(
                '-s', '--slice',
                help=''.join([
                    'slice of ', self.object_sliced(), 'to display; described',
                    ' by enclosed cube index ranges along all the axes']),
                nargs=6, type=int,
                default=(None, ) * 6)

    def object_sliced(self):
        """SGAP.object_sliced() -> string

        Name of the object being sliced.
        """

        raise NotImplementedError(self.__class__.__name__, self.object_sliced.__name__)
