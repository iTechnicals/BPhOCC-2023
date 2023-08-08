import math
import numpy as np
import pygame as pg

from plotter.objects import *

class Plotter:
    def __init__(self, parent):
        self.parent = parent
        self.animating = False
        self.create_objects()
        self.tick()

    def create_objects(self):
        self.lines = []
        [self.lines.append(gridline) for gridline in self.gridlines()]
        self.animate()

    def gridlines(self, gridlines=6, colour="#CCCCCC33", axis_colour="#CCCCCCCC", thickness=2, bottom_left=(0.1, 0.1), top_right=(0.9, 0.9)):
        self.gridlines = []
        bottom_left = np.array(bottom_left)
        top_left = np.array([bottom_left[0], top_right[1]])
        bottom_right = np.array([top_right[0], bottom_left[1]])
        top_right = np.array(top_right)
        for i in range(gridlines+1):
            t_i = i / gridlines
            this_colour = axis_colour if i == 0 else colour
            self.gridlines.append(Line(self, t_i*bottom_right + (1-t_i)*bottom_left, t_i*top_right + (1-t_i)*top_left, this_colour, thickness, relative=True))
        for i in range(gridlines+1):
            t_i = i / gridlines
            this_colour = axis_colour if i == 0 else colour
            self.gridlines.append(Line(self, t_i*bottom_left + (1-t_i)*top_left, t_i*bottom_right + (1-t_i)*top_right, this_colour, thickness, relative=True))
        return self.gridlines

    def animate(self, duration=1000, bottom_left=(0.09, 0.91), top_right=(0.91, 0.09), relative=True):
        self.animating = True
        self.anim_start = pg.time.get_ticks()
        self.anim_dur = duration
        self.anim_bottom_left = bottom_left
        self.anim_top_right = top_right
        self.anim_relative = relative

    def tick(self):
        self.draw()

    def draw(self):
        [line.draw() for line in self.lines]
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
