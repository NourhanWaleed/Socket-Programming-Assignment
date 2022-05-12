import socket
import random

from requests import request

'''
TODO: check correctness of all constant numbers
TODO: check whether the constant truly is a constant or might we receive a value to change this (HOST,PORT)
TODO: do we need to use struct package? If so, use it in send and receive.
TODO: check the http message format
TODO: map localhost to LOCAL_HOST, anyhting else to its appropriate address
------------------------------------------- HOUSEKEEPING -------------------------------------------
TODO: cache


TODO: tests
'''
COMMAND_FILE_PATH = 'commands.txt'

DEST_PORT = 65432 # server port number
BROWSER_PORT = 80             # where to use this?
LOCAL_HOST = "127.0.0.1"
DEST_ADDRESS = (LOCAL_HOST, DEST_PORT)

RECV_BUFF = 50*1024
GET_RECV_BUFF = 50*2048

HOST_IDX = 2
PORT_IDX = 3
REQUEST_IDX = 0
FILE_NAME_IDX = 1

GET = "GET"
POST = "POST"
STATUS_OK = "200 OK" # TODO:use
STATUS_NOT_FOUND = "404 Not Found"



'''
def create_message():
    messages = 'GET test.txt'
    return messages
'''
def server_post_request(file_name:str):
    with open(file_name, 'rb') as f:
        data = f.read()
        data_size = len(data)
    return data,data_size    

def main():
    f = open(COMMAND_FILE_PATH,'r')    #open commands file

    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:      # should we change this to while true?
            # msg = 'GET images.png'
            #msg = input()
            #msg = 'GET images.png'
            #msg  = input()
            msg = f.readline()  #read line by line
            
            if not msg:    #end of file 
                break

            msg_tokens = msg.split()
            request = msg_tokens[REQUEST_IDX]
            file_name = msg_tokens[FILE_NAME_IDX].split('/',1)[1]
            Host_name = msg_tokens[HOST_IDX]     
            if len(msg_tokens) >= 4 and msg_tokens[PORT_IDX] != '\0' :
                HTTP_Port = ":"  + msg_tokens[PORT_IDX]     
            else:
                HTTP_Port = ""
            data = 0
            
            s.connect((LOCAL_HOST, DEST_PORT)) 
            if request == "GET":
                message = f"GET {file_name} HTTP/1.1\r\nHost: {Host_name}{HTTP_Port}\r\n\r\n"
            elif request == "POST":
                file, file_size = server_post_request(file_name)
                message = f"POST /{file_name} HTTP/1.1\r\nHost: {Host_name}{HTTP_Port}\r\nContent-Length: {file_size}\r\n\r\n{file}\r\n"
            s.sendall(bytes(message,"UTF-8")) # sending message to server
            
            if msg_tokens[REQUEST_IDX] == 'POST':
                data = s.recv(RECV_BUFF) #receives responce (OK/Not found)
            elif msg_tokens[REQUEST_IDX] == 'GET':
                data = s.recv(RECV_BUFF)     # receives 1MB
                # # TODO: what is this? WHY 300?
                # for i in range(0, 300):     #receives data in case of GET what is the server sending here?
                #     data = s.recv(GET_RECV_BUFF)
                #     print(data)
            print(f"Received {data}!")  
            # data = s.recv(GET_RECV_BUFF)


    f.close()



if __name__ == "__main__":
    main()



# point 3 still not done
