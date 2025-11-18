import pygame as pg
import glm
from abc import ABC, abstractmethod
  



class MainObject(ABC):

    @abstractmethod
    def update(**kwargs):
        pass

    @abstractmethod
    def handler_event(**kwargs):
        pass


    @abstractmethod
    def render(**kwargs):
        pass



class Converter2D(ABC):
    @abstractmethod
    def build_map(self):
        pass

    @abstractmethod
    def get_objects(self):
        pass






class Kinematic2D(ABC):
    @abstractmethod
    def __init__(self, x, y, w, h, app):
        self.app = app

        self.rect = pg.FRect(x, y, w, h)
        self.velocity = glm.vec2(0.0, 0.0)


    def init_on(self):
        pass

    def set_obj(self, **kwargs):
        pass

    def update(self, **kwargs):
        pass

    
    def handler_event(self, event):
        pass

    
    def collision(self, **kwargs):
        pass


    def collision_x(self, **kwargs):
        pass


    def collision_y(self, **kwargs):
        pass


    def __repr__(self):
        return "That Kinematic2D object"




class Static2D(ABC):
    @abstractmethod
    def __init__(self, x, y, w, h, app):
        self.app = app

        self.rect = pg.FRect(x, y, w, h)

    def init_on(self):
        pass


    def set_obj(self, **kwargs):
        pass



    def update(self, **kwargs):
        pass

    
    def handler_event(self, event):
        pass


    def collision(self, **kwargs):
        pass


    def collision_x(self, **kwargs):
        pass


    def collision_y(self, **kwargs):
        pass


    def __repr__(self):
        return "That Static2D object"



