from socket import socket
from typing import Any, Union


class ConnectionBuffer:
    def __init__(self, connection: socket) -> None:
        self.connection: socket = connection
        self.buffer: bytes = b""

    def read(self, buffer_size: int) -> bytes:
        if len(self.buffer) < buffer_size:
            data: bytes = self.connection.recv(1024)

            if not data:
                return b""

            self.buffer += data

        data, self.buffer = self.buffer[:buffer_size], self.buffer[buffer_size:]
        return data

    def read_until_delimiter(self, delimiter: bytes) -> bytes:
        while delimiter not in self.buffer:
            data = self.connection.recv(1024)

            if not data:
                return b""

            self.buffer += data

        data_before_delimiter: bytes
        data_before_delimiter, delimiter, self.buffer = self.buffer.partition(delimiter)
        return data_before_delimiter


class RESPDecoder:
    def __init__(self, connection: socket) -> None:
        self.connection: ConnectionBuffer = ConnectionBuffer(connection=connection)

    def decode(self) -> bytes | list[Any]:
        data_type_byte: bytes | None = self.connection.read(1)
        match data_type_byte:
            case b"+":
                return self.decode_simple_string()
            case b"$":
                return self.decode_bulk_string()
            case b"*":
                return self.decode_array()
            case _:
                raise Exception(f"Unknown data type byte: {data_type_byte!r}")

    def decode_simple_string(self) -> bytes:
        return self.connection.read_until_delimiter(b"\r\n")

    def decode_bulk_string(self) -> bytes:
        length_optional: bytes | None = self.connection.read_until_delimiter(b"\r\n")
        if length_optional is None:
            return b""

        bulk_string_length: int = int(length_optional)
        data: bytes = self.connection.read(bulk_string_length)
        assert self.connection.read_until_delimiter(b"\r\n") == b""
        return data

    def decode_array(self) -> list[Union[bytes, list[Any]]]:
        length_optional: bytes | None = self.connection.read_until_delimiter(b"\r\n")
        if length_optional is None:
            return []

        array_length: int = int(length_optional)
        return [self.decode() for _ in range(array_length)]
