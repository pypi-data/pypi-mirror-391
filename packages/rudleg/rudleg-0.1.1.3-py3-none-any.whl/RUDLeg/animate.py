import pygame as pg
from RUDLeg.textures.texture import give_surfture


class DecursiveAnimation2D:
    pass


class RecursiveAnimation2D:
    def __init__(self, frames: list, ctx, repeat=True, fps=10):
        self.frames_texture = [give_surfture(frame, ctx=ctx) for frame in frames]
        self.index = 0

    
        self.repeat = repeat
        self.duration = 1000 / fps
        self.last_time = pg.time.get_ticks()
        


    def update(self, paused=False):
        now = pg.time.get_ticks()

        if now - self.last_time >= self.duration:
            if not paused:
                self.index += 1

            if len(self.frames_texture) <= self.index:
                if self.repeat:
                    self.index = 0
                else:
                    self.index = len(self.frames_texture) - 1


            self.last_time = now

        
    def get_texture(self):
        return self.frames_texture[self.index]
    
