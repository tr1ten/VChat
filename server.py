import socket
import threading
import random
import string

''' Initializing variables '''

DISCONNECT = '!!F'
FORMAT = 'utf-8'
HEADER = 64
PORT = 5050
''' generating random keyword for join message'''
JOIN = ''.join([random.choice(string.ascii_uppercase) for _ in range(random.randrange(30,50))])
'''  Socket obj for server '''
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER,PORT)
server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
''' Reusing the same port if rerun '''
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(ADDR)
connections = {}

''' Sending messages to all connected users '''
def sendtoall(msg,addr,nickname):
	if msg == DISCONNECT:
		message = (f'{nickname} Disconnected !').encode(FORMAT)
	elif msg == JOIN:
		message = (f'[JOINED] {nickname}').encode(FORMAT)
	
	else:
		message = (f'[MESSAGE] {nickname} : {msg}').encode(FORMAT)
	msg_len = str(len(message)).encode(FORMAT)
	msg_len += b' '*(HEADER - len(msg_len))
	for addresses in connections:
		if addresses != addr :
			try:
				connections[addresses][0].send(msg_len)
				connections[addresses][0].send(message)
			except socket.error:
				del connections[addresses]


''' Handling and showing clients messages ''' 
def handle_client(conn,addr):
	sendtoall(JOIN,addr,connections[addr][1])
	connection = True
	while connection:
		msg_length = conn.recv(HEADER).decode(FORMAT)
		if msg_length:
			msg_length = int(msg_length)
			msg = conn.recv(msg_length).decode(FORMAT)
			sendtoall(msg,addr,connections[addr][1])
			if msg == DISCONNECT:
				connection = False

	del connections[addr]
	conn.close()
	print(f'[DISCONNECTED] {addr}')



''' Starting Listening on IP '''
def start():
	server.listen()
	print(f'[LISTENING] Server listening on  {SERVER}')
	while True:
		conn,addr = server.accept()
		nick = conn.recv(256).decode(FORMAT)
		connections[addr] = (conn,nick)
		thread = threading.Thread(target=handle_client,args=(conn,addr))
		print(f'[JOINED] {nick} join the  chat')
		print(f'Current Connections : {threading.activeCount()}')
		thread.start()

		
''' Handling Force exit and closing server '''
try:
	start()
except KeyboardInterrupt:
	server.shutdown(socket.SHUT_RDWR)
	server.close()
	print('Server Closed !')
