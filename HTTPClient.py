import socket
import random

Host = "127.0.0.1"
port = 65432
HTTP_Port = 80             # where to use this?
address = ("127.0.0.1", 65432)


def create_message():
    messages = 'GET test.txt'
    return messages


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:      # should we change this to while true?
        f = open('commands.txt','r')
        while True:
            # msg = 'GET images.png'
            msg = input()
            #msg = 'GET images.png'
            #msg  = input()
            msg = f.readline()
            if not msg :    #end of file 
                break
            Host_name = msg.split()[2]      #mesh m7tagenhom bs homa 2alo 3leha 
            if msg.split()[2] != '\0' :
                HTTP_Port = msg.split()[2]      #mesh m7tagenhom bs homa 2alo 3leha
            data = 0
            s.connect((Host, port))
            s.sendto(bytes(msg, "UTF-8"), address)
            if msg.split()[0] == 'POST':
                data = s.recv(1024)
            elif msg.split()[0] == 'GET':
                data = s.recv(1024)     # receives 1MB
            print(f"Received {data}!")
            # data = s.recv(2048)
            for i in range(0, 300):
                data = s.recv(2048)
                print(data)

        f.close()



if __name__ == "__main__":
    main()



# point 3 still not done