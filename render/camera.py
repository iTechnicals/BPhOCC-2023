import pygame as pg
import numpy as np
import render.objects as objects
from render.matrices import *

class Camera:
    def __init__(self, render, position):
        self.render = render
        self.position = np.array([*position, 1.0])
        self.h_fov = math.pi / 3
        self.v_fov = self.h_fov * render.height / render.width
        self.cos_fov = math.cos(max(self.h_fov, self.v_fov))
        self.near_plane = 0.1
        self.far_plane = 100
        self.move_speed = 0.02
        self.zoom_speed = 0.7
        self.up_sign = 1

        
        self.control()
        self.matrix = self.translate_cob() @ self.rotate_cob()

    def control(self):
        moved = False

        fps = self.render.parent.clock.get_fps()
        fps = 60 if fps == 0 else fps

        self.r = math.hypot(*self.position[:3])

        angle_from_vertical = abs(self.position[2]/self.r)

        if angle_from_vertical > 0.9999:
            self.move_speed = 0
            self.position = np.array([-self.position[0]*2, -self.position[1]*2, self.position[2]/1.01, 1])
            self.up_sign *= -1
            self.move_speed = 0.1

        
        coords = pg.mouse.get_rel()
        if pg.mouse.get_pressed()[0]:
            self.position -= coords[0]*self.right*self.move_speed*math.sqrt(1-angle_from_vertical)*self.r/fps
            self.position += coords[1]*self.up*self.move_speed*self.r/fps
            moved = (coords != (0, 0))

        self.position *= self.r / math.hypot(*self.position[:3])


        key = pg.key.get_pressed()
        if key[pg.K_s]:
            self.position *= 1 + self.zoom_speed/fps
            moved = True
        if key[pg.K_w]:
            self.position /= 1 + self.zoom_speed/fps
            moved = True
        
        self.forward = -self.position / self.r; self.forward[-1] = 1
        self.right = np.array([-self.forward[1], self.forward[0], 0, 1]); self.right /= math.hypot(*self.right[:3]); self.right[-1] = 1
        self.up = self.up_sign*np.array([*np.cross(self.right[:3], self.forward[:3]), 1]); self.up /= math.hypot(*self.up[:3]); self.right[-1] = 1

        if moved:
            self.update_matrix()

    def camera_distance(self, object):
        if isinstance(object, objects.PointlessLine):
            return max(math.hypot(*(self.position[:3] - object.point1[:3])), math.hypot(*(self.position[:3] - object.point2[:3]))) + 1
        if isinstance(object, objects.Point):
            return math.hypot(*(self.position[:3] - object.position[:3]))
    
    def update_matrix(self):
        self.matrix = self.translate_cob() @ self.rotate_cob()
        self.render.m = self.matrix @ self.render.projection.matrix

    def translate_cob(self):
        x, y, z, w = self.position
        return np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 1],
            [0, 0, 1, 0],
            [-x, -y, -z, 1]
        ])

    def untranslate_cob(self):
        x, y, z, w = self.position
        return np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 1],
            [0, 0, 1, 0],
            [x, y, z, 1]
        ])

    def rotate_cob(self):
        rx, ry, rz, w = self.right
        fx, fy, fz, w = self.forward
        ux, uy, uz, w = self.up
        return np.array([
            [rx, ux, fx, 0],
            [ry, uy, fy, 0],
            [rz, uz, fz, 0],
            [0, 0, 0, 1]
        ])

    def cos_angle_between(self, v):
        dot = self.forward[0] * v[0] + self.forward[1] * v[1] + self.forward[2] * v[2]
        return dot / math.hypot(*v[:3])