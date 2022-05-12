import socket
from urllib import request
from urllib.error import URLError
import selectors
import types

# from grpc import LocalConnectionType
# TODO: POST request reads content length into file
PORT = 65432

SAVE_PATH = "files/output"

RECV_BUFF = 1024*4
GET_RECV_BUFF = 2048

GET = "GET"
POST = "POST"
STATUS_OK = "200 OK"
STATUS_NOT_FOUND = "404 Not Found"

LOCAL_HOST = "127.0.0.1"
DEF_PORT = 80

ADDRESS = (LOCAL_HOST, PORT)

SEL = selectors.DefaultSelector()

post_request_continuation = False

def retreive_page(url):
    f = request.urlopen(url)
    page = f.read()
    f.close()
    return page

#util
def unpack_request(message:str) -> dict:
    msg_tokens = message.split()
    
    message_contains_port = False
    message_contains_host = False

    # unpacking message contents
    request = msg_tokens[0]
    filename = msg_tokens[1].split("/",1)[1]
    
    # http version
    try:
        _ = msg_tokens.index("HTTP/1.1")
        version = "HTTP/1.1"
    except (ValueError):
        version = "HTTP/1.0"

    # host name and port number
    try:
        i = msg_tokens.index("Host:")
        host = msg_tokens[i+1]
        
        # if not external url
        if not host.startswith("http"):
            try:
                port = host.split(":")[1]
                host = host.split(":")[0]
                message_contains_port = True
            except IndexError:
                port = DEF_PORT
        else:
            # check if http url contains localhost to prevent loop
            try:
                _ =  host.index('localhost')
                host = LOCAL_HOST
                port = host.split(':')[2]
            except(ValueError):
                # external url
                port = None
        message_contains_host = True
    # default is localhost
    except (ValueError, IndexError):
        host = LOCAL_HOST
        port = DEF_PORT

    # get content length
    try:
        i = msg_tokens.index("Content-Length:")
        message_size = int(msg_tokens[i + 1])
    except (ValueError):
        message_size = None

    if request == POST:
        if message_contains_port:
            data_idx = message.index(port) + len(port) + 2
        elif message_contains_host:
            data_idx = message.index(host) + len(host) + 2
        else:
            data_idx = message.index(version) + len(version) + 2
    
        data = message[data_idx:]
    else :
        data = ""

    result = {
        'host':host,
        'port':port,
        'version':version,
        'filename':filename,
        'request': request,
        'message-length':message_size,
        'data':data
    }
    return result



def service_get_request(result:dict) -> bytes:
    # if external url delegate  to urllib or the url is wrong
    if result['port'] != PORT:
        response = (bytes(f"{result ['version']} {STATUS_NOT_FOUND}\r\n","UTF-8"))    # TODO: send a clearer message

    if result['host'].startswith("http"):
        try:
            file = retreive_page(result['host']+"/"+result['filename'])
            response = bytes(f"{result['version']} {STATUS_OK}\r\n","UTF-8") + file
        except(URLError):
            response = (bytes(f"{result['version']} {STATUS_NOT_FOUND}\r\n","UTF-8"))   
            
    else:
        try:
            with open(result['filename'],"rb") as f:
                outputdata = f.read()       #opens requiered file and reads its content
                                
            response = bytes(f"{result ['version']} {STATUS_OK}\r\n\r\n","UTF-8")
            response += outputdata
        except(FileNotFoundError):
            response = (bytes(f"{result ['version']} {STATUS_NOT_FOUND}\r\n","UTF-8"))    
    return response

def service_post_request(result:dict)-> bytes:
    outfile = result['filename']
    data = result['data']

    with open(outfile,'wb') as f:
        f.write(bytes(data[:-2],"UTF-8"))
    response = (bytes(f"{result['version']} {STATUS_OK}\r\n","UTF-8"))    
    return response

def receive_from_client(message):
    message = message.decode()
    response = b""

    result = unpack_request(message)

    if result['request'] == GET :
        response = service_get_request(result)  
    elif result['request'] == POST:
        response = service_post_request(result)
            
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
                        accept_wrapper(key.fileobj)
                    else:
                        service_connection(key, mask)
        except KeyboardInterrupt:
            print("Caught keyboard interrupt, exiting")
        finally:
            SEL.close()

if __name__ == "__main__":
    main()

'''
TODO: HTTP 1.1: time out : persistent connection
TODO: buffer size in post request

outline
 set a global variaable to recognize whether the next packet is continuation of post request
 in the receive from client fn: check this the first thing, delegate to post to continue receiving

'''