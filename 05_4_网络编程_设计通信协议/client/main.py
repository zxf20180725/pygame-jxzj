import socket

s = socket.socket()
s.connect(('127.0.0.1', 6666))  # 与服务器建立连接

# 发送登录协议，请求登录
s.sendall('{"protocol":"cli_login","username":"admin01","password":"123456"}|#|'.encode())
# 接收服务端返回的消息
data = s.recv(4096)
print(data.decode())
data = s.recv(4096)
print(data.decode())
input("")
s.close()
