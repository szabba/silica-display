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
