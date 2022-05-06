import socket
import threading
import urllib
import os.path
import shutil

Host = "127.0.0.1"
port = 65432
address = (Host, port)
GET = "GET"
POST = "POST"
status_200 = "status 200"
status_404 = "status 404"

def retreive_page(url):
    f = urllib.request.urlopen(url)
    page = f.read().decode("UTF-8")
    f.close()
    return page


def receive_from_client(conn,addr):
    print(f"New client {address} connected.")

    connected = True
    outputdata = "failed"
    while connected:
        message = conn.recv(1024).decode()      # buffer is 1MB
        if message.split()[0] == 'GET' :
            # TODO: pick out name of requested file
            try:
                filename = message.split()[1]
                print(filename)
                #outputdata = retreive_page(filename)
                f = open(filename[0:])
                outputdata = f.read()
                f.close()
                #send the Http header which is formatted as 200 OK 
                conn.send(bytes("HTTP/1.0 200 OK\r\n","UTF-8"))
                #Send the content of the requested file to the client
                #for i in range(0, len(outputdata)+10):
                    #conn.send(outputdata[i].encode())
                    #print(outputdata[i].encode())
                #conn.send("\r\n".encode())
                
                #connected = False
            except: # if file not found
               conn.send(bytes("HTTP/1.0 404 Not Found\r\n","UTF-8"))
               #connected = False
               
        elif message.split()[0] == POST:
            try:
                outputdata = message.split()[1] 
                newpath = shutil.copy(outputdata,"E:\esraa\Computer Networks\prog.Ass\ServerFolder")
                conn.send(bytes("HTTP/1.0 200 OK\r\n","UTF-8"))     
                # TODO: wait for uploaded file from client
            except:
                conn.send(bytes("HTTP/1.0 404 Not Found\r\n","UTF-8"))
        # TODO: handle html files, txt files and png files
        else:
            outputdata = "unknown message"
        if not message:
            break

        print(f"[{addr}] {message}")
        conn.send(bytes(outputdata,"UTF-8"))
        conn.send("\r\n".encode())
    conn.close()


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:          #just a smol question is this equivilant to while true?
        s.bind(address)
        s.listen()
        print(f"[LISTENING] Server is listening on {Host}:{port}")
        while True:
            conn, addr = s.accept()
            thread = threading.Thread(target=receive_from_client(conn,addr), args=(conn, addr))
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")     # what is threading.activecount?

if __name__ == "__main__":
    main()



