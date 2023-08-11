import math, json
import numpy as np
import pygame as pg

from itertools import chain

from plotter.objects import *
from plotter.mathtools import *

class Plotter:
    def __init__(self, parent, bottom_left, top_right):
        self.parent = parent
        self.bottom_left = bottom_left
        self.top_right = top_right

        self.width = top_right[0] - bottom_left[0]
        self.height = top_right[1] - bottom_left[1]

        self.animating = False
        self.create_objects()
        self.tick()

    def set_visible_plot(self, plot):
        self.visible_plot = plot
        self.animate()

    def create_objects(self):
        semimajors = []
        periods = []
        
        self.plots = {"K3_raw": [],
                      "K3_lin": [],
                      "polar": []}

        with open("data.json", newline="") as data:
            contents = json.loads(data.read())["planets"]
            for name, row in contents.items():
                clr_planet, clr_orbit, a, ecc, beta, period, radius = (
                    row["planet_colour"],
                    row["orbit_colour"],
                    row["semimajor"],
                    row["eccentricity"],
                    row["beta"],
                    row["period"],
                    row["radius"],
                )
                semimajors.append(a)
                periods.append(period)

        self.visible_plot = "K3_raw"

        self.make_plot("K3_raw", (semimajors, periods), ("Semi-major axis / AU", "Orbital period / yr"))
        self.make_plot("K3_lin", (semimajors, periods), ("Semi-major axis ^ 3/2 / AU ^ 3/2", "Orbital period / yr"))
        self.make_plot("polar", (period, ecc), ("Time / yr", "Orbit angle / rad"))

        self.animate()

    def make_plot(self, key, args, labels):
        match key:
            case "K3_raw":
                self.plot_line("K3_raw", lambda x: pow(args[1][-1], 2/3) / args[0][-1] * pow(x, 3/2), (), (0, args[0][-1]), colour="#687599", thickness=2, make_graph=True, labels=labels)
                self.plot_points("K3_raw", list(zip(args[0], args[1])), colour="#8A9BCC", line=None)
            case "K3_lin":
                self.plot_points("K3_lin", list(zip([pow(a, 3/2) for a in args[0]], args[1])), colour="#8A9BCC", make_graph=True, labels=labels, degree=1)
            case "polar":
                self.plot_line("polar", lambda x: args[0] * x / (2 * math.pi), (), (0, 6 * math.pi), colour="#687599", thickness=2, make_graph=True, labels=labels, reverse=True)
                self.plot_line("polar", orbit_angle, (args[0], args[1]), (0, 6 * math.pi), colour="#8A9BCC", thickness=2, reverse=True)

    def make_graph(self, plot, points, labels):
        self.x_gridlines = self.decide_gridlines([point[0] for point in points])
        self.y_gridlines = self.decide_gridlines([point[1] for point in points])
        self.gridlines = self.make_gridlines(plot, vertical_gridlines=self.y_gridlines[1], horizontal_gridlines=self.x_gridlines[1])

        for i in range(self.x_gridlines[1] + 1):
            self.plots[plot].append(Text(self, str(self.x_gridlines[0] + i*self.x_gridlines[2]), (self.bottom_left[0] * (1 - i / self.x_gridlines[1]) + self.top_right[0] * i / self.x_gridlines[1], self.bottom_left[1] + 0.03), "#8A9BCC", "Segoe UI", 16, bold=True, relative=True))

        for i in range(self.y_gridlines[1] + 1):
            self.plots[plot].append(Text(self, str(self.y_gridlines[0] + i*self.y_gridlines[2]), (self.bottom_left[0] - 0.03 * self.parent.viewport_height / self.parent.viewport_width, self.bottom_left[1] * (1 - i / self.y_gridlines[1]) + self.top_right[1] * i / self.y_gridlines[1]), "#8A9BCC", "Segoe UI", 16, bold=True, relative=True))

        if labels:
            self.plots[plot].append(Text(self, labels[0], ((self.bottom_left[0] + self.top_right[0])/2, self.bottom_left[1] + 0.06), "#8A9BCC", "Segoe UI", 16, bold=True, relative=True))
            self.plots[plot].append(Text(self, labels[1], (self.bottom_left[0] - 0.06 * self.parent.viewport_height / self.parent.viewport_width, (self.bottom_left[1] + self.top_right[1])/2), "#8A9BCC", "Segoe UI", 16, rotation=90, bold=True, relative=True))


    def plot_points(self, plot, points, colour="#FFFFFF", thickness=5, plot_type="o", line="best_fit", degree=2, make_graph=False, labels=None):
        if make_graph:
            self.make_graph(plot, points, labels)
        
        for point in points:
            point_x = self.bottom_left[0] + (point[0] - self.x_gridlines[0]) * self.width / (self.x_gridlines[1] * self.x_gridlines[2])
            point_y = self.bottom_left[1] + (point[1] - self.y_gridlines[0]) * self.height / (self.y_gridlines[1] * self.y_gridlines[2])
            self.plots[plot].append(Point(self, (point_x, point_y), colour, thickness, style=plot_type))

        match line:
            case "best_fit":
                sols = regress(points, degree)
                self.plot_line(plot, cfcs_to_func, (sols,), (min([point[0] for point in points]), max([point[0] for point in points])), colour, thickness // 2, lines=1 if degree == 1 else 50)

    def plot_line(self, plot, func, preset_args, x_interval, colour, thickness, lines=50, make_graph=False, labels=None, reverse=False):
        
        points = []
        for point in range(lines+1):
            t = point/lines
            point_x = t*x_interval[0] + (1-t)*x_interval[1]
            point_y = func(point_x, *preset_args)
            points.append([point_y, point_x] if reverse else [point_x, point_y])

        if make_graph:
            self.make_graph(plot, points, labels)

        for point in points:
            point[0] = self.bottom_left[0] + (point[0] - self.x_gridlines[0]) * self.width / (self.x_gridlines[1] * self.x_gridlines[2])
            point[1] = self.bottom_left[1] + (point[1] - self.y_gridlines[0]) * self.height / (self.y_gridlines[1] * self.y_gridlines[2])
        
        for i in range(lines):
            self.plots[plot].append(Line(self, points[i], points[i+1], colour, thickness, relative=True))
        
    def decide_gridlines(self, values, ming=5, maxg=8):
        minv, maxv = np.inf, -np.inf
        for value in values:
            minv = min(minv, value)
            maxv = max(maxv, value)
        k_multiplier = pow(10, math.floor(np.log10(2*maxv - 2*minv)) - 1)
        rounded_diff = math.ceil((maxv - minv) / k_multiplier) * k_multiplier
        bottom = math.floor(minv / k_multiplier) * k_multiplier
        searching = True
        while searching:
            for i in range(ming, maxg + 1):
                if rounded_diff % (k_multiplier * i) == 0:
                    searching = False
                    gridlines = i
                    gridline_val = rounded_diff // i
                    break
            rounded_diff += k_multiplier
        return bottom, gridlines, gridline_val

    def make_gridlines(self, plot, vertical_gridlines=6, horizontal_gridlines=5, colour="#CCCCCC33", axis_colour="#CCCCCCCC", thickness=2):
        self.gridlines = []
        bottom_left = np.array(self.bottom_left)
        top_left = np.array([self.bottom_left[0], self.top_right[1]])
        bottom_right = np.array([self.top_right[0], self.bottom_left[1]])
        top_right = np.array(self.top_right)
        for i in range(horizontal_gridlines+1):
            t_i = i / horizontal_gridlines
            this_colour = axis_colour if i == 0 else colour
            self.plots[plot].append(Line(self, t_i*bottom_right + (1-t_i)*bottom_left, t_i*top_right + (1-t_i)*top_left, this_colour, thickness, relative=True))
        for i in range(vertical_gridlines+1):
            t_i = i / vertical_gridlines
            this_colour = axis_colour if i == 0 else colour
            self.plots[plot].append(Line(self, t_i*top_right + (1-t_i)*bottom_right, t_i*top_left + (1-t_i)*bottom_left, this_colour, thickness, relative=True))
        return self.gridlines

    def animate(self, duration=1000, relative=True):
        self.animating = True
        self.anim_start = pg.time.get_ticks()
        self.anim_dur = duration
        self.anim_bottom_left = (self.bottom_left[0] - 0.01, self.bottom_left[1] + 0.01)
        self.anim_top_right = (self.top_right[0] + 0.01, self.top_right[1] - 0.01)
        self.anim_relative = relative

    def tick(self):
        self.draw()

    def draw(self):
        [object.draw() for object in self.plots[self.visible_plot]]
        if self.animating:
            t = 2 * ((pg.time.get_ticks() - self.anim_start) / self.anim_dur) - 1
            if t >= 1:
                self.animating = False
            else:
                scaled_blx = self.parent.viewport_width * self.anim_bottom_left[0] if self.anim_relative else self.anim_bottom_left[0]
                scaled_bly = self.parent.viewport_height * self.anim_bottom_left[1] if self.anim_relative else self.anim_bottom_left[1]
                scaled_trx = self.parent.viewport_width * self.anim_top_right[0] if self.anim_relative else self.anim_top_right[0]
                scaled_try = self.parent.viewport_height * self.anim_top_right[1] if self.anim_relative else self.anim_top_right[1]
                pg.gfxdraw.filled_trigon(self.parent.viewport, int(scaled_trx), int(scaled_try), int(t*scaled_trx + (1-t)*scaled_blx), int(scaled_try), int(scaled_trx), int(t*scaled_try + (1-t)*scaled_bly), pg.Color("#2C3040"))

    def update_resolution(self):
        [text.update_resolution() for text in chain.from_iterable(self.plots.values()) if text.__class__ == Text]
