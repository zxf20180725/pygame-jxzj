import json
import traceback
from threading import Thread

from core import Player, CharWalk
from game_global import g


class Client:
    """
    客户端与服务端网络交互相关的操作
    """

    def __init__(self, socket, game_scene):
        self.socket = socket  # 客户端socket
        self.game = game_scene  # GameScene对象
        # 创建一个线程专门处理数据接收
        thread = Thread(target=self.recv_data)
        thread.setDaemon(True)
        thread.start()

    def data_handler(self):
        # 给每个连接创建一个独立的线程进行管理
        thread = Thread(target=self.recv_data)
        thread.setDaemon(True)
        thread.start()

    def deal_data(self, bytes):
        """
        处理数据
        """
        # 将字节流转成字符串
        pck = bytes.decode()
        # 切割数据包
        pck = pck.split('|#|')
        # 处理每一个协议,最后一个是空字符串，不用处理它
        for str_protocol in pck[:-1]:
            protocol = json.loads(str_protocol)
            # 根据协议中的protocol字段，直接调用相应的函数处理
            self.protocol_handler(protocol)

    def recv_data(self):
        # 接收数据
        try:
            while True:
                bytes = self.socket.recv(4096)
                if len(bytes) == 0:
                    self.socket.close()
                    # TODO:掉线处理
                    break
                # 处理数据
                self.deal_data(bytes)
        except:
            self.socket.close()
            # TODO:异常掉线处理
            traceback.print_exc()

    def send(self, py_obj):
        """
        给服务器发送协议包
        py_obj:python的字典或者list
        """
        self.socket.sendall((json.dumps(py_obj, ensure_ascii=False) + '|#|').encode())

    def protocol_handler(self, protocol):
        """
        处理服务端发来的协议
        """
        if protocol['protocol'] == 'ser_login':
            # 登录协议的相关逻辑
            if not protocol['result']:
                # 登录失败，继续调用登录方法
                print("登录失败：", protocol['msg'])
                return
            # 登录成功
            # 创建玩家
            self.game.role = Player(self.game.hero, protocol['player_data']['role_id'], CharWalk.DIR_DOWN,
                                    protocol['player_data']['x'], protocol['player_data']['y'],
                                    name=protocol['player_data']['nickname'], uuid=protocol['player_data']['uuid'])
            # 把玩家存到全局对象中，后面有用
            g.player = self.game.role
            g.scene_id = 2  # 切换场景
        elif protocol['protocol'] == 'ser_player_list':
            # 玩家列表
            print(protocol)
            for player_data in protocol['player_list']:
                player = Player(self.game.hero, player_data['role_id'], CharWalk.DIR_DOWN,
                                player_data['x'], player_data['y'],
                                name=player_data['nickname'], uuid=player_data['uuid']
                                )
                self.game.other_player.append(player)
        elif protocol['protocol'] == 'ser_move':
            # 其他玩家移动了
            for p in self.game.other_player:
                if p.uuid == protocol['player_data']['uuid']:
                    p.goto(protocol['player_data']['x'], protocol['player_data']['y'])
                    break
        elif protocol['protocol'] == 'ser_online':
            # 有其他玩家上线
            player_data = protocol['player_data']
            player = Player(self.game.hero, player_data['role_id'], CharWalk.DIR_DOWN,
                            player_data['x'], player_data['y'],
                            name=player_data['nickname'], uuid=player_data['uuid']
                            )
            self.game.other_player.append(player)
        elif protocol['protocol'] == 'ser_chat':
            # 聊天
            self.game.chat_history.insert(0, "【%s】 " % protocol["nickname"] + protocol['text'])
            if len(self.game.chat_history) > 5:
                self.game.chat_history.pop()

    def login(self, username, password):
        """
        登录
        """
        data = {
            'protocol': 'cli_login',
            'username': username,
            'password': password
        }
        self.send(data)

    def move(self, player):
        """
        玩家移动
        """
        data = {
            'protocol': 'cli_move',
            'x': player.next_mx,
            'y': player.next_my
        }
        self.send(data)

    def chat(self, text):
        data = {
            'protocol': 'cli_chat',
            'text': text
        }
        self.send(data)
