import sys

import pygame

from core import GameMap, CharWalk


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
        """
        pygame相关的初始化操作
        """
        pygame.init()
        pygame.display.set_caption(self.title)
        self.screen_surf = pygame.display.set_mode([self.width, self.height])
        self.clock = pygame.time.Clock()

    def __init_game(self):
        """
        我们游戏的一些初始化操作
        """
        self.hero = pygame.image.load('./img/character/hero.png').convert_alpha()
        self.map_bottom = pygame.image.load('./img/map/0.png').convert_alpha()
        self.map_top = pygame.image.load('./img/map/0_top.png').convert_alpha()
        self.game_map = GameMap(self.map_bottom, self.map_top, 0, 0)
        self.game_map.load_walk_file('./img/map/0.map')
        self.role = CharWalk(self.hero, 48, CharWalk.DIR_DOWN, 5, 10)

    def update(self):
        while True:
            self.clock.tick(self.fps)
            # 逻辑更新
            self.role.logic()
            self.event_handler()
            self.game_map.roll(self.role.x, self.role.y)
            # 画面更新
            self.game_map.draw_bottom(self.screen_surf)
            self.role.draw(self.screen_surf, self.game_map.x, self.game_map.y)
            self.game_map.draw_top(self.screen_surf)
            self.game_map.draw_grid(self.screen_surf)
            pygame.display.update()

    def event_handler(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                mx = int((mouse_x - self.game_map.x) / 32)
                my = int((mouse_y - self.game_map.y) / 32)
                # 寻路
                self.role.find_path(self.game_map, (mx, my))


if __name__ == '__main__':
    Game("间隙之间", 640, 480)
