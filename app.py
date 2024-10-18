import socket
import struct

def receive_exact(conn, n):
    chunks = []
    bytes_received = 0
    while bytes_received < n:
        chunk = conn.recv(1024)
        if not chunk:
            raise ConnectionError("Connection lost")
        chunks.append(chunk)
        bytes_received += len(chunk)
    return b''.join(chunks)

def receive_full_message(conn):
    message_length_bytes = receive_exact(conn, 4)
    message_length = struct.unpack('!I', message_length_bytes)[0]

    return receive_exact(conn, message_length)

def send_message(conn, message):
    message_bytes = message.encode()
    message_length = len(message_bytes)

    conn.sendall(struct.pack('!I', message_length))

    chunk_size = 1024
    for i in range(0, message_length, chunk_size):
        conn.sendall(message_bytes[i:i + chunk_size])

def tcp_server(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen(1)
        print(f"TCP server listening on {host}:{port}")
        
        try:
            while True:
                conn, addr = server_socket.accept()
                print(f"Connected by {addr}")
                with conn:
                    while True:
                        try:
                            data = receive_full_message(conn)
                        except ConnectionError:
                            print(f"Connection with {addr} closed")
                            break
                        print(f"Received ({len(data)} bytes): {data.decode()}")
                        message = input("You: ")
                        send_message(conn, message)
        except KeyboardInterrupt:
            print("\nServer interrupted, shutting down.")
        finally:
            server_socket.close()
            print("Socket closed.")

def tcp_client(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        try:
            client_socket.connect((host, port))
            print(f"Connected to TCP server {host}:{port}")
            while True:
                message = input("You: ")
                send_message(client_socket, message)
                data = receive_full_message(client_socket)
                print(f"Received ({len(data)} bytes): {data.decode()}")
        except KeyboardInterrupt:
            print("\nClient interrupted, shutting down.")
        finally:
            client_socket.close()
            print("Socket closed.")

def udp_server(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
        server_socket.bind((host, port))
        print(f"UDP server listening on {host}:{port}")
        try:
            while True:
                data, addr = server_socket.recvfrom(1024)
                print(f"Received from {addr}: {data.decode()}")
                message = input("You: ")
                server_socket.sendto(message.encode(), addr)
        except KeyboardInterrupt:
            print("\nServer interrupted, closing socket.")
        finally:
            server_socket.close()

def udp_client(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
        print(f"Connected to UDP server {host}:{port}")
        try:
            while True:
                message = input("You: ")
                client_socket.sendto(message.encode(), (host, port))
                data, _ = client_socket.recvfrom(1024)
                print(f"Received: {data.decode()}")
        except KeyboardInterrupt:
            print("\nClient interrupted, closing socket.")
        finally:
            client_socket.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="TCP Chat Client-Server")
    parser.add_argument("mode", choices=["tcp_server", "tcp_client", "udp_server", "udp_client"], help="Mode to run the program")
    parser.add_argument("--host", default="127.0.0.1", help="Host IP")
    parser.add_argument("--port", type=int, default=12345, help="Port number")
    args = parser.parse_args()

    try:
        if args.mode == "tcp_server":
            tcp_server(args.host, args.port)
        elif args.mode == "tcp_client":
            tcp_client(args.host, args.port)
        elif args.mode == "udp_server":
            udp_server(args.host, args.port)
        elif args.mode == "udp_client":
            udp_client(args.host, args.port)
    except KeyboardInterrupt:
        print("\nProgram interrupted.")
