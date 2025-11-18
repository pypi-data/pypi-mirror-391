


def scene_code(dir_name: str):
    scene_code = f"from {dir_name}.scenes.ExampleScene1 import MyScene1\n"\
             f"from {dir_name}.scenes.ExampleScene2 import MyScene2\n"\
             "\n"\
             "class SceneManager:\n" \
             "\tdef __init__(self, app):\n" \
             "\n"\
             "\t\tself.app = app\n" \
             "\t\tself.state = None\n"\
             "\t\tself.app.data_read['game-state'] = 'scene-1'\n"\
             "\n"\
             "\t\t#That you can register a new scene\n"\
             "\t\tself.scene_dict = {'scene-1': lambda: MyScene1(app=app), 'scene-2': lambda: MyScene2(app=app)}\n"\
             "\t\tself.current_scene = self.scene_dict.get(self.app.data_read['game-state'])()"\
             "\n" \
             "\n"\
             "\t#that method need only for update logic and physic functions\n"\
             "\tdef update(self):\n" \
             "\t\tstate = self.app.data_read['game-state']\n"\
             "\t\tif self.state != state:\n"\
             "\t\t\tself.current_scene = self.scene_dict.get(self.app.data_read['game-state'])()\n"\
             "\t\t\tself.state = state\n"\
             "\n"\
             "\t\tself.current_scene.update()\n" \
             "\n" \
             "\t#that method only for handler events\n"\
             "\tdef handler_event(self, event):\n"\
             "\t\tself.current_scene.handler_event(event=event)\n"\
             "\n"\
             "\t#in this method you render objects\n"\
             "\tdef render(self, **kwargs):\n" \
             "\t\tself.current_scene.render()"
    return scene_code







example_code_1 = "class MyScene1:\n" \
                 "\tdef __init__(self, app):\n" \
                 "\t\tself.app = app\n" \
                 "\n" \
                 "\tdef update(self, **kwargs):\n" \
                 "\t\tpass\n" \
                 "\n" \
                 "\tdef handler_event(self, event):\n" \
                 "\t\tpass\n" \
                 "\n" \
                 "\tdef render(self, **kwargs):\n" \
                 "\t\tpass"








example_code_2 = "class MyScene2:\n" \
                 "\tdef __init__(self, app):\n" \
                 "\t\tself.app = app\n" \
                 "\n" \
                 "\tdef update(self, **kwargs):\n" \
                 "\t\tpass\n" \
                 "\n" \
                 "\tdef handler_event(self, event):\n" \
                 "\t\tpass\n" \
                 "\n" \
                 "\tdef render(self, **kwargs):\n" \
                 "\t\tpass"


test_code_cpu = "import pygame as pg\n" \
            "import os\n"\
            "\n" \
            "pg.init()\n" \
            "screen = pg.display.set_mode((800, 600), flags=0)\n" \
            "pg.display.set_icon(pg.image.load(os.path.join('RudlEngine', 'RudlAssets', 'stuff', 'icon.png')).convert_alpha())\n"\
            "pg.display.set_caption('RudlEngine: TestFile')\n" \
            "clock = pg.time.Clock()\n" \
            "\n" \
            "\n" \
            "\n" \
            "run = True\n" \
            "while run:\n" \
            "\tdelta_time = min(clock.tick(60) / 1000.0, 0.05)\n"\
            "\tscreen.fill((255, 255, 255))\n"\
            "\tfor event in pg.event.get():\n" \
            "\t\tif event.type == pg.QUIT:\n" \
            "\t\t\trun = False\n" \
            "\n" \
            "\tpg.display.flip()\n" \
            "pg.quit()\n"


test_code_gpu = code = \
                "import pygame as pg\n" \
                "import moderngl\n" \
                "import numpy as np\n" \
                "\n" \
                "pg.init()\n" \
                "pg.display.set_mode((800, 600), pg.OPENGL | pg.DOUBLEBUF)\n" \
                "ctx = moderngl.create_context()\n" \
                "\n" \
                "prog = ctx.program(\n" \
                "    vertex_shader='''\n" \
                "        #version 330\n" \
                "        in vec2 in_vert;\n" \
                "        void main() { gl_Position = vec4(in_vert, 0.0, 1.0); }\n" \
                "    ''',\n" \
                "    fragment_shader='''\n" \
                "        #version 330\n" \
                "        out vec4 f_color;\n" \
                "        void main() { f_color = vec4(1.0, 0.0, 0.0, 1.0); }\n" \
                "    '''\n" \
                ")\n" \
                "\n" \
                "vbo = ctx.buffer(np.array([\n" \
                "    -0.5, -0.5,\n" \
                "     0.5, -0.5,\n" \
                "     0.0,  0.5\n" \
                "], dtype='f4').tobytes())\n" \
                "\n" \
                "vao = ctx.vertex_array(prog, [(vbo, '2f', 'in_vert')])\n" \
                "\n" \
                "clock = pg.time.Clock()\n" \
                "running = True\n" \
                "while running:\n" \
                "\tfor e in pg.event.get():\n" \
                "\t\tif e.type == pg.QUIT:\n" \
                "\t\t\trunning = False\n" \
                "\n" \
                "\tctx.clear(0.1, 0.1, 0.1)\n" \
                "\tvao.render(moderngl.TRIANGLES)\n" \
                "\tpg.display.flip()\n" \
                "\tclock.tick(60)\n" \
                "\n" \
                "pg.quit()\n"









example_vert = "#version 330 core\n" \
                "layout(location = 0) in vec2 in_vert;\n" \
                "layout(location = 1) in vec2 in_coord;\n" \
                "\n" \
                "out vec2 uv;\n" \
                "\n" \
                "uniform vec2 camera_offset;\n" \
                "uniform vec2 pos;\n" \
                "uniform vec2 scale;\n" \
                "\n" \
                "void main(){\n" \
                "\tuv = in_coord;\n" \
                "\n" \
                "\tvec2 position = in_vert * scale;\n" \
                "\tgl_Position = vec4(position + pos - camera_offset, 0.0, 1.0);\n" \
                "}"


example_frag = "#version 330 core\n" \
                "in vec2 uv;\n" \
                "\n" \
                "out vec4 fragColor;\n" \
                "\n" \
                "uniform sampler2D tex;\n"\
                "void main(){\n" \
                "\t\n" \
                "\tfragColor = texture(tex, uv);  \n" \
                "\n" \
                "}"


example_data = '{\n'\
  '\t"window-size": [\n'\
  '\t\t800,\n'\
  '\t\t600\n'\
  '\t],\n'\
  '\t"fps": 90,\n'\
  '\t"game-state": "scene-1",\n'\
  '\t"need-to-save": true\n'\
'}'\



manager =   'from RUDLeg.core_magic.ExecuteCommand import task_run\n' \
            'import sys\n' \
            '\n' \
            'def main():\n' \
            '\n' \
            '\tUse that command if you don not know:\n'\
            '\t\tpy manager.py help : shows list of command promt\n'\
            '\t\tpy manager.py create <config-name> : create game_dev config'\
            '\tOther command you can learn in documentation. GoodLuck'\
            '\n' \
            '\ttask_run(sys.argv)\n' \
            '\n' \
            'if __name__ == "__main__":\n' \
            '\tmain()'






def locate_danger(dir_name):
    from RUDLeg.exceptions import ProhibitionError
    from pathlib import Path

    folder = Path(dir_name)
    bad_expressions = ["os.remove", "os.rename", "os.environ", "os.system", "os.rmdir", "os.chdir", 
                       "os.walk", "exec", "sys.modules", "sys.path", "sys.settrace", "sys.setprofile", "subprocces"]


    some_writen = ""
    paths = []
    for file in folder.rglob("*.py"):
        paths.append(file)

    for path in paths:
        with open(path, "r", encoding="UTF-8") as f:
            some_writen = f.read()

        for bad_expression in bad_expressions:
            if bad_expression in some_writen:
                raise ProhibitionError(f"That expression: '{bad_expression}' has in your file: '{path}'. Please delete that.")
    
    
    return 0


def locate_danger_from_file(filename):
    from RUDLeg.exceptions import ProhibitionError
    bad_expressions = ["os.remove", "os.rename", "os.environ", "os.system", "os.rmdir", "os.chdir", 
                       "os.walk", "exec", "sys.modules", "sys.path", "sys.settrace", "sys.setprofile", "subprocces"]

    some_writen = ""

    with open(filename, "r", encoding="UTF-8") as f:
        some_writen = f.read()

    for bad_expression in bad_expressions:
        if bad_expression in some_writen:
            raise ProhibitionError(f"That expression: '{bad_expression}'. Please delete that.")



