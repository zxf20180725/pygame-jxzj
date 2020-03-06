import pygame

from core import GameMap
from engine.gui import TextBox
from engine.scene import Scene
from engine.sprite import Sprite, draw_src_outline_text
from game_global import g


class GameScene(Scene):
    def __init__(self, scene_id):
        super().__init__(scene_id=scene_id)
        self.hero = pygame.image.load('./img/character/hero.png').convert_alpha()
        self.map_bottom = pygame.image.load('./img/map/0.png').convert_alpha()
        self.map_top = pygame.image.load('./img/map/0_top.png').convert_alpha()
        self.game_map = GameMap(self.map_bottom, self.map_top, 0, 0)
        self.game_map.load_walk_file('./img/map/0.map')
        self.role = None
        self.other_player = []
        self.chat_box = pygame.image.load('./img/chat_box.png').convert_alpha()
        self.chat_input = TextBox(145, 20, 75, 550, color=(0, 0, 0), no_bg=True, callback=self.cb_send_chat)
        self.chat_history = []

    def cb_send_chat(self, text):
        # 不予许发空字符串
        if not text:
            return
        g.client.chat(text)
        self.chat_input.reset()

    def logic(self):
        self.role.logic()
        for player in self.other_player:
            player.logic()
        self.game_map.roll(self.role.x, self.role.y)

    def render(self):
        self.game_map.draw_bottom(g.screen)
        self.role.draw(g.screen, self.game_map.x, self.game_map.y)
        # 绘制其他玩家
        for player in self.other_player:
            player.draw(g.screen, self.game_map.x, self.game_map.y)
        self.game_map.draw_top(g.screen)
        # 绘制聊天记录
        for index, history in enumerate(self.chat_history):
            draw_src_outline_text(g.screen, 0, 380 + index * 25, history, g.font, (255, 0, 0), (0, 0, 0))
        # 绘制聊天框
        Sprite.blit(g.screen, self.chat_box, 0, 571 - self.chat_box.get_height())
        self.chat_input.draw(g.screen)
        # self.game_map.draw_grid(g.screen)

    def mouse_down(self, x, y, pressed):
        if self.chat_input.mouse_down(x, y, pressed):
            return

        mx = int((x - self.game_map.x) / 32)
        my = int((y - self.game_map.y) / 32)
        # 寻路
        self.role.find_path(self.game_map, (mx, my))

    def mouse_move(self, x, y):
        pass

    def mouse_up(self, x, y, pressed):
        pass

    def key_down(self, event):
        self.chat_input.safe_key_down(event)
