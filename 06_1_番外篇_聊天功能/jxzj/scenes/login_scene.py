import pygame

from engine.gui import TextBox
from engine.sprite import Sprite
from engine.scene import Scene
from game_global import g


class LoginScene(Scene):
    def __init__(self, scene_id):
        super().__init__(scene_id=scene_id)
        self.bg = pygame.image.load('./img/Login.jpg')
        self.username_input = TextBox(150, 20, 350, 265)
        self.password_input = TextBox(150, 20, 350, 315, callback=self.cb_login)
        self.username_input.text = 'admin01'
        self.password_input.text = '123456'

    def cb_login(self, text):
        """
        密码框回车回调
        """
        username = self.username_input.text
        password = text
        g.client.login(username, password)

    def logic(self):
        """
        界面逻辑
        """

    def render(self):
        """
        渲染
        """
        Sprite.blit(g.screen, self.bg, 0, 0)
        self.username_input.draw(g.screen)
        self.password_input.draw(g.screen)

    def mouse_down(self, x, y, pressed):
        self.username_input.mouse_down(x, y, pressed)
        self.password_input.mouse_down(x, y, pressed)

    def mouse_up(self, x, y, pressed):
        pass

    def mouse_move(self, x, y):
        pass

    def key_down(self, event):
        self.username_input.safe_key_down(event)
        self.password_input.safe_key_down(event)
        print("keydown")
