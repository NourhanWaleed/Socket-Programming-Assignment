
import socket

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65432  # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))

    request = b"POST /file.pdf HTTP/1.0\r\nHost: localhost:65432\r\n"
    
    with open("asnmnt.pdf","rb") as f:
        data = f.read()
        request += bytes(f"Content-Length: {len(data)}\r\n\r\n","UTF-8")
        request += data
    
    request += b"\r\n"
    s.sendall(request)

    data = s.recv(241*1024) #receive OK

    print(f"Received {data!r}")