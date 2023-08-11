import math
import numpy as np


def identity():
    return np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])


def translate(vec):
    tx, ty, tz = vec
    return np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [tx, ty, tz, 1]])


def rotate_x(a):
    return np.array(
        [
            [1, 0, 0, 0],
            [0, math.cos(a), math.sin(a), 0],
            [0, -math.sin(a), math.cos(a), 0],
            [0, 0, 0, 1],
        ]
    )


def rotate_y(a):
    return np.array(
        [
            [math.cos(a), 0, -math.sin(a), 0],
            [0, 1, 0, 0],
            [math.sin(a), 0, math.cos(a), 0],
            [0, 0, 0, 1],
        ]
    )


def rotate_z(a):
    return np.array(
        [
            [math.cos(a), math.sin(a), 0, 0],
            [-math.sin(a), math.cos(a), 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
        ]
    )


def scale(n):
    return np.array([[n, 0, 0, 0], [0, n, 0, 0], [0, 0, n, 0], [0, 0, 0, 1]])


def get_cos_angle_between(v1, v2):
    dot = v1[0] * v2[0] + v1[1] * v2[1] + v1[2] * v2[2]
    mags = math.hypot(*v1[:3]) * math.hypot(*v2[:3])
    return dot / mags
