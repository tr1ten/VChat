import socket
import threading
import random
import string
from pyngrok import ngrok
import tqdm

''' Initializing variables '''
DISCONNECT = '!!F'
BUFFER = 4096
FORMAT = 'utf-8'
HEADER = 64
PORT = 5050
SEPERATOR = ':'
connections = {}
''' generating random keyword for join message'''
JOIN = ''.join([random.choice(string.ascii_uppercase) for _ in range(random.randrange(30,50))])
'''  Local host where traffic would be forwarded by ngrok server '''
SERVER = '127.0.0.1'
ADDR = (SERVER,PORT)
server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
''' Reusing the same port if rerun '''
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#  FORWARDING TRAFFIC TO LOCAL HOST:PORT
p_url = ngrok.connect(PORT,'tcp')
_,n_host,n_port = p_url.split(':')
server.bind(ADDR)

''' Random Client Generator '''
def gen_username():
	n = 1
	while 1:
		yield f'user {n}'
		n +=1

gen = gen_username()



''' recieving file '''
def transfer_file(conn,name):
	ln = conn.recv(HEADER).decode(FORMAT)
	ln = int(ln)
	recs = conn.recv(ln).decode(FORMAT)
	filename,filesize,nick = recs.split(SEPERATOR)
	for con in connections.values():
		if con[1] == nick:
			sender = con[0]
			print("Sending file to ",nick)
			send(sender,'--R')
			send(sender,filename+SEPERATOR+str(filesize)+SEPERATOR+name)
			break
	else:
		print('user not found !')
		conn.close()

	filesize = int(filesize)
	sent_size = 0
	progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
	for _ in progress:
		if  sent_size >= filesize:
			break
		chunk = conn.recv(BUFFER)
		if not chunk:
			print('Breaking !')
			break
		sender.sendall(chunk)
		sent_size += len(chunk)
		progress.update(len(chunk))


	print(f'{name} : [FILE] {filename} ')


''' Sending messages to all connected users '''
def sendtoall(msg,addr,nickname):
	if msg == DISCONNECT:
		message = (f'{nickname} Disconnected !').encode(FORMAT)
	elif msg == JOIN:
		message = (f'[JOINED] {nickname}').encode(FORMAT)
	
	else:
		message = (f'{nickname} : {msg}').encode(FORMAT)
	msg_len = str(len(message)).encode(FORMAT)
	msg_len += b' '*(HEADER - len(msg_len))
	try:
		for addresses in connections:
			if addresses != addr :
				try:
					connections[addresses][0].send(msg_len)
					connections[addresses][0].send(message)
				except socket.error:
					del connections[addresses]
	except Exception:
		print('Error while sending to all clients !')


''' Sending msg  '''
def send(conn,msg):
    message = msg.encode(FORMAT)
    msg_len = len(message)
    send_length = str(msg_len).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    conn.send(send_length)
    conn.send(message)

''' Handling and Sending messages to all clients ''' 
def handle_client(conn,addr):
	sendtoall(JOIN,addr,connections[addr][1])
	connection = True
	while connection:
		msg_length = conn.recv(HEADER).decode(FORMAT)
		if msg_length:
			msg_length = int(msg_length)
			msg = conn.recv(msg_length).decode(FORMAT)
			if msg == DISCONNECT:
				connection = False
			if msg in FMSG:
				FMSG[msg](conn,connections[addr][1])
				continue
			sendtoall(msg, addr, connections[addr][1])

	del connections[addr]
	conn.close()
	print(f'[DISCONNECTED] {addr}')



''' Starting Listening on Server Socket '''
def start():
	server.listen()
	print(f'[LISTENING] Server listening on  {SERVER}')
	print('HOST : ',n_host)
	print('PORT : ',n_port)
	while True:
		conn,addr = server.accept()
		try:
			nick = conn.recv(HEADER).decode(FORMAT).strip()
		except:
			continue
		else:
			if not nick:
				continue

		connections[addr] = (conn,nick)
		thread = threading.Thread(target=handle_client,args=(conn,addr))
		print(f'[JOINED] {nick} join the  chat  ->',addr)
		print(f'Current Connections : {threading.activeCount()}')
		thread.start()

		
FMSG = {'!!T':transfer_file}
''' Handling Force exit and closing server connection '''
try:
	start()
except KeyboardInterrupt:
	server.shutdown(socket.SHUT_RDWR)
	server.close()
	print('Server Closed !')
