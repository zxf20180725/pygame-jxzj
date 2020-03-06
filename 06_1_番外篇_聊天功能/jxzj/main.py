import sys
import socket

import pygame

from core import GameMap, CharWalk
from engine.scene import SceneManager
from scenes.game_scene import GameScene
from scenes.login_scene import LoginScene
from game_global import g
from net import Client


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
        g.screen = self.screen_surf
        g.font = pygame.font.SysFont('microsoftyaheimicrosoftyaheiui', 16)
        self.clock = pygame.time.Clock()

    def __init_game(self):
        """
        我们游戏的一些初始化操作
        """
        # 创建场景管理器
        g.scene_mgr = SceneManager()
        # 创建登录场景
        login_scene = LoginScene(1)
        # 创建游戏场景
        game_scene = GameScene(2)
        g.scene_mgr.add(login_scene)
        g.scene_mgr.add(game_scene)
        # 与服务端建立连接
        s = socket.socket()
        s.connect(('47.100.44.206', 8712))  # 与服务器建立连接
        self.client = Client(s, game_scene)
        g.client = self.client  # 把client赋值给全局对象上，以便到处使用

    def update(self):
        while True:
            self.clock.tick(self.fps)
            # 输入事件处理
            scene = g.scene_mgr.find_scene_by_id(g.scene_id)
            self.event_handler()
            scene.logic()
            scene.render()
            pygame.display.update()

    def event_handler(self):
        x, y = pygame.mouse.get_pos()
        scene = g.scene_mgr.find_scene_by_id(g.scene_id)
        for event in pygame.event.get():
            pressed = pygame.mouse.get_pressed()
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEMOTION:
                scene.mouse_move(x, y)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                scene.mouse_down(x, y, pressed)
            elif event.type == pygame.MOUSEBUTTONUP:
                scene.mouse_up(x, y, pressed)
            elif event.type == pygame.KEYDOWN:
                scene.key_down(event)

        # for event in pygame.event.get():
        #     if event.type == pygame.QUIT:
        #         sys.exit()
        #     elif event.type == pygame.MOUSEBUTTONDOWN:
        #         mouse_x, mouse_y = pygame.mouse.get_pos()



if __name__ == '__main__':
    Game("间隙之间", 800, 571)
