#!/usr/bin/env python2

import math


FILENAME = 'rollers.sim'

FRAMES_PER_PERIOD, PARTICLES = 10, 7
FRAMES = FRAMES_PER_PERIOD * PARTICLES

INIT_ALPHA_BASE = 2 * math.pi / PARTICLES
ALPHA_PER_FRAME = INIT_ALPHA_BASE / FRAMES_PER_PERIOD

INIT_RHO_BASE = math.pi / 2
RHO_PER_FRAME = 2 * math.pi / FRAMES

THETA_PER_FRAME = 2 * math.pi / FRAMES

RADIUS = 10


class Particle(object):
    """A 'simulated' particle"""

    def __init__(self, no):

        self.__no = no
        self.__step = 0
        self.__alpha = INIT_ALPHA_BASE * no

    def step(self):
        """P.step()

        Forward the internal counter.
        """

        self.__step += 1
        self.__alpha += ALPHA_PER_FRAME

    def position(self):
        """P.position() -> x, y, z"""

        x = RADIUS * math.cos(self.__alpha)
        y = RADIUS * math.sin(self.__alpha)
        z = 0

        return x, y, z

    def orientation(self):
        """P.orientation() -> m_x, m_y, m_z"""

        rho = INIT_RHO_BASE +  RHO_PER_FRAME * (self.__no + self.__step)
        theta = THETA_PER_FRAME * self.__step

        m_x = math.cos(rho) * math.cos(theta)
        m_y = math.sin(rho) * math.cos(theta)
        m_z = math.sin(theta)

        return m_x, m_y, m_z


if __name__ == '__main__':

    particles = [Particle(i) for i in range(PARTICLES)]

    with open(FILENAME, 'w') as output_file:

        output_file.write('%d\n' % PARTICLES)

        for __ in range(FRAMES):
            for particle in particles:

                output_file.write('%f %f %f ' % particle.position())
                output_file.write('%f %f %f' % particle.orientation())
                output_file.write('\n')

                particle.step()
