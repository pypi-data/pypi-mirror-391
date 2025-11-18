from RUDLeg.settings.imports import *



class ButtonSimple:
    def __init__(self, x, y, w, h, app, img:pg.Surface|None=None, text="Write you text"):
        self.rect = pg.Rect(x, y, w, h)
        self.app = app

        self.img = img

        self.hovered = False
        self.clicked = False
        self.timer = 0


    def handler_event(self, event):
        pass


    def update(self, **kwargs):
        mouse_pos = pg.mouse.get_pos()

       
        self.hovered = self.rect.collidepoint((int(mouse_pos[0]), int(mouse_pos[1])))





class ButtonState(ButtonSimple):
    def __init__(self, x, y, w, h, app, game_state, img=None, text="Write you text"):
        super().__init__(x, y, w, h, app, img, text)

        self.game_state = game_state

    def handler_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1 and self.hovered:
                self.clicked = True
    
    def update(self, timer_gone, func_fade=None):
        mouse_pos = pg.mouse.get_pos()

        self.hovered = self.rect.collidepoint((int(mouse_pos[0]), int(mouse_pos[1])))

        if self.clicked:
            self.timer += self.app.delta_time
            if func_fade is not None: func_fade()

        if self.timer >= timer_gone:
            self.app.switch_scene(self.game_state)
    

    


class ButtonSwitch(ButtonSimple):
    pass





class ButtonChoose(ButtonSimple):
    pass


