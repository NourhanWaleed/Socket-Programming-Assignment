import socket
import threading
from urllib import request
from urllib.error import URLError
import selectors
import sys
import shutil
import types

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
STATUS_OK = "200 OK"
STATUS_NOT_FOUND = "404 Not Found"

LOCAL_HOST = "127.0.0.1"
DEF_PORT = 80

ADDRESS = (LOCAL_HOST, PORT)

SEL = selectors.DefaultSelector()

def retreive_page(url):
    f = request.urlopen(url)
    page = f.read()
    f.close()
    return page


def receive_from_client(message):
    # print(f"New client {ADDRESS} connected.")
    message = message.decode()
    response = ""

    msg_tokens = message.split()
    
    # unpacking message contents
    request = msg_tokens[0]
    filename = msg_tokens[1].split("/",1)[1]
    
    # http version
    try:
        _ = msg_tokens.index("HTTP/1.1")
        version = "HTTP/1.1"
    except (ValueError):
        version = "HTTP/1.0"

    # host name and por number
    try:
        i = msg_tokens.index("Host:")
        host = msg_tokens[i+1]
        
        # if not external url
        if not host.startswith("http"):
            try:
                port = host.split(":")[1]
                host = host.split(":")[0]
            except IndexError:
                port = DEF_PORT

    # default is localhost
    except (ValueError):
        host = LOCAL_HOST

        
    if request == GET :
        # if external url delegate  to urllib or the url is wrong
        if host.startswith("http"):
            try:
                file = retreive_page(host+"/"+filename)
                response = bytes(f"{version} {STATUS_OK}\r\n","UTF-8") + file
            except(URLError):
                response = (bytes(f"{version} {STATUS_NOT_FOUND}\r\n","UTF-8"))   
                
        else:
            try:
                print(filename)
                
                with open(filename,"rb") as f:
                    outputdata = f.read()       #opens requiered file and reads its content
                                    
                response = bytes(f"{version} 200 OK\r\n","UTF-8")
                response += outputdata
            except(FileNotFoundError):
                response = (bytes(f"{version} 404 Not Found\r\n","UTF-8"))    

    # TODO: post
    elif request == POST:
        try:
            outdata = msg_tokens[FILE_NAME_IDX] 
            newpath = shutil.copy(outputdata,SAVE_PATH)    #TODO: clean this up, copy the required file into ServerFolder (simulating sending it to server)
            response = (bytes("HTTP/1.0 200 OK\r\n","UTF-8"))     
            # TODO: wait for uploaded file from client
        except(FileNotFoundError):
            response = (b"HTTP/1.0 404 Not Found\r\n")
            
    
    # else:
    #     outputdata = "unknown message"      #for any unsupported methods


    #print(f"[{addr}] {message}")
#     if response != "":     # Send the content of the requested file to the client
#         conn.sendall(response) 
#     conn.sendall("\r\n".encode())
# conn.close()
    # conn.sendall(b"exitinggggg")
    return response + (b"\r\n")

def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    print(f"Accepted connection from {addr}")
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    SEL.register(conn, events, data=data)

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        try:
            recv_data = sock.recv(RECV_BUFF)  # Should be ready to read
            if recv_data:
                data.outb += recv_data
            else:
                print(f"Closing connection to {data.addr}")
                SEL.unregister(sock)
                sock.close()
        except(ConnectionResetError):
            print(f"Connection to {data.addr} was reset")
            SEL.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE and data.outb:
        # print(f"Echoing {data.outb!r} to {data.addr}") #TODO: replace
        # send data to fn, receive output data, place it in data.outb
        data.outb = receive_from_client(data.outb)
        sent = sock.send(data.outb)  # Should be ready to write
        data.outb = data.outb[sent:]

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(ADDRESS)
        s.listen()
        print(f"[LISTENING] Server is listening on {LOCAL_HOST}:{PORT}")
        s.setblocking(False)
        SEL.register(s, selectors.EVENT_READ, data=None)

        try:
            while True:
                events = SEL.select(timeout=None)
                for key, mask in events:
                    if key.data is None:
                        accept_wrapper(key.fileobj) #TODO
                    else:
                        service_connection(key, mask) #TODO
        except KeyboardInterrupt:
            print("Caught keyboard interrupt, exiting")
        finally:
            SEL.close()

        while True:
            conn, addr = s.accept()
            #thread = threading.Thread(target=receive_from_client(conn,addr), args=(conn, addr)) # f: is this working?
            #thread.start()
            #print(f"[ACTIVE CONNECTIONS] {threading.activeCount()}")     # what is threading.activecount?  the number of Thread objects currently alive. 

if __name__ == "__main__":
    main()

'''
TODO: why does it get sad when a connection is closed? ConnectionResetError: [WinError 10054] An existing connection was forcibly closed by the remote host
TODO: who closes the threads?
'''