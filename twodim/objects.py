import math
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

        self.children = []

        self.update()
        self.update_resolution()
        self.draw()

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

        self.blit_coords = self.t*self.on_blit + (1 - self.t)*self.off_blit

    def draw(self):

        self.surface.fill(self.colour)

        [child.update() for child in self.children]
        [child.draw() for child in self.children if type(child) == Button]
        [child.draw() for child in self.children if type(child) == Dropdown]
        self.blit_coords = self.t*self.on_blit + (1 - self.t)*self.off_blit
        
        self.parent.parent.screen.blit(self.surface, self.blit_coords)


class Button:
    def __init__(self, parent, toggle, centre_pos, texture_path, anchor="top_left", positioning="absolute", widths=None, pane=None, text=None, turn_on_func=None, turn_off_func=None, on_extra_args=None, off_extra_args=None):
        self.parent = parent
        self.toggle = toggle
        self.anchor = anchor
        self.offset_centre_pos = centre_pos
        self.positioning = positioning
        self.pane = pane
        self.text = text
        self.turn_on_func = turn_on_func
        self.turn_off_func = turn_off_func

        self.on_extra_args = on_extra_args if on_extra_args else []
        self.off_extra_args = off_extra_args if off_extra_args else []

        self.on = False
        self.hovered = False
        self.neutral_texture = pg.image.load(texture_path + "/neutral.png").convert_alpha()
        self.hover_texture = pg.image.load(texture_path + "/hovered.png").convert_alpha()
        self.down_texture = pg.image.load(texture_path + "/pressed.png").convert_alpha()

        if self.positioning == "relative":
            self.widths = widths
            self.base_neutral_texture = pg.image.load(texture_path + "/neutral.png").convert_alpha()
            self.base_hover_texture = pg.image.load(texture_path + "/hovered.png").convert_alpha()
            self.base_down_texture = pg.image.load(texture_path + "/pressed.png").convert_alpha()

        self.texture = pg.image.load(texture_path + "/neutral.png").convert_alpha()

        self.update_resolution()

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
                parent_width = self.pane.surface.get_width() if self.pane else self.parent.parent.viewport_width
                self.neutral_texture = pg.transform.smoothscale(self.base_neutral_texture, (self.widths[0] * parent_width, self.widths[0] * parent_width * self.base_neutral_texture.get_height() / self.base_neutral_texture.get_width()))
                self.hover_texture = pg.transform.smoothscale(self.base_hover_texture, (self.widths[1] * parent_width, self.widths[1] * parent_width * self.base_hover_texture.get_height() / self.base_hover_texture.get_width()))
                self.down_texture = pg.transform.smoothscale(self.base_down_texture, (self.widths[2] * parent_width, self.widths[2] * parent_width * self.base_down_texture.get_height() / self.base_down_texture.get_width()))
                if self.on:
                    self.texture = self.down_texture
                elif self.hovered:
                    self.texture = self.hover_texture
                else:
                    self.texture = self.neutral_texture
                self.abs_centre_pos = (self.offset_centre_pos[0] * parent_width, self.offset_centre_pos[1] * parent_width)
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
            self.abs_top_left = (self.top_left[0] + self.pane.blit_coords[0], self.top_left[1] + self.pane.blit_coords[1])
        else:
            self.abs_top_left = (self.top_left[0] + self.parent.parent.blit_coords[0], self.top_left[1] + self.parent.parent.blit_coords[1])

        if self.text:
            self.text.update_resolution()

    def update(self):

        if self.toggle in (self.parent.parent.showing, "both"):
        
            self.hovered = pg.mouse.get_pos()[0] >= self.abs_top_left[0] and pg.mouse.get_pos()[0] <= self.abs_top_left[0] + self.texture.get_width() and pg.mouse.get_pos()[1] >= self.abs_top_left[1] and pg.mouse.get_pos()[1] <= self.abs_top_left[1] + self.texture.get_height()
            self.new_on = self.hovered and pg.mouse.get_pressed()[0]

            if self.pane:
                if len(self.pane.children) == 9:
                    if (self.offset_centre_pos == (0.5, 1) and (self.pane.children[1].open or self.pane.children[2].open or self.pane.children[4].open)) or (self.offset_centre_pos == (0.5, 0.6) and self.pane.children[4].open):
                        self.hovered = False

            if not self.on and self.new_on:
                self.on = self.new_on
                if self.turn_on_func:
                    self.turn_on_func(*self.on_extra_args)

            if self.on and not self.new_on:
                self.on = self.new_on
                if self.turn_off_func:
                    self.turn_off_func(*self.off_extra_args)

            if self.on:
                self.texture = self.down_texture
            elif self.hovered:
                self.texture = self.hover_texture
            else:
                self.texture = self.neutral_texture

            self.top_left = (self.centre_pos[0] - (self.texture.get_width() - 1)/2, self.centre_pos[1] - (self.texture.get_height() - 1)/2)

    def draw(self):

        if self.toggle in (self.parent.parent.showing, "both"):

            if self.pane:
                self.pane.surface.blit(self.texture, (self.top_left[0], self.top_left[1]))
            else:
                self.parent.parent.viewport.blit(self.texture, (self.top_left[0], self.top_left[1]))

                
            if self.text:
                self.text.draw()



class Dropdown:
    def __init__(self, parent, toggle, centre_pos, texture_paths, width, options, pane, textcolour="#8A9BCC", textfont="Segoe UI", textsize=12):
        self.parent = parent
        self.toggle = toggle
        self.centre_pos = centre_pos
        self.width = width
        self.options = options
        self.pane = pane

        self.texture = pg.image.load(texture_paths[0] + "/neutral.png")
        self.texture_height = 0.97 * self.width * self.texture.get_height() / self.texture.get_width() 

        self.children = []
        self.children.append(Button(self.parent, self.toggle, self.centre_pos, texture_paths[0], positioning="relative", widths=[self.width] * 3, pane=self.pane, text=Text(self.parent, self.pane, "Select planet", self.centre_pos, textcolour, textfont, textsize, relative=True, bold=True), turn_on_func=lambda: self.drop_toggle()))
        self.children.append(Button(self.parent, self.toggle, (self.centre_pos[0], self.centre_pos[1] + self.texture_height), texture_paths[1], positioning="relative", widths=[self.width] * 3, pane=self.pane, text=Text(self.parent, self.pane, options[0], (self.centre_pos[0], self.centre_pos[1] + self.texture_height), textcolour, textfont, textsize, relative=True), turn_on_func=self.update_head_text, on_extra_args=(options[0],)))
        for index, option in enumerate(self.options[1:-1]):
            self.children.append(Button(self.parent, self.toggle, (self.centre_pos[0], self.centre_pos[1] + (index+2)*self.texture_height), texture_paths[2], positioning="relative", widths=[self.width] * 3, pane=self.pane, text=Text(self.parent, self.pane, option, (self.centre_pos[0], self.centre_pos[1] + (index+2)*self.texture_height), textcolour, textfont, textsize, relative=True), turn_on_func=self.update_head_text, on_extra_args=(option,)))
        self.children.append(Button(self.parent, self.toggle, (self.centre_pos[0], self.centre_pos[1] + (index+3)*self.texture_height), texture_paths[3], positioning="relative", widths=[self.width] * 3, pane=self.pane, text=Text(self.parent, self.pane, options[-1], (self.centre_pos[0], self.centre_pos[1] + (index+3)*self.texture_height), textcolour, textfont, textsize, relative=True), turn_on_func=self.update_head_text, on_extra_args=(options[-1],)))

        self.open = False

    def update_head_text(self, text):
        if self.open:
            self.selected = text
            self.children[0].text.update(text)
            self.drop_toggle()

    def get_selected(self):
        return self.selected

    def drop_toggle(self):
        self.open = not self.open

    def update_resolution(self):
        [button.update_resolution() for button in self.children]

    def update(self):
        [button.update() for button in self.children]

    def draw(self):
        if self.toggle in (self.parent.parent.showing, "both"):
            self.children[0].draw()
            if self.open:
                [button.draw() for button in self.children[1:]]


class Text:
    def __init__(self, parent, pane, text, position, colour, font, size, align="center", rotation=0, bold=False, italic=False, relative=False):
        self.parent = parent
        self.pane = pane
        self.text = text
        self.position = position
        self.align = align
        self.rotation = rotation
        self.colour = pg.Color(colour)
        self.font = font
        self.size = size
        self.bold = bold
        self.italic = italic
        self.relative = relative

        self.font_object = pg.freetype.SysFont(self.font, self.size * math.sqrt(self.pane.surface.get_height() * self.pane.surface.get_width()) / 960, self.bold, self.italic)
        self.text_object, self.rect = self.font_object.render(self.text, self.colour)
        self.text_object = pg.transform.rotate(self.text_object, self.rotation)
        self.rect = self.text_object.get_rect()
        self.rect.center = (self.pane.surface.get_width() * self.position[0], self.pane.surface.get_width() * self.position[1]) if self.relative else self.position

    def draw(self):
        self.pane.surface.blit(self.text_object, self.rect)

    def update(self, text):
        self.text = text
        self.text_object, self.rect = self.font_object.render(self.text, self.colour)
        self.text_object = pg.transform.rotate(self.text_object, self.rotation)
        self.rect = self.text_object.get_rect()
        setattr(self.rect, self.align, (self.pane.surface.get_width() * self.position[0], self.pane.surface.get_width() * self.position[1]) if self.relative else self.position)

    def update_resolution(self):
        self.font_object = pg.freetype.SysFont(self.font, self.size * math.sqrt(self.parent.parent.viewport_height * self.parent.parent.viewport_width) / 960, self.bold, self.italic)
        self.text_object, self.rect = self.font_object.render(self.text, self.colour)
        self.text_object = pg.transform.rotate(self.text_object, self.rotation)
        self.rect = self.text_object.get_rect()
        setattr(self.rect, self.align, (self.pane.surface.get_width() * self.position[0], self.pane.surface.get_width() * self.position[1]) if self.relative else self.position)