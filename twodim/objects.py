import numpy as np
import pygame as pg

class Pane:
    # left: 0
    # right: 1
    # top: 2
    # bottom: 3
    def __init__(self, parent, thickness, colour="#232633", edge=0, easing_duration=1, easing_function=lambda x: x):
        self.parent = parent
        self.thickness = thickness
        self.colour = pg.Color(colour)
        self.edge = edge
        self.easing_duration = easing_duration
        self.easing_function = easing_function
        
        self.surface = pg.Surface((0, 0))
        self.easing = False
        self.t = 0

    def start_ease(self):
        self.easing = True
        self.start_time = pg.time.get_ticks()
        self.inout = "in" if self.t < 0.5 else "out"

    def update(self):
        if self.easing:
            self.t = (pg.time.get_ticks() - self.start_time)/(1000*self.easing_duration)
            if self.t <= 0:
                self.t = 0
                self.easing = False
            if self.t >= 1:
                self.t = 1
                self.easing = False
            self.t = self.easing_function(self.t if self.inout == "in" else 1 - self.t)
            self.parent.parent.vp[self.edge] = self.thickness * self.t
            self.parent.parent.update_viewport(*self.parent.parent.vp)

    def update_resolution(self):
        if self.edge in (0, 1):
            self.surface = pg.transform.scale(self.surface, (self.thickness * self.parent.parent.width, self.parent.parent.height))
        else:
            self.surface = pg.transform.scale(self.surface, (self.parent.parent.width, self.thickness * self.parent.parent.height))

        match self.edge:
            case 0:
                self.off_blit = np.array([-self.thickness * self.parent.parent.width, 0])
                self.on_blit = np.array([0, 0])
            case 1:
                self.off_blit = np.array([self.parent.parent.width, 0])
                self.on_blit = np.array([(1 - self.thickness) * self.parent.parent.width, 0])
            case 2:
                self.off_blit = np.array([0, -self.thickness * self.parent.parent.height])
                self.on_blit = np.array([0, 0])
            case 3:
                self.off_blit = np.array([0, self.parent.parent.height])
                self.on_blit = np.array([0, (1 - self.thickness) * self.parent.parent.height])

    def draw(self):
        self.surface.fill(self.colour)
        self.parent.parent.screen.blit(self.surface, self.t*self.on_blit + (1 - self.t)*self.off_blit)


class Button:
    def __init__(self, parent, centre_pos, texture_path, anchor="top_left", positioning="absolute", width=None, pane=None, turn_on_func=lambda: None, turn_off_func=lambda: None):
        self.parent = parent
        self.anchor = anchor
        self.offset_centre_pos = centre_pos
        self.positioning = positioning
        self.pane = pane
        self.turn_on_func = turn_on_func
        self.turn_off_func = turn_off_func

        self.on = False
        self.neutral_texture = pg.image.load(texture_path + "/neutral.png")
        self.hover_texture = pg.image.load(texture_path + "/hovered.png")
        self.down_texture = pg.image.load(texture_path + "/pressed.png")

        if self.positioning == "relative":
            self.width = width
            self.base_neutral_texture = self.neutral_texture
            self.base_hover_texture = self.hover_texture
            self.base_down_texture = self.down_texture

        self.texture = self.neutral_texture

    def update_resolution(self):

        match self.positioning:
            case "absolute":
                match self.anchor:
                    case "top_left":
                        self.centre_pos = self.offset_centre_pos
                    case "top_right":
                        self.centre_pos = (self.parent.parent.viewport_width + self.offset_centre_pos[0], self.offset_centre_pos[1])
                    case "bottom_left":
                        self.centre_pos = (self.offset_centre_pos[0], self.parent.parent.viewport_height + self.offset_centre_pos[1])
                    case "bottom_right":
                        self.centre_pos = (self.parent.parent.viewport_width + self.offset_centre_pos[0], self.parent.parent.viewport_height + self.offset_centre_pos[1])
            case "relative":
                self.neutral_texture = pg.transform.smoothscale(self.base_neutral_texture, (self.width * self.parent.parent.viewport_width, self.width * self.parent.parent.viewport_width * self.base_neutral_texture.get_height() / self.base_neutral_texture.get_width()))
                self.hover_texture = pg.transform.smoothscale(self.base_hover_texture, (self.width * self.parent.parent.viewport_width, self.width * self.parent.parent.viewport_width * self.base_hover_texture.get_height() / self.base_hover_texture.get_width()))
                self.down_texture = pg.transform.smoothscale(self.base_down_texture, (self.width * self.parent.parent.viewport_width, self.width * self.parent.parent.viewport_width * self.base_down_texture.get_height() / self.base_down_texture.get_width()))
                self.abs_centre_pos = (self.offset_centre_pos[0] * self.parent.parent.viewport_width, self.offset_centre_pos[1] * self.parent.parent.viewport_width)
                match self.anchor:
                    case "top_left":
                        self.centre_pos = self.abs_centre_pos
                    case "top_right":
                        self.centre_pos = (self.parent.parent.viewport_width + self.abs_centre_pos[0], self.abs_centre_pos[1])
                    case "bottom_left":
                        self.centre_pos = (self.abs_centre_pos[0], self.parent.parent.viewport_height + self.abs_centre_pos[1])
                    case "bottom_right":
                        self.centre_pos = (self.parent.parent.viewport_width + self.abs_centre_pos[0], self.parent.parent.viewport_height + self.abs_centre_pos[1])

        self.top_left = (self.centre_pos[0] - (self.texture.get_width() - 1)/2, self.centre_pos[1] - (self.texture.get_height() - 1)/2)
        if self.pane:
            self.abs_top_left = (self.top_left[0] + self.pane.blit[0], self.top_left[1] + self.pane.blit[1])
        else:
            self.abs_top_left = (self.top_left[0] + self.parent.parent.blit[0], self.top_left[1] + self.parent.parent.blit[1])

    def update(self):
        
        self.hovered = pg.mouse.get_pos()[0] >= self.abs_top_left[0] and pg.mouse.get_pos()[0] <= self.abs_top_left[0] + self.texture.get_width() and pg.mouse.get_pos()[1] >= self.abs_top_left[1] and pg.mouse.get_pos()[1] <= self.abs_top_left[1] + self.texture.get_height()
        self.new_on = self.hovered and pg.mouse.get_pressed()[0]

        if not self.on and self.new_on:
            self.turn_on_func()
            self.on = self.new_on

        if self.on and not self.new_on:
            self.turn_off_func()
            self.on = self.new_on

        if self.on:
            self.texture = self.down_texture
        elif self.hovered:
            self.texture = self.hover_texture
        else:
            self.texture = self.neutral_texture

        self.top_left = (self.centre_pos[0] - (self.texture.get_width() - 1)/2, self.centre_pos[1] - (self.texture.get_height() - 1)/2)

    def draw(self):

        if self.pane:
            self.pane.surface.blit(self.texture, (self.top_left[0], self.top_left[1]))
        else:
            self.parent.parent.viewport.blit(self.texture, (self.top_left[0], self.top_left[1]))
