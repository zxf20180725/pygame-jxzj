import datetime
import json
import socket
import time
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

    @staticmethod
    def write_in_log_file(msg):
        """
        把一些重要的信息写入日志文件
        """
        with open('./'+time.strftime('%Y-%m-%d',time.localtime(time.time()))+'.log',mode='a+',encoding='utf8') as file:
            cur_time = datetime.datetime.now()
            s = "[" + str(cur_time) + "]" + msg
            file.write(s)

    def __init__(self, ip, port):
        self.connections = []  # 所有客户端连接
        self.write_log('服务器启动中，请稍候...')
        try:
            self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 监听者，用于接收新的socket连接
            self.listener.bind((ip, port))  # 绑定ip、端口
            self.listener.listen(5)  # 最大等待数
        except:
            self.write_log('服务器启动失败，请检查ip端口是否被占用。详细原因请查看日志文件')
            self.write_in_log_file(traceback.format_exc())

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
            self.socket.close()
            self.connections.remove(self)
            Server.write_log('有用户发送的数据异常：' + bytes.decode() + '\n' + '已强制下线，详细原因请查看日志文件')
            Server.write_in_log_file(traceback.format_exc())

    def deal_data(self, bytes):
        """
        处理客户端的数据，需要子类实现
        """
        raise NotImplementedError

    def send(self, py_obj):
        """
        给玩家发送协议包
        py_obj:python的字典或者list
        """
        self.socket.sendall((json.dumps(py_obj, ensure_ascii=False) + '|#|').encode())


@Server.register_cls
class Player(Connection):

    def __init__(self, *args):
        self.login_state = False  # 登录状态
        self.game_data = None  # 玩家游戏中的相关数据
        self.protocol_handler = ProtocolHandler()  # 协议处理对象
        super().__init__(*args)

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
                        {"protocol":"ser_login","result":true,"player_data":{"uuid":"07103feb0bb041d4b14f4f61379fbbfa","nickname":"昵称","x":5,"y":5}}|#|
                    登录失败：
                        {"protocol":"ser_login","result":false,"msg":"账号或密码错误"}|#|
            当前所有在线玩家：
                服务端发送：{"protocol":"ser_player_list","player_list":[{"nickname":"昵称","x":5,"y":5}]}|#|
            玩家移动协议：
                客户端发送：{"protocol":"cli_move","x":100,"y":100}|#|
                服务端发送给所有客户端：{"protocol":"ser_move","player_data":{"uuid":"07103feb0bb041d4b14f4f61379fbbfa","nickname":"昵称","x":5,"y":5}}|#|
            玩家上线协议：
                服务端发送给所有客户端：{"protocol":"ser_online","player_data":{"uuid":"07103feb0bb041d4b14f4f61379fbbfa","nickname":"昵称","x":5,"y":5}}|#|
            玩家下线协议：
                服务端发送给所有客户端：{"protocol":"ser_offline","player_data":{"uuid":"07103feb0bb041d4b14f4f61379fbbfa","nickname":"昵称","x":5,"y":5}}|#|
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

    def send_all_player(self, py_obj):
        """
        把这个数据包发送给所有在线玩家，包括自己
        """
        for player in self.connections:
            player.send(py_obj)

    def send_without_self(self, py_obj):
        """
        发送给除了自己的所有在线玩家
        """
        for player in self.connections:
            if player is not self:
                player.send(py_obj)


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
        return result

    @staticmethod
    def cli_login(player, protocol):
        """
        客户端登录请求
        """
        # 由于我们还没接入数据库，玩家的信息还无法持久化，所以我们写死几个账号在这里吧
        data = [
            ['admin01', '123456', '玩家昵称1'],
            ['admin02', '123456', '玩家昵称2'],
            ['admin03', '123456', '玩家昵称3'],
        ]
        username = protocol.get('username')
        password = protocol.get('password')

        # 校验帐号密码是否正确
        login_state = False
        nickname = None
        for user_info in data:
            if user_info[0] == username and user_info[1] == password:
                login_state = True
                nickname = user_info[2]
                break

        # 登录不成功
        if not login_state:
            player.send({"protocol": "ser_login", "result": False, "msg": "账号或密码错误"})
            return

        # 登录成功
        player.login_state = True
        player.game_data = {
            'uuid': uuid.uuid4().hex,
            'nickname': nickname,
            'x': 5,  # 初始位置
            'y': 5
        }

        # 发送登录成功协议
        player.send({"protocol": "ser_login", "result": True, "player_data": player.game_data})

        # 发送上线信息给其他玩家
        player.send_without_self({"protocol": "ser_online", "player_data": player.game_data})

        player_list = []
        for p in player.connections:
            if p is not player and p.login_state:
                player_list.append(p.game_data)

        # 发送当前在线玩家列表（不包括自己）
        player.send({"protocol": "ser_player_list", "player_list": player_list})

    @staticmethod
    def cli_move(player, protocol):
        """
        客户端移动请求
        """
        # 如果这个玩家没有登录，那么不理会这个数据包
        if not player.login_state:
            return

        # 客户端想要去的位置
        x = protocol.get('x')
        y = protocol.get('y')




if __name__ == '__main__':
    server = Server('127.0.0.1', 6666)
