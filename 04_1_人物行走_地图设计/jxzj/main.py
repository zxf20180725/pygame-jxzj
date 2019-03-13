import sys

import pygame

from core import Sprite, GameMap


class Game:
    def __init__(self, title, width, height, fps=60):
        """
        :param title: 游戏窗口的标题
        :param width: 游戏窗口的宽度
        :param height: 游戏窗口的高度
        :param fps: 游戏每秒刷新次数
        """
        self.title = title
        self.width = width
        self.height = height
        self.screen_surf = None
        self.fps = fps
        self.__init_pygame()
        self.__init_game()
        self.update()

    def __init_pygame(self):
        pygame.init()
        pygame.display.set_caption(self.title)
        self.screen_surf = pygame.display.set_mode([self.width, self.height])
        self.clock = pygame.time.Clock()

    def __init_game(self):
        self.hero = pygame.image.load('./img/character/hero.png').convert_alpha()
        self.map_bottom = pygame.image.load('./img/map/0.png').convert_alpha()
        self.map_top = pygame.image.load('./img/map/0_top.png').convert_alpha()
        self.game_map = GameMap(self.map_bottom, self.map_top, 0, 0)
        self.game_map.load_walk_file('./img/map/0.map')

    def update(self):
        while True:
            self.clock.tick(self.fps)
            # TODO:逻辑更新
            self.event_handler()
            # TODO:画面更新
            self.game_map.draw_bottom(self.screen_surf)
            Sprite.draw(self.screen_surf, self.hero, 100, 100, 0, 0)
            Sprite.draw(self.screen_surf, self.hero, 210, 120, 1, 1)
            Sprite.draw(self.screen_surf, self.hero, 300, 100, 2, 2)
            self.game_map.draw_top(self.screen_surf)
            self.game_map.draw_grid(self.screen_surf)
            pygame.display.update()

    def event_handler(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()


if __name__ == '__main__':
    Game("间隙之间", 640, 480)
