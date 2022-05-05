import socket
import threading

Host = "127.0.0.1"
port = 65432
address = (Host, port)
GET = "GET"
POST = "POST"
status_200 = "status 200"
status_404 = "status 404"
def receive_from_client(conn,addr):
    print(f"New client {address} connected.")

    connected = True
    while connected:
        message = conn.recv(1024).decode()      # buffer is 1MB
        if message == GET:
            # TODO: pick out name of requested file
      # if file not found:
        #      reply = "HTTP/1.0 404 Not Found\r\n"
        elif message == POST:
            reply = "OK"
            # TODO: wait for uploaded file from client
        elif message == status_200:
            # honestly i have no idea what is status 200
        elif message == status_404:
            reply = "error: file not found"
        # TODO: handle html files, txt files and png files
        else:
            reply = "unknown message"
        if not message:
            break

        print(f"[{addr}] {message}")
        conn.sendall(reply)

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



