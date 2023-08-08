import math
import numpy as np
import pygame as pg

class Line:
    def __init__(self, plotter, point1, point2, colour, thickness, relative=False):
        self.plotter = plotter
        self.point1 = point1
        self.point2 = point2
        self.colour = pg.Color(colour)
        if self.colour.a:
            self.ha_colour = pg.Color(colour)
            self.ha_colour.a //= 2
        self.thickness = thickness
        self.relative = relative

    def draw(self):
        p1 = (self.plotter.parent.viewport_width * self.point1[0], self.plotter.parent.viewport_height * self.point1[1]) if self.relative else self.point1
        p2 = (self.plotter.parent.viewport_width * self.point2[0], self.plotter.parent.viewport_height * self.point2[1]) if self.relative else self.point2

        d = (p2[0] - p1[0], p2[1] - p1[1])
        l = math.hypot(*d)
        sp = (
            -d[1] * self.thickness / (2 * l),
            d[0] * self.thickness / (2 * l),
        )

        UL = (p1[0] - sp[0], p1[1] - sp[1])
        UR = (p1[0] + sp[0], p1[1] + sp[1])
        BL = (p2[0] - sp[0], p2[1] - sp[1])
        BR = (p2[0] + sp[0], p2[1] + sp[1])

        pg.gfxdraw.filled_polygon(self.plotter.parent.viewport, (UL, UR, BR, BL), self.colour)
        pg.gfxdraw.aapolygon(self.plotter.parent.viewport, (UL, UR, BR, BL), self.ha_colour)