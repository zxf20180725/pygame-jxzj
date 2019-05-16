import socket

# 创建socket对象
client = socket.socket()

# 连接服务端
client.connect(('127.0.0.1', 8712))

# 接收服务端发送过来的数据
data = client.recv(1024)

str_data = data.decode()

print(str_data)

client.send(b'I am client.Hello!')

client.close()
