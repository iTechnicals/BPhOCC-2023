import render.manager as render_manager
import twodim.manager as twodim_manager
import plotter.manager as plotter_manager
import pygame as pg


class Application:
    def __init__(self, width, height, vp=[0, 0, 0, 0]):
        # vp_coords = left, right, top, bottom
        pg.init()
        self.width, self.height = width, height
        self.vp = vp
        self.FPS = 60
        self.screen = pg.display.set_mode((0, 0), pg.RESIZABLE, pg.FULLSCREEN)
        self.viewport = pg.Surface((self.width, self.height))
        self.clock = pg.time.Clock()
        self.mod = 0

        self.showing = "graph"

        self.blit_coords = (self.width * vp[0], self.height * vp[2])
        self.viewport_width = self.width * (1 - vp[0] - vp[1])
        self.viewport_height = self.height * (1 - vp[2] - vp[3])

        self.render = render_manager.Render(self, self.width * (1 - sum(vp)), self.height)
        self.twodim_elements = twodim_manager.Manager(self)
        self.plotter = plotter_manager.Plotter(self, (0.1, 0.9), (0.9, 0.1))

    def update_viewport(self, left, right, top, bottom):
        self.blit_coords = (self.width * left, self.height * top)
        self.viewport_width = self.width * (1 - right - left)
        self.viewport_height = self.height * (1 - top - bottom)
        self.viewport = pg.transform.scale(self.viewport, (self.viewport_width, self.viewport_height))
        self.render.width, self.render.height = self.viewport_width, self.viewport_height
        self.render.update_resolution()
        self.twodim_elements.update_resolution()
        self.plotter.update_resolution()

    def update(self):
        if self.screen.get_size() != (self.width, self.height):
            self.width, self.height = self.screen.get_size()
            self.update_viewport(*self.vp)

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
            self.plotter.tick()
            self.twodim_elements.tick()

        self.screen.blit(self.viewport, self.blit_coords)


app = Application(768, 400)

while True:
    app.update()
