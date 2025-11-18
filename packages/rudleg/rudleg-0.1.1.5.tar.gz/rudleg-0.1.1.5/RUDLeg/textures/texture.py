import pygame as pg
import moderngl as mgl
import glm
import os


#from path str to texture
def give_texture(path, ctx, filter="near"):
    if os.path.exists(path):
        surface = pg.transform.flip(pg.image.load(path).convert_alpha(), flip_x=False, flip_y=True)
        surface_data = pg.image.tobytes(surface, "RGBA")

        texture = ctx.texture(surface.get_size(), 4, surface_data)
        
        if filter == "near":
            texture.filter = (mgl.NEAREST, mgl.NEAREST)
        elif filter == "line":
            texture.filter = (mgl.LINEAR, mgl.LINEAR)

        return texture
    else:
        raise FileNotFoundError(f"Undefined path - {path}")
    

#from surface to texture

def give_surfture(surface: pg.Surface, ctx, filter="near"):
    surface = pg.transform.flip(surface, flip_y=True, flip_x=False)
    surface_data = pg.image.tobytes(surface, "RGBA")

    texture = ctx.texture(surface.get_size(), 4, surface_data)
    if filter == "near":
            texture.filter = (mgl.NEAREST, mgl.NEAREST)
    elif filter == "line":
            texture.filter = (mgl.LINEAR, mgl.LINEAR)

    return texture




def give_program(vertex_path, fragment_path, ctx):
    vertex_shader = read_shader_file(path=vertex_path)
    fragment_shader = read_shader_file(path=fragment_path)

    return ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)



def from_ndc_to_sdl(width, height) -> glm.mat4:
     return glm.mat4(
        glm.vec4(2.0/width, 0.0, 0.0, 0.0),
        glm.vec4(0.0, -2.0/height, 0.0, 0.0),
        glm.vec4(0.0, 0.0, 1.0, 0.0),
        glm.vec4(-1.0, 1.0, 0.0, 1.0)
    )
     




def subthat(which_pos: tuple, which_size: tuple, original_surface: pg.Surface):
    sub_surface = original_surface.subsurface(*which_pos, *which_size).copy()

    return sub_surface.convert_alpha()




#very usefull function
def read_shader_file(path):
    if os.path.exists(path):
        with open(path, "r", encoding="UTF-8") as f:
            return f.read()
        
    else:
        raise FileNotFoundError(f"Undefined path - {path}")