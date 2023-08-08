from twodim.objects import *

import pygame as pg
import math

def cubic_ease(t):
    return 4 * t * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 3) / 2

def sin_ease(t):
    return (1 - math.cos(math.pi * t)) / 2

class Manager:
    def __init__(self, parent):
        self.parent = parent
        self.create_objects()

    def set_showing(self, showing):
        self.parent.showing = showing

    def create_objects(self):
        self.panes = []
        self.buttons = []
        
        self.panes.append(Pane(self, 0.2, easing_duration = 1, easing_function = sin_ease))
        self.panes.append(Pane(self, 0.2, edge=1, easing_duration = 1, easing_function = sin_ease))
        self.buttons.append(Button(self, (50, 50), "twodim/assets/left_menu", turn_on_func=self.panes[0].start_ease))
        self.buttons.append(Button(self, (-50, 50), "twodim/assets/right_menu", "top_right", turn_on_func=self.panes[1].start_ease))
        self.panes[0].children.append(Button(self, (0.5, 0.2), "twodim/assets/graphing_interface", positioning="relative", widths=(0.84375, 0.875, 0.875), pane=self.panes[0], turn_on_func=lambda: self.set_showing("graph")))
        self.panes[0].children.append(Button(self, (0.5, 0.5), "twodim/assets/ss_renderer", positioning="relative", widths=(0.84375, 0.875, 0.875), pane=self.panes[0], turn_on_func=lambda: self.set_showing("render")))

    def tick(self):
        [i.update() for i in self.panes + self.buttons]
        [i.draw() for i in self.panes]
        [i.draw() for i in self.buttons]

    def update_resolution(self):
        [i.update_resolution() for i in self.panes + self.buttons + [child for pane in self.panes for child in pane.children]]