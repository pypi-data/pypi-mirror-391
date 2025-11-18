import glm
import pygame as pg


class CameraBase:
    def __init__(self, app):
        self.app = app
        self.offset = glm.vec2(0, 0)

        self.vision = None

    def scroll(**kwargs):
        pass

    def debug_render(self, **kwargs):
        pass



class RegionCamera:
    def __init__(self, app):
        self.app = app
        self.region_rect = pg.FRect(0, 200, 100, 600)

        self.offset = glm.vec2(0.0, 0.0)
        self.vision = pg.FRect(0, 0, 0, 0)

    def scroll(self, target_rect, surface, **kwargs):
        surface = surface if surface else self.app.screen

        min_x = kwargs.get("min_x", 0)
        min_y = kwargs.get("min_y", 0)

        max_x = kwargs.get("max_x", 2000)
        max_y = kwargs.get("max_y", 2000)

        velocity = kwargs.get("velocity", glm.vec2(150, 0))


        if not self.region_rect.contains(target_rect):
            if target_rect.left < self.region_rect.left:
                self.region_rect.x -= velocity.x * self.app.delta_time
            elif target_rect.right > self.region_rect.right:
                self.region_rect.x += velocity.x * self.app.delta_time

            if target_rect.top < self.region_rect.top:
                self.region_rect.y -= velocity.y * self.app.delta_time
            elif target_rect.bottom > self.region_rect.bottom:
                self.region_rect.y += velocity.y * self.app.delta_time



        self.vision.x = self.offset.x - 400
        self.vision.y = self.offset.y - 250
        self.vision.w = surface.get_width()
        self.vision.h = surface.get_height()

     
        self.offset.x = max(min_x, min(self.region_rect.x - surface.get_width() // 2 + 500, max_x))
        self.offset.y = max(min_y, min(self.region_rect.y - surface.get_height() // 2 + 200, max_y))




