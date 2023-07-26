import render.manager as manager
import pygame as pg

class Application:
    def __init__(self, width, height, vp = (0, 0)):
        # vp_coords = left, right
        pg.init()
        self.width, self.height = width, height
        self.vp = vp
        self.FPS = 60
        self.screen = pg.display.set_mode((self.width, self.height), pg.RESIZABLE)
        self.clock = pg.time.Clock()
        self.render = manager.Render(self, self.width*(1 - sum(vp)), self.height)
        self.tot = 0
        self.i = 0

    def update_viewport(self, left, right):
        self.viewport_right = right*self.width
        self.viewport_width = self.width*(1 - right - left)
        self.viewport_height = self.height
        self.render.update_resolution()

    def update(self):
        if self.screen.get_size != (self.width, self.height):
            self.width, self.height = self.screen.get_size()
            self.update_viewport(*self.vp)
        self.render.width, self.render.height = self.viewport_width, self.viewport_height

        [exit() for i in pg.event.get() if i.type == pg.QUIT]
        pg.display.set_caption(str(self.clock.get_fps()))
        pg.display.update()
        self.clock.tick(self.FPS)
        
        self.screen.fill(pg.Color('#232633'))
        self.screen.blit(self.render.tick(), (self.viewport_right, 0))

        
app = Application(768, 400)

while True:
    # app.vp = ((abs(0.2 - (pg.time.get_ticks() % 2000)/5000)), (abs(0.2 - (pg.time.get_ticks() % 2000)/5000)))
    app.update()
