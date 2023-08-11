import pygame as pg
import pygame.gfxdraw
import math
import time
from render.matrices import *

# RENDER PIPELINE:
# position = self.position @ m
# position /= position[-1]
# position = position[:2]

# def DistributeSegments(render, multilines, segment_allowance):

#     render.points_table = []
#     visible_multilines = [i for i in multilines if i.visible]
#     total_length = sum(i.length for i in visible_multilines)
#     visible_multilines.sort(key = lambda i: i.length)
#     segment_allocation = []

#     for i in visible_multilines:
#         segments = math.floor(segment_allowance * i.length / total_length)
#         segments = max(segments, i.min_segments)
#         segments = min(segments, i.max_segments)

#         segment_allocation.append(segments)

#         segment_allowance -= segments
#         total_length -= i.length

#     if segment_allowance > 0:
#         total_length = sum(i.length for i in visible_multilines if i.max_segments >= 9999)
#         for i, j in enumerate(visible_multilines):
#             if j.max_segments >= 9999:
#                 additional_segments = math.ceil(segment_allowance * j.length / total_length)
#                 segment_allocation[i] += additional_segments
#                 segment_allowance -= additional_segments
#                 total_length -= j.length
#             if segment_allowance <= 0:
#                 break

#     for i, j in enumerate(visible_multilines):
#         j.generate_sublines(segment_allocation[i])

#     render.points_table = np.array(render.points_table)


class Point:
    def __init__(
        self, render, toggle, position, size, colour, moving, movement_function, preset_args, id
    ):
        self.render = render
        self.toggle = toggle
        self.position = np.array([*position, 1.0])
        self.colour = colour
        self.size = size
        self.moving = moving
        self.projected = None
        self.distance = None
        self.renderable = True
        self.preset_args = preset_args
        self.id = id

        if self.moving:
            self.movement_function = movement_function
            self.movement()

    def movement(self):
        self.position = np.array(
            [
                *self.movement_function(pg.time.get_ticks() / 1000, *self.preset_args),
                1.0,
            ]
        )

    def camera_distance(self):
        return math.hypot(*(self.position[:3] - self.render.camera.position[:3]))

    def screen_projection(self, m):
        if self.moving:
            self.movement()

        self.renderable = (
            self.render.camera.cos_angle_between(
                self.position - self.render.camera.position
            )
            > self.render.camera.cos_fov
        )

        if self.renderable:
            position = self.position @ m
            position /= position[-1]
            position = position[:2]

            self.renderable = (
                position[0] > -100
                and position[0] < 2 * self.render.width
                and position[1] > -100
                and position[1] < 2 * self.render.height
            )

            self.projected = position

            self.distance = math.hypot(
                *(self.position[:3] - self.render.camera.position[:3])
            )

    def draw(self):
        if self.renderable:
            pg.gfxdraw.aacircle(
                self.render.parent.viewport,
                int(self.projected[0]),
                int(self.projected[1]),
                max(2, int(self.size / self.distance * math.sqrt(self.render.width * self.render.height) / 960)),
                pg.Color(self.colour),
            )
            pg.gfxdraw.filled_circle(
                self.render.parent.viewport,
                int(self.projected[0]),
                int(self.projected[1]),
                max(2, int(self.size / self.distance * math.sqrt(self.render.width * self.render.height) / 960)),
                pg.Color(self.colour),
            )


class PointlessLine:
    def __init__(self, render, point1_hash, point2_hash, parent):
        self.render = render
        self.point1_hash = point1_hash
        self.point2_hash = point2_hash
        self.parent = parent
        self.renderable = True

    def camera_distance(self):
        return (
            max(
                self.render.distance_tables[self.parent.toggle][self.point1_hash],
                self.render.distance_tables[self.parent.toggle][self.point1_hash],
            )
            + 1
        )

    def draw(self):
        # print(self.render.cos_angle_between_table[self.point1_hash], self.render.camera.cos_angle_between(self.render.points_table[self.point1_hash] - self.render.camera.position))
        cos_angle_between_1 = self.render.cos_tables[self.parent.toggle][self.point1_hash]
        cos_angle_between_2 = self.render.cos_tables[self.parent.toggle][self.point2_hash]
        self.renderable = (
            cos_angle_between_1 > self.render.camera.d_cos_fov
            and cos_angle_between_2 > self.render.camera.d_cos_fov
            and (
                cos_angle_between_1 > self.render.camera.cos_fov
                or cos_angle_between_2 > self.render.camera.cos_fov
            )
            and not self.parent.colour.a == 0
            and not self.parent.hidden
        )

        if self.renderable:
            p1 = self.render.projected_tables[self.parent.toggle][self.point1_hash]
            p2 = self.render.projected_tables[self.parent.toggle][self.point2_hash]
            # print(self.render.point_tables[self.parent.toggle][self.point1_hash], self.render.point_tables[self.parent.toggle][self.point2_hash])
            # print(p1, p2)
            d = (p2[0] - p1[0], p2[1] - p1[1])
            l = math.hypot(*d)
            sp = (
                -d[1] * self.parent.thickness / (2 * l),
                d[0] * self.parent.thickness / (2 * l),
            )

            UL = (p1[0] - sp[0], p1[1] - sp[1])
            UR = (p1[0] + sp[0], p1[1] + sp[1])
            BL = (p2[0] - sp[0], p2[1] - sp[1])
            BR = (p2[0] + sp[0], p2[1] + sp[1])

            colour = self.parent.colour
            if self.parent.fading:
                colour.a = int(self.parent.opacity)
            pg.gfxdraw.aapolygon(self.render.parent.viewport, (UL, UR, BR, BL), colour)
            pg.gfxdraw.filled_polygon(self.render.parent.viewport, (UL, UR, BR, BL), colour)


class MultiLine:
    def __init__(
        self,
        render,
        toggle,
        f,
        preset_args,
        segments,
        colour,
        thickness=2,
        length=None,
        min_segments=0,
        max_segments=9999,
        fading=False,
        duration=0,
        fading_function=lambda x: 1 - x,
        t_max = 1
    ):
        self.render = render
        self.toggle = toggle
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
        self.t_max = t_max

        if self.fading:
            self.fading_function = fading_function
            self.duration = duration
            self.creation_time = time.time()
            self.initial_opacity = self.colour.a

        self.generate_sublines(segments)

    def generate_sublines(self, segments):
        self.segments = segments
        self.sublines = []
        self.hash_start = len(self.render.point_tables[self.toggle])

        for i in range(self.segments + 1):
            t = self.t_max * i / self.segments  # TODO: stop overlapping at multiline join points
            p = np.array([*self.f(t, *self.preset_args), 1.0])
            self.render.point_tables[self.toggle] = np.append(self.render.point_tables[self.toggle], np.array([p]), axis=0)

            if i == self.segments:
                break

            self.sublines.append(
                PointlessLine(
                    self.render, self.hash_start + i, self.hash_start + i + 1, self
                )
            )
