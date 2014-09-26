# -*- coding: utf-8 -*-

__all__ = ['projection', 'rotation', 'common_transforms']

import math

from silica.viz.common import transform
from silica.viz.common.constants import X_AXIS, Y_AXIS, Z_AXIS


def projection(transforms, cam_geometry, window):
    """projection(transforms, cam_geometry, window)

    Adds 'aspect' and 'project' to the transforms dict.
    """

    foreshort = transform.Foreshortening(cam_geometry)

    transforms['aspect'] = aspect = transform.AspectRatio(*window.get_size())

    flip_hand = transform.FlipHandedness(Z_AXIS)

    transforms['ah'] = ah = transform.Product()
    ah.add_factor(aspect)
    ah.add_factor(flip_hand)

    transforms['project'] = project = transform.Product()
    project.add_factor(foreshort)
    project.add_factor(ah)


def rotation(transforms, config):
    """rotation(transforms, config)

    Adds 'rot_y', 'rot_z' and 'rot' to the transforms dict.
    """

    transforms['rot_y'] = rot_y = transform.BasicAxisRotation(
            config.init_phi(), Y_AXIS)
    transforms['rot_z'] = rot_z = transform.BasicAxisRotation(
            config.init_theta(), Z_AXIS)
    rot_x = transform.BasicAxisRotation(-math.pi / 2, X_AXIS)

    transforms['rot'] = rot = transform.Product()
    rot.add_factor(rot_y)
    rot.add_factor(rot_z)
    rot.add_factor(rot_x)


def common_transforms(transforms, config, window):
    """common_transforms(transforms, config, window)

    Stores the commnon transforms in a dictionary.
    """

    cam_geometry = transform.CameraGeometry(
            *config.perspective_params())

    projection(transforms, cam_geometry, window)
    rotation(transforms, config)
