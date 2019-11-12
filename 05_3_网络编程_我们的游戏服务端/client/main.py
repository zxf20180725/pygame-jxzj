import socket

s = socket.socket()
s.connect(('192.168.2.27', 6666))
s.send("连接了".encode('utf8'))
input("")