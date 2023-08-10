import math
import numpy as np
import pygame as pg

class Line:
    def __init__(self, plotter, point1, point2, colour, thickness, relative=False, display="fancy"):
        self.plotter = plotter
        self.point1 = point1
        self.point2 = point2
        self.colour = pg.Color(colour)
        if self.colour.a:
            self.ha_colour = pg.Color(colour)
            self.ha_colour.a //= 2
        self.thickness = thickness
        self.relative = relative
        self.display = display

    def draw(self):
        p1 = (self.plotter.parent.viewport_width * self.point1[0], self.plotter.parent.viewport_height * self.point1[1]) if self.relative else self.point1
        p2 = (self.plotter.parent.viewport_width * self.point2[0], self.plotter.parent.viewport_height * self.point2[1]) if self.relative else self.point2
        match self.display:
            case "fancy":
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
            case "fast":
                pg.draw.line(self.plotter.parent.viewport, self.colour, p1, p2, width=self.thickness)

class Point:
    def __init__(self, plotter, position, colour, thickness, style="o", size=0.003):
        self.plotter = plotter
        self.position = position
        self.colour = pg.Color(colour)
        self.thickness = thickness
        self.style = style
        self.size = size

    def draw(self):
        match self.style:
            case "o":
                pg.draw.circle(self.plotter.parent.viewport, self.colour, (self.position[0] * self.plotter.parent.viewport_width, self.position[1] * self.plotter.parent.viewport_height), self.thickness)

class Text:
    def __init__(self, plotter, text, position, colour, font, size, bold=False, italic=False, relative=False):
        self.plotter = plotter
        self.text = text
        self.position = position
        self.colour = pg.Color(colour)
        self.font = font
        self.size = size
        self.bold = bold
        self.italic = italic
        self.relative = relative

        self.font_object = pg.freetype.SysFont(self.font, self.size * math.sqrt(self.plotter.parent.viewport_height * self.plotter.parent.viewport_width) / 960, self.bold, self.italic)
        self.text_object, self.rect = self.font_object.render(self.text, self.colour)
        self.rect.center = (self.plotter.parent.viewport_width * self.position[0], self.plotter.parent.viewport_height * self.position[1]) if self.relative else self.position

    def draw(self):
        self.plotter.parent.viewport.blit(self.text_object, self.rect)

    def update_resolution(self):
        self.font_object = pg.freetype.SysFont(self.font, self.size * math.sqrt(self.plotter.parent.viewport_height * self.plotter.parent.viewport_width) / 960, self.bold, self.italic)
        self.text_object, self.rect = self.font_object.render(self.text, self.colour)
        self.rect.center = (self.plotter.parent.viewport_width * self.position[0], self.plotter.parent.viewport_height * self.position[1]) if self.relative else self.position