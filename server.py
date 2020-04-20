import socket
import threading


''' Initializing variables '''

DISCONNECT = '!!F'
FORMAT = 'utf-8'
HEADER = 64
PORT = 5050
'''  Socket obj for server '''
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER,PORT)
server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
''' Reusing the same port if rerun '''
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(ADDR)
connections = {}

''' Sending messages to all connected users '''
def sendtoall(msg,addr):
	if msg == DISCONNECT:
		message = (f'User {addr} Disconnected !').encode(FORMAT)
	else:
		message = (f'[MESSAGE] {addr} : {msg}').encode(FORMAT)
	msg_len = str(len(message)).encode(FORMAT)
	msg_len += b' '*(HEADER - len(msg_len))
	for addresses in connections:
		if addresses != addr :
			try:
				connections[addresses].send(msg_len)
				connections[addresses].send(message)
			except socket.error:
				del connections[addresses]


''' Handling and showing clients messages ''' 
def handle_client(conn,addr):
	connections[addr] = conn
	print(f'[JOINED] new user {addr}')
	connection = True
	while connection:
		msg_length = conn.recv(HEADER).decode(FORMAT)
		if msg_length:
			msg_length = int(msg_length)
			msg = conn.recv(msg_length).decode(FORMAT)
			print(f'[MESSAGE] {addr} : {msg}')
			sendtoall(msg,addr)
			
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
		connections[addr] = conn
		thread = threading.Thread(target=handle_client,args=(conn,addr))
		print(f'Current Connections : {threading.activeCount()}')
		thread.start()

		

start()