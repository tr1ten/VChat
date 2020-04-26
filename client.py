import socket
import threading
import os
import tqdm


DISCONNECT = '!!F'
FORMAT = 'utf-8'
HEADER = 64
BUFFER = 4096
''' Port provided by ngrok '''
PORT = int(input('PORT : '))
''' Setting ngrok server '''
SERVER = '0.tcp.ngrok.io'
# SERVER = '127.0.0.1'

ADDR = (SERVER, PORT)
SEPERATOR = ':'

''' Transferring File '''
def file_transfer():
    sendto = input('Send to [everyone,username]: ')
    file_path = input('Path :')
    if not os.path.exists(file_path):
        print('file not found ,try again.. ')
        file_transfer()
    
    filename = os.path.basename(file_path)
    filesize = os.path.getsize(file_path)
    send(filename+SEPERATOR+str(filesize)+SEPERATOR+sendto)
    progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    ''' reading data as binary in chunks and sending it to server '''
    with open(file_path,'rb') as f:
        for _ in progress:
            data = f.read(BUFFER)
            if not data:
                break
            client.sendall(data)
            progress.update(len(data))
    return 1

''' protocol for sending message to server'''
def send(msg):
    message = msg.encode(FORMAT)
    msg_len = len(message)
    send_length = str(msg_len).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)

    if msg == DISCONNECT:
        print('Disconnected !')
        client.close()
        return False
    if msg in FMSG.keys():
        FMSG[msg]()
    return True

''' Recieving File '''
def rec_file(conn):
    ln = conn.recv(HEADER).decode(FORMAT)
    ln = int(ln)
    recs = conn.recv(ln).decode(FORMAT)
    filename,filesize,nick = recs.split(SEPERATOR)
    filesize = int(filesize)
    progress = tqdm.tqdm(range(filesize), f"Recieving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(filename,'wb') as f:
        for _ in progress:
            chunk = conn.recv(BUFFER)
            if not chunk:
                print('breaking.. ',chunk)
                break
            f.write(chunk)
            progress.update(len(chunk))
    print('\r' + f'{nick} : [Shared] {filename} '+'\nYou :',end=' ')

''' recieving messages '''

def recieving():
    try:
        msg_length = client.recv(HEADER).decode(FORMAT)
    except socket.error:
        return 0
    if msg_length:
        msg_length = int(msg_length)
        msg = client.recv(msg_length).decode(FORMAT)
        if msg in FMSG:
            FMSG[msg](client)
        else:	
            print('\r' + msg + '\nYou : ', end='')

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

FMSG = {'!!T':file_transfer,'--R':rec_file}
if __name__ == '__main__':
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    print('[SUCCESS] Succesfully connected to ', ADDR)
    nickname = input('Nickname (Max 64 chars): ').encode(FORMAT)
    nickname += b' ' * (HEADER - len(nickname))
    client.send(nickname)
    connected = True
    usr_thread = threading.Thread(target=user_msgs)
    usr_thread.start()
    chat()
