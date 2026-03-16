"""UDP-клиент для обмена с сервером симуляции."""
import socket


class UdpConnection:
    """Канал связи с сервером по UDP."""

    def __init__(self, server_host: str = "localhost", server_port: int = 6000):
        self._host = server_host
        self._port = server_port
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.settimeout(3.0)

    def write(self, msg: str) -> None:
        """Отправить строку на сервер."""
        self._sock.sendto(msg.encode(), (self._host, self._port))

    def read_next(self, bufsize: int = 8192) -> str | None:
        """Прочитать следующее сообщение; при таймауте вернуть None."""
        try:
            data, _ = self._sock.recvfrom(bufsize)
            return data.decode()
        except socket.timeout:
            return None

    def close(self) -> None:
        """Закрыть сокет."""
        self._sock.close()
