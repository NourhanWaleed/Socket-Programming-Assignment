import socket
import threading
from urllib import request
import os.path
import shutil
from struct import pack, unpack

PORT = 65432 

SAVE_PATH = "files/output"

RECV_BUFF = 1024
GET_RECV_BUFF = 2048

REQUEST_IDX = 0
FILE_NAME_IDX = 1
HTTP_VERSION_IDX = 2
HOST_IDX = 4
PORT_IDX = 5

GET = "GET"
POST = "POST"
STATUS_OK = "200 OK" # TODO:use
STATUS_NOT_FOUND = "404 Not Found"

LOCAL_HOST = "127.0.0.1"
DEF_PORT = 80

ADDRESS = (LOCAL_HOST, PORT)

def retreive_page(url):
    f = request.urlopen(url)
    page = f.read().decode("UTF-8")
    f.close()
    return page


def receive_from_client(conn,addr):
    print(f"New client {ADDRESS} connected.")

    connected = True
    response = ""
    while connected:
        message = conn.recv(RECV_BUFF).decode()      # TODO: recv bytes w struct and unpack, buffer is 1MB 
        if not message:
            break

        msg_tokens = message.split()
        # unpacking message contents
        request = msg_tokens[0]
        filename = msg_tokens[1].split("/",1)[1]
        try:
            _ = msg_tokens.index("HTTP/1.1")
            version = "HTTP/1.1"
        except (ValueError):
            version = "HTTP/1.0"

        try:
            i = msg_tokens.index("Host:")
            host = msg_tokens[i+1]
            try:
                port = host.split(":")[1]
                host = host.split(":")[0]
            except IndexError:
                port = DEF_PORT
        except (ValueError):
            host = LOCAL_HOST

        if request == GET :
            # TODO: pick out name of requested file
            try:
                print(filename)
                # outputdata = retreive_page(filename)
                with open(filename) as f:
                    outputdata = f.read()       #opens requiered file and reads its content
                                 
                response = f"{version} 200 OK\r\n"
                response += outputdata
            except(FileNotFoundError):
               conn.sendall(bytes(f"{version} 404 Not Found\r\n","UTF-8"))     #TODO:send the Http header which is formatted as 404 Not Found

        elif request == POST:
            try:
                outputdata = msg_tokens[FILE_NAME_IDX] 
                newpath = shutil.copy(outputdata,SAVE_PATH)    #TODO: clean this up, copy the required file into ServerFolder (simulating sending it to server)
                conn.sendall(bytes("HTTP/1.0 200 OK\r\n","UTF-8"))     
                # TODO: wait for uploaded file from client
            except(FileNotFoundError):
                conn.sendall(b"HTTP/1.0 404 Not Found\r\n")
                break
        # TODO: handle html files, txt files and png files
        else:
            outputdata = "unknown message"      #for any not supported methods


        print(f"[{addr}] {message}")
        if response != "":     # Send the content of the requested file to the client
            conn.sendall(bytes(response,"UTF-8")) 
        conn.sendall("\r\n".encode())
    conn.close()


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:          #just a smol question is this equivilant to while true? nah ur good
        s.bind(ADDRESS)
        s.listen()
        print(f"[LISTENING] Server is listening on {LOCAL_HOST}:{PORT}")
        while True:
            conn, addr = s.accept()
            thread = threading.Thread(target=receive_from_client(conn,addr), args=(conn, addr)) # f: is this working?
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.activeCount()}")     # what is threading.activecount?  the number of Thread objects currently alive. 

if __name__ == "__main__":
    main()

'''
TODO: why does it get sad when a connection is closed? ConnectionResetError: [WinError 10054] An existing connection was forcibly closed by the remote host
TODO: who closes the threads?
'''