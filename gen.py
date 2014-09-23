#!/usr/bin/env python

from __future__  import print_function

import math
import random

print("500")
for i in range(500):

    x = random.uniform(0.0, 50.0)
    y = random.uniform(0.0, 50.0)
    z = random.uniform(50.0, 100.0)

    o_x, o_y, o_z = random.uniform(-1., 1.), random.uniform(-1., 1.), random.uniform(-1., 1.)

    o_len = math.sqrt(o_x**2 + o_y**2 + o_z**2)

    print("{} {} {} {} {} {}".format(x, y, z, o_x / o_len, o_y / o_len, o_z / o_len))
