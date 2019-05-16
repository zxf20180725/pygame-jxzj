import socket

# 创建socket对象，使用TCP协议
server = socket.socket()

# 绑定本机ip和端口号
server.bind(('127.0.0.1', 8712))

# 开始监听
server.listen(5)

# 接收客户端(阻塞线程)，client也是socket对象
client, address = server.accept()

print('有客户端连接啦！', address)

# 发送消息给客户端
client.send(b'I am server.HelloWorld')

# 接收客户端返回的消息(阻塞线程)
data = client.recv(1024)  # 返回的数据类型是bytes

# 由于是字节数组类型，所以需要解码成字符串
str_data = data.decode()

print(str_data)

client.close()

server.close()
