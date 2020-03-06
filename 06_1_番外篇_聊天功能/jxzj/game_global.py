class Global:
    """
    游戏全局对象
    """
    __instance = None

    client = None  # 网络处理对象
    player = None  # 玩家自己
    scene_id = 1  # 1登录界面 2游戏界面
    scene_mgr = None  # 场景管理器
    screen = None  # 窗口表面

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = object.__new__(cls)
        return cls.__instance


g = Global()
