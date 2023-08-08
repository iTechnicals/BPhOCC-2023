import render.manager as render_manager
import twodim.manager as twodim_manager
import pygame as pg


class Application:
    def __init__(self, width, height, vp=[0, 0, 0, 0]):
        # vp_coords = left, right, top, bottom
        pg.init()
        self.width, self.height = width, height
        self.vp = vp
        self.FPS = 60
        self.screen = pg.display.set_mode((self.width, self.height), pg.RESIZABLE)
        self.viewport = pg.Surface((self.width, self.height))
        self.clock = pg.time.Clock()

        self.showing = "graph"

        self.blit = (self.width * vp[0], self.height * vp[2])
        self.viewport_width = self.width * (1 - vp[0] - vp[1])
        self.viewport_height = self.height * (1 - vp[2] - vp[3])

        self.render = render_manager.Render(self, self.width * (1 - sum(vp)), self.height)
        self.twodim_elements = twodim_manager.Manager(self)

    def update_viewport(self, left, right, top, bottom):
        self.blit = (self.width * left, self.height * top)
        self.viewport_width = self.width * (1 - right - left)
        self.viewport_height = self.height * (1 - top - bottom)
        self.render.update_resolution()
        self.twodim_elements.update_resolution()

    def update(self):
        if self.screen.get_size != (self.width, self.height):
            self.width, self.height = self.screen.get_size()
            self.update_viewport(*self.vp)
        self.render.width, self.render.height = (
            self.viewport_width,
            self.viewport_height,
        )

        [exit() for i in pg.event.get() if i.type == pg.QUIT]
        pg.display.set_caption(str(self.clock.get_fps()))
        pg.display.update()
        self.clock.tick(self.FPS)

        self.viewport.fill(pg.Color("#2C3040"))
        self.screen.fill(pg.Color("#2C3040"))

        if self.showing == "render":
            self.render.tick()
            self.twodim_elements.tick()
        else:
            self.twodim_elements.tick()
        self.screen.blit(self.viewport, self.blit)


app = Application(768, 400)

while True:
    app.update()
