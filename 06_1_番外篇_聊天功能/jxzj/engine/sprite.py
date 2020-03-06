import pygame


class Sprite:
    @staticmethod
    def draw(dest, source, x, y, cell_x, cell_y, cell_w=32, cell_h=32):
        """
        绘制精灵图中，指定x,y的图像
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
        dest.blit(source, (x, y), (cell_x * cell_w, cell_y * cell_h, cell_w, cell_h))

    @staticmethod
    def draw_rect(dest, source, x, y, src_x, src_y, w, h):
        dest.blit(source, (x, y), (src_x, src_y, w, h))

    @staticmethod
    def blit(dest, source, x, y):
        """
        绘制原图
        """
        dest.blit(source, (x, y))

    @staticmethod
    def blit_w(dest, source, x, y, percent):
        """
        按宽度百分比绘制
        percent:[0,1]
        """
        dest.blit(source, (x, y), (0, 0, int(source.get_width() * percent), source.get_height()))

    @staticmethod
    def blit_alpha(target, source, x, y, opacity, rect=None):
        """
        绘制半透明图片（解决带alpha通道的surface的set_alpha不起作用的问题）
        """
        temp = pygame.Surface((source.get_width(), source.get_height())).convert()
        if rect:
            rect[0] = -rect[0]
            rect[1] = -rect[1]
            temp.blit(target, (-x, -y), rect)
            temp.blit(source, (0, 0), rect)
            temp.set_alpha(opacity)
            target.blit(temp, (x, y), rect)
        else:
            temp.blit(target, (-x, -y))
            temp.blit(source, (0, 0))
            temp.set_alpha(opacity)
            target.blit(temp, (x, y))

    @staticmethod
    def draw_alpha(dest, source, x, y, cell_x, cell_y, cell_w=32, cell_h=32, opacity=0):
        """
        有bug，不可用
        """
        print((cell_x * cell_w, cell_y * cell_h, cell_w, cell_h))
        Sprite.blit_alpha(dest, source, x, y, opacity, [cell_x * cell_w, cell_y * cell_h, cell_w, cell_h])

    @staticmethod
    def subsurface(source, cell_x, cell_y, cell_w=32, cell_h=32):
        """
        返回子表面
        """
        return source.subsurface([cell_x * cell_w, cell_y * cell_h, cell_w, cell_h])

    @staticmethod
    def draw_fill_rect(target, x, y, w, h, rgba):
        """
        画半透明矩形
        """
        surface = pygame.Surface((w, h), pygame.SRCALPHA)
        surface.fill(rgba)
        target.blit(surface, (x, y))


def draw_text(dest, x, y, text, font, rgb):
    """
    绘制文字（取中心点绘制）
    """
    surface = font.render(text, True, rgb)
    w = surface.get_width()
    Sprite.blit(dest, surface, x - int(w / 2), y)


def draw_src_text(dest, x, y, text, font, rgb):
    """
    绘制文字
    """
    surface = font.render(text, True, rgb)
    Sprite.blit(dest, surface, x, y)


def draw_outline_text(dest, x, y, text, font, inner_rgb, outter_rgb):
    """
    绘制带边框的文字
    """
    sur_inner = font.render(text, True, inner_rgb)
    sur_outter = font.render(text, True, outter_rgb)
    w = sur_inner.get_width()
    Sprite.blit(dest, sur_outter, x - int(w / 2) + 1, y)
    Sprite.blit(dest, sur_outter, x - int(w / 2) - 1, y)
    Sprite.blit(dest, sur_outter, x - int(w / 2), y + 1)
    Sprite.blit(dest, sur_outter, x - int(w / 2), y - 1)
    Sprite.blit(dest, sur_inner, x - int(w / 2), y)


def draw_src_outline_text(dest, x, y, text, font, inner_rgb, outter_rgb):
    """
    绘制带边框的文字
    """
    sur_inner = font.render(text, True, inner_rgb)
    sur_outter = font.render(text, True, outter_rgb)
    Sprite.blit(dest, sur_outter, x + 1, y)
    Sprite.blit(dest, sur_outter, x - 1, y)
    Sprite.blit(dest, sur_outter, x, y + 1)
    Sprite.blit(dest, sur_outter, x, y - 1)
    Sprite.blit(dest, sur_inner, x, y)


def draw_rect_text(dest, color, text, font, x, y, width):
    lineWidth = 0
    lastSubStrIndex = 0
    lineHeight = font.get_linesize()  # 行高=字体高度+行距
    for i in range(0, len(text)):
        lineWidth += font.size(text[i])[0]
        if lineWidth > width or text[i] == '\n':
            draw_src_text(dest, x, y, text[lastSubStrIndex:i], font, color)
            y += lineHeight
            lineWidth = 0
            if text[i] == '\n':
                lastSubStrIndex = i + 1
            else:
                lastSubStrIndex = i

        if i == len(text) - 1:
            draw_src_text(dest, x, y, text[lastSubStrIndex:i + 1], font, color)
