from render.objects import *
from render.camera import *
from render.projection import *

import pygame as pg
import numpy as np
from scipy.special import ellipe
from random import random
import json


def ellipse(t, a, b, beta, t_scaler=1, t_offset=0):
    t *= t_scaler
    t -= t_offset
    t %= 1
    return (
        a * math.cos(t * 2 * math.pi) * math.cos(beta),
        b * math.sin(t * 2 * math.pi),
        a * math.cos(t * 2 * math.pi) * math.sin(beta),
    )


def ellipse_length(a, ecc):
    return 4 * a * ellipe(ecc)


def lerp(t, p1, p2):
    return t * p1 + (1 - t) * p2


def line_length(p1, p2):
    return math.hypot(*(p2 - p1))


class Render:
    def __init__(self, parent, width, height):
        self.width, self.height = width, height
        self.half_width, self.half_height = self.width // 2, self.height // 2
        self.parent = parent
        self.secs = 0
        self.create_objects()
        self.camera.update_matrix()

    def create_objects(self):
        self.camera = Camera(self, [2, 0, 100])
        self.projection = Projection(self)
        self.stationary_points = 0
        self.moving_points = 0

        self.points_table = []

        self.projection.update_matrix()
        self.points = []
        self.multilines = []

        for i in range(-6, 7):
            x_p1 = np.array([5 * i, -30, 0])
            x_p2 = np.array([5 * i, 30, 0])
            y_p1 = np.array([-30, 5 * i, 0])
            y_p2 = np.array([30, 5 * i, 0])

            self.multilines.append(
                MultiLine(
                    self,
                    f=lerp,
                    preset_args=(x_p1, x_p2),
                    segments=10,
                    colour=(200, 200, 200, 100),
                    thickness=2,
                    length=line_length(x_p1, x_p2),
                    min_segments=6,
                    max_segments=12,
                )
            )
            self.multilines.append(
                MultiLine(
                    self,
                    f=lerp,
                    preset_args=(y_p1, y_p2),
                    segments=10,
                    colour=(200, 200, 200, 100),
                    thickness=2,
                    length=line_length(y_p1, y_p2),
                    min_segments=6,
                    max_segments=12,
                )
            )

        for i in range(-5, 6):
            x_p1 = np.array([i, -5, 0])
            x_p2 = np.array([i, 5, 0])
            y_p1 = np.array([-5, i, 0])
            y_p2 = np.array([5, i, 0])

            self.multilines.append(
                MultiLine(
                    self,
                    f=lerp,
                    preset_args=(x_p1, x_p2),
                    segments=10,
                    colour=(200, 200, 200, 100),
                    thickness=2,
                    length=line_length(x_p1, x_p2),
                    min_segments=5,
                    max_segments=12,
                )
            )
            self.multilines.append(
                MultiLine(
                    self,
                    f=lerp,
                    preset_args=(y_p1, y_p2),
                    segments=10,
                    colour=(200, 200, 200, 100),
                    thickness=2,
                    length=line_length(y_p1, y_p2),
                    min_segments=5,
                    max_segments=12,
                )
            )

        with open("render/data.json", newline="") as data:
            contents = json.loads(data.read())["planets"]
            for row in contents:
                name, clr_planet, clr_orbit, a, ecc, beta, period, radius = (
                    row["name"],
                    row["planet_colour"],
                    row["orbit_colour"],
                    row["semimajor"],
                    row["eccentricity"],
                    row["beta"],
                    row["period"],
                    row["radius"],
                )

                beta *= math.pi / 180
                b = a * math.sqrt(1 - ecc**2)

                self.points.append(
                    Point(
                        self,
                        (0, 0, 0),
                        100 * radius,
                        clr_planet,
                        True,
                        ellipse,
                        (a, b, beta, 1 / (5 * period), random()),
                        name,
                    )
                )
                self.multilines.append(
                    MultiLine(
                        self,
                        ellipse,
                        (a, b, beta),
                        50,
                        clr_orbit,
                        2,
                        ellipse_length(a, ecc),
                        15,
                    )
                )

        self.segment_allowance = 3000
        # self.multilines = self.gridlines + self.orbits
        # DistributeSegments(self, self.multilines, self.segment_allowance)
        self.points_table = np.array(self.points_table)

    def update_resolution(self):
        self.parent.viewport = pg.transform.scale(self.parent.viewport, (self.width, self.height))
        self.half_width, self.half_height = self.width // 2, self.height // 2
        self.projection.update_matrix()

    def draw(self):
        for i in self.multilines[26:48]:
            i.colour.a = max(0, 2 * int(50 - math.hypot(*self.camera.position[:3])))

        self.projected_points_table = self.points_table @ self.m
        self.projected_points_table /= self.projected_points_table[:, -1].reshape(-1, 1)
        self.projected_points_table = self.projected_points_table[:, :2]

        self.cos_angle_between_table = (self.points_table - self.camera.position)[
            :, :3
        ] @ self.camera.forward[:3]
        self.cos_angle_between_table /= np.linalg.norm(self.points_table[:, :3], axis=1)

        self.camera_distance_table = np.linalg.norm(
            (self.points_table - self.camera.position)[:, :3], axis=1
        )

        projecting_objects = self.points
        drawing_objects = self.points + [i for j in self.multilines for i in j.sublines]
        drawing_objects.sort(reverse=True, key=lambda obj: obj.camera_distance())

        for i in projecting_objects:
            i.screen_projection(self.m)

        for i in drawing_objects:
            i.draw()

    def tick(self):
        self.camera.control()
        self.draw()
