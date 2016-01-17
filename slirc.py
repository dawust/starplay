import socket
import os, fcntl

def connect():
	while True:
		try:
			socket_path =  "/var/run/lirc/lircd"
			sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
			sock.connect(socket_path)
			ret = fcntl.fcntl(sock, fcntl.F_GETFL, 0)
			fcntl.fcntl(sock, fcntl.F_SETFL, ret | os.O_NONBLOCK)
			return sock
		except:
			pass

def nextcodes(sock):
	try:
		res = []
		buf = sock.recv(1024)
		lines = buf.decode('ascii').split("\n")
		for line in lines[:-1]:
			code,count,cmd,device = line.split(" ")
			res.append(cmd)
		return res
	except:
		return []

