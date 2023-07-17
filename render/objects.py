import pygame as pg
import pygame.gfxdraw
from numba import njit
import math
import time
from render.matrices import *

def DistributeSegments(multilines, segment_allowance):

    visible_multilines = [i for i in multilines if i.visible]
    total_length = sum(i.length for i in visible_multilines)
    visible_multilines.sort(key = lambda i: i.length)
    segment_allocation = []

    for i in visible_multilines:
        segments = math.floor(segment_allowance * i.length / total_length)
        segments = max(segments, i.min_segments)
        segments = min(segments, i.max_segments)

        segment_allocation.append(segments)

        segment_allowance -= segments
        total_length -= i.length

    if segment_allowance > 0:
        total_length = sum(i.length for i in visible_multilines if i.max_segments >= 9999)
        for i, j in enumerate(visible_multilines):
            if j.max_segments >= 9999:
                additional_segments = math.ceil(segment_allowance * j.length / total_length)
                segment_allocation[i] += additional_segments
                segment_allowance -= additional_segments
                total_length -= j.length
            if segment_allowance <= 0:
                break

    for i, j in enumerate(visible_multilines):
        j.generate_sublines(segment_allocation[i])


class Point:
    def __init__(self, render, position, size, colour, moving, movement_function, preset_args):
        self.render = render
        self.position = np.array([*position, 1.0]).astype(np.float32)
        self.colour = colour
        self.size = size
        self.moving = moving
        self.projected = None
        self.distance = None
        self.renderable = True
        self.preset_args = preset_args

        if self.moving:
            self.movement_function = movement_function
            self.movement()

    def movement(self):
        self.position = np.array([*self.movement_function(pg.time.get_ticks()/1000, *self.preset_args), 1.0])

    def screen_projection(self, m):
        if self.moving:
            self.movement()

        self.renderable = cos_angle_between(self.render.camera.forward, self.position - self.render.camera.position) > self.render.camera.cos_fov

        if self.renderable:
            position = self.position @ m
            position /= position[-1]
            position = position[:2]

            self.projected = position

            self.distance = math.hypot(*(self.position[:3] - self.render.camera.position[:3]))

    def draw(self):
        if self.renderable:
            pg.draw.circle(self.render.surface, pg.Color(self.colour), self.projected, max(2, self.size/self.distance * self.render.width/1280))

class PointlessLine:
    def __init__(self, render, point1, point2, parent):
        self.render = render
        self.point1 = np.array([*point1, 1.0]).astype(np.float32)
        self.point1_projected = None
        self.point2 = np.array([*point2, 1.0]).astype(np.float32)
        self.point2_projected = None
        self.parent = parent
        self.renderable = True
        self.screen_projection(self.render.m)

    def screen_projection(self, m):
        self.renderable = cos_angle_between(self.render.camera.forward, self.point1 - self.render.camera.position) > self.render.camera.d_cos_fov and cos_angle_between(self.render.camera.forward, self.point2 - self.render.camera.position) > self.render.camera.d_cos_fov and (cos_angle_between(self.render.camera.forward, self.point1 - self.render.camera.position) > self.render.camera.cos_fov or cos_angle_between(self.render.camera.forward, self.point2 - self.render.camera.position) > self.render.camera.cos_fov) and not self.parent.colour.a == 0 and not self.parent.hidden
        
        if self.renderable:
            position = self.point1 @ m
            position /= position[-1]
            position = position[:2]

            self.point1_projected = position
            
            position = self.point2 @ m
            position /= position[-1]
            position = position[:2]

            self.point2_projected = position
        

    def draw(self):
        if self.renderable:

            p1 = self.point1_projected; p2 = self.point2_projected
            d = (p2[0] - p1[0], p2[1] - p1[1])
            l = math.hypot(*d)
            sp = (-d[1] * self.parent.thickness/(2 * l), d[0] * self.parent.thickness/(2 * l))

            UL = (p1[0] - sp[0], p1[1] - sp[1])
            UR = (p1[0] + sp[0], p1[1] + sp[1])
            BL = (p2[0] - sp[0], p2[1] - sp[1])
            BR = (p2[0] + sp[0], p2[1] + sp[1])

            colour = self.parent.colour
            if self.parent.fading:
                colour.a = int(self.parent.opacity)
            pg.gfxdraw.aapolygon(self.render.surface, (UL, UR, BR, BL), colour)
            pg.gfxdraw.filled_polygon(self.render.surface, (UL, UR, BR, BL), colour)

class MultiLine:
    def __init__(self, render, f, preset_args, segments, colour, thickness = 2, length = None, min_segments = 0, max_segments = 9999, fading = False, duration = 0, fading_function = lambda x : 1 - x):
        self.render = render
        self.f = f
        self.preset_args = preset_args
        self.colour = pg.Color(colour)
        self.thickness = thickness
        self.length = length
        self.min_segments = min_segments
        self.max_segments = max_segments
        self.fading = fading
        self.visible = True
        self.hidden = False

        if self.fading:
            self.fading_function = fading_function
            self.duration = duration
            self.creation_time = time.time()
            self.initial_opacity = self.colour.a

        self.generate_sublines(segments)

    def generate_sublines(self, segments):
        self.segments = segments
        self.sublines = []

        for i in range(self.segments):

            t1 = i / segments; t2 = (i + 1) / segments # TODO: stop overlapping at multiline join points
            p1 = self.f(t1, *self.preset_args)
            p2 = self.f(t2, *self.preset_args)

            self.sublines.append(PointlessLine(self.render, p1, p2, self))

    def screen_projection(self, m):
        for i in self.sublines:
            i.screen_projection(m)
        visibility = np.any([i.renderable for i in self.sublines])
        if self.visible != visibility:
            self.visible = visibility
            # if self.render.new_second_flag:
            #     self.render.new_second_flag = False
            #     DistributeSegments(self.render.multilines, self.render.segment_allowance)
                # [i.screen_projection(m) for j in self.render.multilines for i in j.sublines]
        if self.fading:
            self.opacity = self.initial_opacity*self.fading_function((time.time() - self.creation_time)/self.duration)
            if self.opacity < 0 or self.opacity > 255:
                for i in self.sublines:
                    del i                
                self.render.multilines.remove(self)
                del self