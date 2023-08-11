from twodim.objects import *

import pygame as pg
import math, json

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
        if showing == "graph":
            self.parent.plotter.animate()

    def create_objects(self):
        self.panes = []
        self.buttons = []

        with open("data.json", newline="") as data:
            contents = list(json.loads(data.read())["planets"].keys())
        
        self.panes.append(Pane(self, 0.2, easing_duration = 1, easing_function = sin_ease))
        self.panes.append(Pane(self, 0.2, edge=1, easing_duration = 1, easing_function = sin_ease))
        self.buttons.append(Button(self, "both", (50, 50), "twodim/assets/left_menu", turn_on_func=self.panes[0].start_ease))
        self.buttons.append(Button(self, "both", (-50, 50), "twodim/assets/right_menu", "top_right", turn_on_func=self.panes[1].start_ease))
        self.panes[0].children.append(Button(self, "both", (0.5, 0.2), "twodim/assets/graphing_interface", positioning="relative", widths=(0.84375, 0.875, 0.875), pane=self.panes[0], turn_on_func=lambda: self.set_showing("graph")))
        self.panes[0].children.append(Button(self, "both", (0.5, 0.5), "twodim/assets/ss_renderer", positioning="relative", widths=(0.84375, 0.875, 0.875), pane=self.panes[0], turn_on_func=lambda: self.set_showing("render")))

        self.panes[1].children.append(Button(self, "render", (0.5, 0.2), "twodim/assets/refresh", positioning="relative", widths=(0.84375, 0.875, 0.875), pane=self.panes[1], turn_on_func=lambda: self.parent.render.create_objects()))

        self.panes[1].children.append(Dropdown(self, "render", (0.27, 0.8), ("twodim/assets/dropdown_head", "twodim/assets/dropdown_top", "twodim/assets/dropdown_mid", "twodim/assets/dropdown_bottom"), 0.4, contents, pane=self.panes[1]))
        self.panes[1].children.append(Dropdown(self, "render", (0.73, 0.8), ("twodim/assets/dropdown_head", "twodim/assets/dropdown_top", "twodim/assets/dropdown_mid", "twodim/assets/dropdown_bottom"), 0.4, contents, pane=self.panes[1]))
        self.panes[1].children.append(Button(self, "render", (0.5, 1), "twodim/assets/spirograph", positioning="relative", widths=(0.84375, 0.875, 0.875), pane=self.panes[1], turn_on_func=lambda selected: self.parent.render.start_spiro(selected), on_extra_args=((self.panes[1].children[1].get_selected, self.panes[1].children[2].get_selected),)))

        self.panes[1].children.append(Dropdown(self, "render", (0.5, 0.4), ("twodim/assets/dropdown_head", "twodim/assets/dropdown_top", "twodim/assets/dropdown_mid", "twodim/assets/dropdown_bottom"), 0.4, contents, pane=self.panes[1]))
        self.panes[1].children.append(Button(self, "render", (0.5, 0.6), "twodim/assets/ptolemy_mode", positioning="relative", widths=(0.84375, 0.875, 0.875), pane=self.panes[1], turn_on_func=lambda selected: self.parent.render.ptolemy_update(selected), on_extra_args=(self.panes[1].children[4].get_selected,)))

        self.panes[1].children.append(Button(self, "graph", (0.5, 0.2), "twodim/assets/K3_raw", positioning="relative", widths=(0.84375, 0.875, 0.875), pane=self.panes[1], turn_on_func=lambda plot: self.parent.plotter.set_visible_plot(plot), on_extra_args=("K3_raw",)))        
        self.panes[1].children.append(Button(self, "graph", (0.5, 0.5), "twodim/assets/K3_lin", positioning="relative", widths=(0.84375, 0.875, 0.875), pane=self.panes[1], turn_on_func=lambda plot: self.parent.plotter.set_visible_plot(plot), on_extra_args=("K3_lin",)))
        self.panes[1].children.append(Button(self, "graph", (0.5, 0.8), "twodim/assets/polar", positioning="relative", widths=(0.84375, 0.875, 0.875), pane=self.panes[1], turn_on_func=lambda plot: self.parent.plotter.set_visible_plot(plot), on_extra_args=("polar",)))

    def tick(self):
        # print(self.panes[1].children[1].children[0].centre_pos, self.panes[1].children[1].children[0].texture.get_size(), self.panes[1].children[1].children[0].top_left, self.panes[1].blit_coords, self.panes[1].children[1].children[0].abs_top_left)
        [i.update() for i in self.panes + self.buttons]
        for pane in self.panes:
            pane.draw()
        [i.draw() for i in self.buttons]

    def update_resolution(self):
        [i.update_resolution() for i in self.panes]
        [i.update_resolution() for i in self.buttons + [child for pane in self.panes for child in pane.children]]