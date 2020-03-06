import pygame
from pygame.surface import Surface


class Animation:
    """
    动画类
    """

    def __init__(self, x, y, img, dw, dh, time, loop, frame_range, frame_callback=None, done_callback=None, fps=60,
                 need_blend=False, **kwargs):
        """
        :param x:绘制动画的中心点（不是左上角）
        :param y:绘制动画的中心点（不是左上角）
        :param img:序列帧图片
        :param dw:单位宽度
        :param dh:单位高度
        :param time:动画播放时长,单位毫秒
        :param loop:否是循环播放
        :param frame_range:动画帧范围,第一帧为0，比如[0,3]为4帧 [1,3]为3帧
        :param frame_callback:帧回调
        :param done_callback:完成回调
        """
        self.x = x
        self.y = y
        self.img = img
        self.time = time
        self.need_blend = need_blend
        # 一共多少帧
        self.frame_range = frame_range
        self.frame = frame_range[1] - frame_range[0] + 1
        self.dw = dw
        self.dh = dh
        self.speed = int(time / self.frame)
        self.loop = loop
        self.least_once = False  # 动画是否至少播放了一次
        self.frame_callback = frame_callback
        self.done_callback = done_callback
        # 精灵图的行和列
        self.row = int(self.img.get_height() / self.dh)
        self.col = int(self.img.get_width() / self.dw)
        self.current_frame = self.frame_range[0]  # 当前帧
        self.frame_count = int(self.speed / (1000 / fps))  # 需要等待几次主循环才切换1帧
        self.current_count = self.frame_range[0] * self.frame_count  # 当前计数

        if self.frame_count < 1:
            self.frame_count = 1

    def update(self):
        last_frame = self.current_frame
        self.current_count += 1
        self.current_frame = int(self.current_count / self.frame_count)
        if self.current_frame > self.frame_range[1]:
            # 播放完成
            self.current_frame = self.frame_range[0]
            self.current_count = self.frame_range[0] * self.frame_count
            self.least_once = True
            # 帧回调
            if self.frame_callback:
                self.frame_callback(last_frame)
            # 完成回调
            if self.done_callback:
                self.done_callback(last_frame)
        else:
            # 播放中
            # 每个动画帧回调，而不是每个主循环回调
            if last_frame != self.current_frame and self.frame_callback:
                self.frame_callback(last_frame)

    def draw(self, surface):
        """
        绘图,把x,y作为中心点绘制
        :param surface: 目标surface
        """
        dest_x = self.x - self.dw / 2
        dest_y = self.y - self.dh / 2
        cell_x = self.current_frame % self.col
        cell_y = int(self.current_frame / self.col)
        self.draw_cell(surface, self.img, dest_x, dest_y, cell_x, cell_y, self.dw, self.dh)

    def blend_draw(self, surface, blend_type):
        """
        带alpha混合的draw
        """
        dest_x = self.x - self.dw / 2
        dest_y = self.y - self.dh / 2
        cell_x = self.current_frame % self.col
        cell_y = int(self.current_frame / self.col)
        self.draw_cell(surface, self.img, dest_x, dest_y, cell_x, cell_y, self.dw, self.dh, blend_type)

    def draw_src(self, surface, x, y):
        """
        绘图，把x，y作为左上角绘制
        """
        cell_x = self.current_frame % self.col
        cell_y = int(self.current_frame / self.col)
        self.draw_cell(surface, self.img, x, y, cell_x, cell_y, self.dw, self.dh)

    def reset(self):
        """
        重置动画
        """
        self.current_frame = 0
        self.current_count = 0
        self.least_once = False

    @staticmethod
    def draw_cell(dest, source, x, y, cell_x, cell_y, cell_w=32, cell_h=32, blend_type=0):
        """
        绘制精灵图中指定x,y的图像
        :param dest: surface类型，要绘制到的目标surface
        :param source: surface类型，来源surface
        :param x: 绘制图像在dest中的坐标
        :param y: 绘制图像在dest中的坐标
        :param cell_x: 在精灵图中的格子坐标
        :param cell_y: 在精灵图中的格子坐标
        :param cell_w: 单个精灵的宽度
        :param cell_h: 单个精灵的高度
        :return:
        """
        dest.blit(source, (x, y), (cell_x * cell_w, cell_y * cell_h, cell_w, cell_h), special_flags=blend_type)


class Animator:
    """
    动画管理类
    """

    def __init__(self, surface):
        """
        :param surface: 动画显示的目标surface(一般是窗口surface)
        """
        self.surface = surface
        self.animations = []  # 存储着当前的动画

    def update(self):
        """
        动画管理类逻辑更新
        """
        for animation in self.animations[::-1]:
            animation.update()
            # 动画播放完成，删除动画
            if not animation.loop and animation.least_once:
                self.animations.remove(animation)

    def draw(self):
        """
        渲染各个动画
        """
        for animation in self.animations:
            if animation.need_blend:
                animation.blend_draw(self.surface, pygame.BLEND_ADD)
            else:
                animation.draw(self.surface)

    def add(self, x, y, img, dw, dh, time, loop, frame_range, frame_callback=None, done_callback=None):
        """
        添加一个动画
        :param x:绘制动画的中心点（不是左上角）
        :param y:绘制动画的中心点（不是左上角）
        :param img:序列帧图片
        :param dw:单位宽度
        :param dh:单位高度
        :param time:动画播放时长，单位毫秒
        :param loop:否是循环播放
        :param frame_range:动画帧范围
        :param frame_callback:帧回调
        :param done_callback:完成回调
        """

        animation = Animation(x, y, img, dw, dh, time, loop, frame_range, frame_callback, done_callback)
        self.animations.insert(0, animation)
        self.animations.sort(key=lambda obj: obj.y)

    def add_ani(self, *animations):
        for ani in animations:
            self.animations.insert(0, ani)
        self.animations.sort(key=lambda obj: obj.y)

    def clear(self):
        """
        清空所有动画
        """
        self.animations = []


class Fade:
    """
    淡出淡入
    """

    def __init__(self, dest):
        self.sw = False  # 开关，是否启动淡入淡出
        self.callback = None  # 回调函数
        self.state = 0  # 当前状态
        self.speed = 5
        self.alpha = 0
        self.dest = dest
        self.surface = Surface((640, 480))
        self.surface.fill((0, 0, 0))
        self.surface.set_alpha(self.alpha)

    def logic(self):
        if not self.sw:
            return

        if self.state == 0:  # 第一阶段，淡出
            self.alpha += self.speed
            if self.alpha >= 255:
                self.alpha = 255
                if self.callback:
                    self.callback()
                self.state = 1

        elif self.state == 1:  # 第二阶段，淡入
            self.alpha -= self.speed
            if self.alpha <= 0:
                self.sw = False

        self.surface.set_alpha(self.alpha)

    def draw(self):
        if not self.sw:
            return
        self.dest.blit(self.surface, (0, 0))

    def start(self, callback=None):
        self.reset()
        self.sw = True
        self.callback = callback

    def reset(self):
        self.state = 0  # 当前状态
        self.alpha = 0
