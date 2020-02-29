class Global:
    """
    游戏全局对象
    """
    __instance = None

    client = None  # 网络处理对象
    player = None  # 玩家自己

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = object.__new__(cls)
        return cls.__instance


g = Global()
