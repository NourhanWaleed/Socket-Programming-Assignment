import socket
import random

Host = "127.0.0.1"
port = 65432
HTTP_Port = 80             #where to use this?


def create_message():
    messages = ['GET', 'POST', 'status 200', 'status 400']                    # how do i handle html, txt and png files?
    i = random.randint(0, 3)
    return messages[i]

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:      # should we change this to while true?
        msg = create_message()
        s.connect((Host, port))
        if msg == 'POST':
            s.sendall(msg)                # ana 7asa eni ba3ok   so please check pseudocode el fel pdf
        elif msg == 'GET':
            data = s.recv(1024)     # receives 1MB
        print(f"Received {data}!")


if __name__ == "__main__":
    main()



# point 3 still not done