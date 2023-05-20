from socket import _RetAddress, create_server, socket
from threading import Thread


def main() -> None:
    server_socket: socket = create_server(("localhost", 6379), reuse_port=True)

    while True:
        client_connection: socket
        addr: _RetAddress
        client_connection, addr = server_socket.accept()  # wait for client
        Thread(target=handle_connection, args=(client_connection,)).start()


def handle_connection(client_connection: socket) -> None:
    while True:
        try:
            client_connection.recv(1024)
            client_connection.send(b"+PONG\r\n")
        except ConnectionError:
            break


if __name__ == "__main__":
    main()
