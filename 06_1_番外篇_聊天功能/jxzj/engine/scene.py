from engine.gui import Button


class Scene:
    """
    游戏场景：
        gui.py下的所有控件都交由scene渲染
    """

    def __init__(self, *args, **kwargs):
        self.scene_id = kwargs['scene_id']  # 场景id
        self.btn_list = []  # 按钮列表

    def logic(self):
        """
        逻辑
        """
        raise NotImplementedError

    def render(self):
        """
        渲染
        """
        raise NotImplementedError

    def mouse_down(self, x, y, pressed):
        """
        鼠标按下
        """
        raise NotImplementedError

    def mouse_move(self, x, y):
        """
        鼠标移动
        """
        raise NotImplementedError

    def mouse_up(self, x, y, pressed):
        """
        鼠标弹起
        """
        raise NotImplementedError

    def key_down(self, event):
        """
        键盘按下
        """
        raise NotImplementedError

    def bind(self, obj):
        if isinstance(obj, Button):
            self.btn_list.append(obj)


class SceneManager:
    def __init__(self):
        self.scenes = []

    def add(self, scene):
        self.scenes.append(scene)

    def find_scene_by_id(self, scene_id):
        for scene in self.scenes:
            if scene.scene_id == scene_id:
                return scene
