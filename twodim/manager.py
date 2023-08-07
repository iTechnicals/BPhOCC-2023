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

    def create_objects(self):
        self.panes = []
        self.buttons = []
        
        self.panes.append(Pane(self, 0.2, easing_duration = 1, easing_function = sin_ease))
        self.panes.append(Pane(self, 0.2, edge=1, easing_duration = 1, easing_function = sin_ease))
        self.buttons.append(Button(self, (60, 60), "twodim/assets/left_menu", turn_on_func=self.panes[0].start_ease))
        self.buttons.append(Button(self, (-60, 60), "twodim/assets/right_menu", "top_right", turn_on_func=self.panes[1].start_ease))

    def draw(self):
        [i.update() for i in self.panes + self.buttons]
        [i.draw() for i in self.panes + self.buttons]

    def update_resolution(self):
        [i.update_resolution() for i in self.panes + self.buttons]