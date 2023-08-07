import math
import numpy as np


class Projection:
    def __init__(self, render):
        self.render = render

    def update_matrix(self):
        self.render.camera.v_fov = (
            self.render.camera.h_fov * self.render.height / self.render.width
        )
        self.render.camera.cos_fov = math.cos(
            math.sqrt(2)
            * max(self.render.camera.h_fov / 2, self.render.camera.v_fov / 2)
        )
        self.render.camera.d_cos_fov = math.cos(
            math.sqrt(2) * max(self.render.camera.h_fov, self.render.camera.v_fov)
        )

        self.matrix = self.projection_matrix() @ self.to_screen_matrix()
        self.render.m = self.render.camera.matrix @ self.matrix

    def projection_matrix(self):
        NEAR = self.render.camera.near_plane
        FAR = self.render.camera.far_plane
        RIGHT = math.tan(self.render.camera.h_fov / 2)
        TOP = math.tan(self.render.camera.v_fov / 2)
        return np.array(
            [
                [1 / RIGHT, 0, 0, 0],
                [0, 1 / TOP, 0, 0],
                [0, 0, (FAR + NEAR) / (FAR - NEAR), 1],
                [0, 0, -2 * FAR * NEAR / (FAR - NEAR), 0],
            ]
        )

    def to_screen_matrix(self):
        HW, HH = self.render.half_width, self.render.half_height
        return np.array([[HW, 0, 0, 0], [0, -HH, 0, 0], [0, 0, 1, 0], [HW, HH, 0, 1]])
