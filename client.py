import socket
import threading


DISCONNECT = '!!F'
FORMAT = 'utf-8'
HEADER = 64
PORT = 5050
''' Set the ip of local server '''

SERVER = '192.168.43.88'
ADDR = (SERVER,PORT)
client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client.connect(ADDR)
print('[SUCCESS] Succesfully connected to ',ADDR)
nickname = input('Nickname (Max 256 chars): ').encode(FORMAT)
client.send(nickname)
connected = True

def recieving():
	try:
		msg_length = client.recv(HEADER).decode(FORMAT)
	except socket.error:
		return 0
	if msg_length:
		msg_length = int(msg_length)
		msg = client.recv(msg_length).decode(FORMAT)
		print('\r'+msg+'\nYou : ',end='')




def send(msg):

	message = msg.encode(FORMAT)
	msg_len = len(message)
	send_length = str(msg_len).encode(FORMAT)
	send_length += b' '*(HEADER - len(send_length))
	client.send(send_length)
	client.send(message)

	if msg == DISCONNECT:
		print('Disconnected !')
		client.close()
		return False
	return True

def user_msgs():
	while connected:
		recieving()

def chat():
	global connected
	while connected:
		msg = input('You : ')
		o = send(msg)
		if not o:
			connected = False
usr_thread = threading.Thread(target=user_msgs)
usr_thread.start()
chat()
