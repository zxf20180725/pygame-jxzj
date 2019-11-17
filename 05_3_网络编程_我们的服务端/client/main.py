import socket

s = socket.socket()
s.connect(('127.0.0.1', 6666))
s.send("你好呀，我是客户端".encode('utf8'))
input("")
