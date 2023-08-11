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
    return np.array([
        a * math.cos(t * 2 * math.pi) * math.cos(beta),
        b * math.sin(t * 2 * math.pi),
        a * math.cos(t * 2 * math.pi) * math.sin(beta)])

def ptolemy_ellipse(t, a, b, beta, t_scaler, t_offset, anchor_a, anchor_b, anchor_beta, anchor_scaler):
    return ellipse(t, a, b, beta, t_scaler, t_offset) - ellipse(t, anchor_a, anchor_b, anchor_beta, anchor_scaler, t_offset)

def lerp(t, p1, p2):
    return t * p1 + (1 - t) * p2

def ellipse_length(a, ecc):
    return 4 * a * ellipe(ecc)




def line_length(p1, p2):
    return math.hypot(*(p2 - p1))


class Render:
    def __init__(self, parent, width, height):
        self.width, self.height = width, height
        self.half_width, self.half_height = self.width // 2, self.height // 2
        self.parent = parent
        self.speed = 0.5
        
        self.camera = Camera(self, [2, 0, 100])
        self.projection = Projection(self)
        self.create_objects()

        self.camera.update_matrix()

    def ptolemy_update(self, anchor_getter):
        self.generate_ptolemy(anchor_getter())
        self.visible = "ptolemy"

    def start_spiro(self, p_getters):
        self.spiro = True
        self.spiro_p1 = p_getters[0]()
        self.spiro_p2 = p_getters[1]()

    def create_objects(self):

        self.points = {"standard": {}, "ptolemy": {}, "both": {}}
        self.multilines = {"standard": [], "ptolemy": [], "both": []}

        self.point_tables = {"standard": np.array([[0, 0, 0, 0]]),
                             "ptolemy": np.array([[0, 0, 0, 0]]),
                             "both": np.array([[0, 0, 0, 0]])}
        self.projected_tables = {}
        self.cos_tables = {}
        self.distance_tables = {}

        self.projection.update_matrix()

        for i in range(-6, 7):
            x_p1 = np.array([5 * i, -30, 0])
            x_p2 = np.array([5 * i, 30, 0])
            y_p1 = np.array([-30, 5 * i, 0])
            y_p2 = np.array([30, 5 * i, 0])

            self.multilines["both"].append(
                MultiLine(
                    self, "both", f=lerp, preset_args=(x_p1, x_p2), segments=10, colour=(200, 200, 200, 100), thickness=2, length=line_length(x_p1, x_p2), min_segments=6, max_segments=12)
            )
            self.multilines["both"].append(
                MultiLine(
                    self, "both", f=lerp, preset_args=(y_p1, y_p2), segments=10, colour=(200, 200, 200, 100), thickness=2, length=line_length(y_p1, y_p2), min_segments=6, max_segments=12)
            )

        for i in range(-5, 6):
            x_p1 = np.array([i, -5, 0])
            x_p2 = np.array([i, 5, 0])
            y_p1 = np.array([-5, i, 0])
            y_p2 = np.array([5, i, 0])

            self.multilines["both"].append(
                MultiLine(
                    self, "both", f=lerp, preset_args=(x_p1, x_p2), segments=10, colour=(200, 200, 200, 100), thickness=2, length=line_length(x_p1, x_p2), min_segments=5, max_segments=12)
            )
            self.multilines["both"].append(
                MultiLine(
                    self, "both", f=lerp, preset_args=(y_p1, y_p2), segments=10, colour=(200, 200, 200, 100), thickness=2, length=line_length(y_p1, y_p2), min_segments=5, max_segments=12)
            )

        with open("data.json", newline="") as data:
            self.contents = json.loads(data.read())["planets"]

        for name, stats in self.contents.items():
            clr_planet, clr_orbit, a, ecc, beta, period, radius = (
                stats["planet_colour"], stats["orbit_colour"], stats["semimajor"], stats["eccentricity"], stats["beta"], stats["period"], stats["radius"])

            beta *= math.pi / 180
            b = a * math.sqrt(1 - ecc**2)

            self.points["standard"][name] = Point(self, "standard", (0, 0, 0), 100 * radius, clr_planet, True, ellipse, (a, b, beta, self.speed / period, random()), name)
            self.multilines["standard"].append(MultiLine(self, "standard", ellipse, (a, b, beta), 50, clr_orbit, 2, ellipse_length(a, ecc), 15))

        self.spiro = False
        self.visible = "standard"

        #self.segment_allowance = 3000
        # DistributeSegments(self, self.multilines, self.segment_allowance)

    def generate_ptolemy(self, planet_name):
        self.points["ptolemy"] = {}
        self.multilines["ptolemy"] = []

        anchor_a, anchor_ecc, anchor_beta, anchor_period = self.contents[planet_name]["semimajor"], self.contents[planet_name]["eccentricity"], self.contents[planet_name]["beta"], self.contents[planet_name]["period"]
        anchor_b = anchor_a * math.sqrt(1 - anchor_ecc**2)
        anchor_beta *= math.pi / 180

        for name, stats in self.contents.items():
            clr_planet, clr_orbit, a, ecc, beta, period, radius = (
                stats["planet_colour"], stats["orbit_colour"], stats["semimajor"], stats["eccentricity"], stats["beta"], stats["period"], stats["radius"])

            beta *= math.pi / 180
            b = a * math.sqrt(1 - ecc**2)

            self.points["ptolemy"][name] = Point(self, "ptolemy", (0, 0, 0), 100 * radius, clr_planet, True, ptolemy_ellipse, (a, b, beta, self.speed / period, random(), anchor_a, anchor_b, anchor_beta, self.speed / anchor_period), name)
            if name != planet_name:
                self.multilines["ptolemy"].append(MultiLine(self, "ptolemy", ptolemy_ellipse, (a, b, beta, self.speed /  period, random(), anchor_a, anchor_b, anchor_beta, self.speed / anchor_period), int(700*math.sqrt(a)), clr_orbit, 2, ellipse_length(a, ecc), 15, t_max=10*a*anchor_a))
    
    def update_resolution(self):
        self.half_width, self.half_height = self.width // 2, self.height // 2
        self.projection.update_matrix()

    def draw(self):

        for i in self.multilines["both"][26:48]:
            i.colour.a = max(0, 2 * int(50 - math.hypot(*self.camera.position[:3])))

        drawing_visible, projecting_visible = self.draw_toggle(self.visible)
        drawing_both, projecting_both = self.draw_toggle("both")

        drawing_objects = drawing_visible + drawing_both
        projecting_objects = projecting_visible + projecting_both

        drawing_objects.sort(reverse=True, key=lambda obj: obj.camera_distance())

        for i in projecting_objects:
            i.screen_projection(self.m)

        for i in drawing_objects:
            i.draw()

    def draw_toggle(self, toggle):
        self.projected_tables[toggle] = self.point_tables[toggle] @ self.m
        self.projected_tables[toggle] /= self.projected_tables[toggle][:, -1].reshape(-1, 1)
        self.projected_tables[toggle] = self.projected_tables[toggle][:, :2]

        self.cos_tables[toggle] = (self.point_tables[toggle] - self.camera.position)[:, :3] @ self.camera.forward[:3]
        self.cos_tables[toggle] /= np.linalg.norm(self.point_tables[toggle][:, :3], axis=1)

        self.distance_tables[toggle] = np.linalg.norm((self.point_tables[toggle] - self.camera.position)[:, :3], axis=1)

        return list(self.points[toggle].values()) + [i for j in self.multilines[toggle] for i in j.sublines], list(self.points[toggle].values())


    def tick(self):
        self.camera.control()
        self.draw()

        try:
            if pg.time.get_ticks() // (210 * math.sqrt(min(self.contents[self.spiro_p1]["semimajor"], self.contents[self.spiro_p2]["semimajor"])) / self.speed) != self.parent.mod and self.spiro:
                self.parent.mod = pg.time.get_ticks() // (210 * math.sqrt(min(self.contents[self.spiro_p1]["semimajor"], self.contents[self.spiro_p2]["semimajor"])) / self.speed)
                self.multilines["standard"].append(MultiLine(self, "standard", lerp, (self.points["standard"][self.spiro_p1].position[:3], self.points["standard"][self.spiro_p2].position[:3]), 1, "#FFFFFF33", thickness=1))
        except AttributeError:
            pass
