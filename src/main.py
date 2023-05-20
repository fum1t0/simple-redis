from socket import create_server, socket
from threading import Thread
from typing import Any

from domain.model.resp_decoder import RESPDecoder


def main() -> None:
    server_socket: socket = create_server(("localhost", 6379), reuse_port=True)

    while True:
        client_connection: socket
        client_connection, _ = server_socket.accept()  # wait for client
        Thread(target=handle_connection, args=(client_connection,)).start()


def handle_connection(client_connection: socket) -> None:
    while True:
        try:
            data: bytes | list[Any] = RESPDecoder(client_connection).decode()
            assert type(data[0]) is bytes
            command: bytes = data[0]

            match command:
                case b"ping":
                    client_connection.send(b"+PONG\r\n")
                case b"echo":
                    args = data[1:]
                    assert type(args[0]) is bytes
                    client_connection.send(b"$%d\r\n%b\r\n" % (len(args[0]), args[0]))
                case _:
                    client_connection.send(b"-ERR unknown command\r\n")
        except ConnectionError:
            break


if __name__ == "__main__":
    main()
