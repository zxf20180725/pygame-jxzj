import datetime
import json
import socket
import traceback
import uuid
from threading import Thread


class Server:
    """
    服务端主类
    """
    __user_cls = None

    @staticmethod
    def write_log(msg):
        cur_time = datetime.datetime.now()
        s = "[" + str(cur_time) + "]" + msg
        print(s)

    def __init__(self, ip, port):
        self.connections = []  # 所有客户端连接
        self.write_log('服务器启动中，请稍候...')
        try:
            self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 监听者，用于接收新的socket连接
            self.listener.bind((ip, port))  # 绑定ip、端口
            self.listener.listen(5)  # 最大等待数
        except:
            self.write_log('服务器启动失败，请检查ip端口是否被占用。详细原因：\n' + traceback.format_exc())

        if self.__user_cls is None:
            self.write_log('服务器启动失败，未注册用户自定义类')
            return

        self.write_log('服务器启动成功：{}:{}'.format(ip, port))
        while True:
            client, _ = self.listener.accept()  # 阻塞，等待客户端连接
            user = self.__user_cls(client, self.connections)
            self.connections.append(user)
            self.write_log('有新连接进入，当前连接数：{}'.format(len(self.connections)))

    @classmethod
    def register_cls(cls, sub_cls):
        """
        注册玩家的自定义类
        """
        if not issubclass(sub_cls, Connection):
            cls.write_log('注册用户自定义类失败，类型不匹配')
            return

        cls.__user_cls = sub_cls


class Connection:
    """
    连接类，每个socket连接都是一个connection
    """

    def __init__(self, socket, connections):
        self.socket = socket
        self.connections = connections
        self.data_handler()

    def data_handler(self):
        # 给每个连接创建一个独立的线程进行管理
        thread = Thread(target=self.recv_data)
        thread.setDaemon(True)
        thread.start()

    def recv_data(self):
        # 接收数据
        bytes = None
        try:
            while True:
                bytes = self.socket.recv(4096)  # 我们这里只做一个简单的服务端框架，只做粘包不做分包处理。
                if len(bytes) == 0:
                    Server.write_log('有玩家离线啦：'+str(self.game_data))
                    self.socket.close()
                    # 删除连接
                    self.connections.remove(self)
                    break
                # 处理数据
                self.deal_data(bytes)
        except:
            self.connections.remove(self)
            Server.write_log('有用户发送的数据异常：'+bytes.decode()+'\n'+'已强制下线，详细原因：\n' + traceback.format_exc())

    def deal_data(self, bytes):
        """
        处理客户端的数据，需要子类实现
        """
        raise NotImplementedError


@Server.register_cls
class Player(Connection):

    def __init__(self, *args):
        super().__init__(*args)
        self.login_state = False  # 登录状态
        self.game_data = None  # 玩家游戏中的相关数据
        self.protocol_handler = ProtocolHandler()  # 协议处理对象

    def deal_data(self, bytes):
        """
        我们规定协议类型：
            1.每个数据包都以json字符串格式传输
            2.json中必须要有protocol字段，该字段表示协议名称
            3.因为会出现粘包现象，所以我们使用特殊字符串"|#|"进行数据包切割。这样的话，一定要注意数据包内不允许出现该字符。
        例如我们需要的协议：
            登录协议：
                客服端发送：{"protocol":"cli_login","username":"玩家账号","password":"玩家密码"}|#|
                服务端返回：
                    登录成功：
                        {"protocol":"ser_login","result":true,"player_data":{"nickname":"昵称","x":5,"y":5}}|#|
                    登录失败：
                        {"protocol":"ser_login","result":false,"msg":"账号或密码错误"}|#|
            玩家移动协议：
                客户端发送：{"protocol":"cli_move","x":100,"y":100}|#|
                服务端发送：{"protocol":"ser_move","uuid":"07103feb0bb041d4b14f4f61379fbbfa","x":100,"y":100}|#|
            玩家上线协议：
                服务端发送：{"protocol":"ser_online","uuid":"07103feb0bb041d4b14f4f61379fbbfa","x":100,"y":100}|#|
            玩家下线协议：
                服务端发送：{"protocol":"ser_offline","uuid":"07103feb0bb041d4b14f4f61379fbbfa"}|#|
        :param bytes:
        :return:
        """
        # 将字节流转成字符串
        pck = bytes.decode()
        # 切割数据包
        pck = pck.split('|#|')
        # 处理每一个协议,最后一个是空字符串，不用处理它
        for str_protocol in pck[:-1]:
            protocol = json.loads(str_protocol)
            # 根据协议中的protocol字段，直接调用相应的函数处理
            self.protocol_handler(self, protocol)


class ProtocolHandler:
    """
    处理客户端返回过来的数据协议
    """

    def __call__(self, player, protocol):
        protocol_name = protocol['protocol']
        if not hasattr(self, protocol_name):
            return None
        # 调用与协议同名的方法
        method = getattr(self, protocol_name)
        result = method(player, protocol)
        if result:
            player.socket.sendall((json.dumps(result,ensure_ascii=False) + '|#|').encode())
        return result

    @staticmethod
    def cli_login(player, protocol):
        """
        客户端登录请求
        {"protocol":"cli_login","username":"玩家账号","password":"玩家密码"}|#|
        登录成功返回：
        {"protocol":"ser_login","result":true,"player_data":{"nickname":"昵称","x":5,"y":5}}|#|
        登录不成功返回：
        {"protocol": "ser_login", "result": false, "msg": "账号或密码错误"}
        """
        # 由于我们还没接入数据库，玩家的信息还无法持久化，所以我们写死几个账号在这里吧
        data = [
            ['admin01', '123456', '玩家昵称1'],
            ['admin02', '123456', '玩家昵称2'],
            ['admin03', '123456', '玩家昵称3'],
        ]
        username = protocol.get('username')
        password = protocol.get('password')
        for user_info in data:
            if user_info[0] == username and user_info[1] == password:
                player.login_state = True
                player.game_data = {
                    'uuid':uuid.uuid4().hex,
                    'nickname': user_info[2],
                    'x': 5,  # 初始位置
                    'y': 5
                }
                # 登录成功
                return {"protocol": "ser_login", "result": True, "player_data": player.game_data}

        # 登录不成功
        return {"protocol": "ser_login", "result": False, "msg": "账号或密码错误"}


if __name__ == '__main__':
    Server('127.0.0.1', 6666)
