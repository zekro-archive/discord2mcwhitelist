import socket
from socket import socket as Socket
import struct

# An RCON package looks like this:
# https://wiki.vg/RCON
#
#  1234 5678 9012 345...
# +----+----+----+--------+--+
# |LLLL|IIII|TTTT|PPPPP...|00|
# +----+----+----+--------+--+
#
# L: int -> length(ident + type + payload + padding)
# I: int -> Request ID
# T: int -> Payload Type
# P: char -> ASCII encoded payload
# 0: byte -> null padding byte

DEFAULT_RCON_PORT = 25575
CMD_LOGIN = 3
CMD_RUN = 2
CMD_RESPONSE = 0


class InvalidPacketException(Exception):
    def __init__(self):
        super(InvalidPacketException, self).__init__('invalid padding data')


class AuthenticationException(Exception):
    def __init__(self):
        super(AuthenticationException, self).__init__('login failed')


class Packet:
    ident: int
    cmd: int
    payload: str

    def __init__(self, ident: int, cmd: int, payload: str):
        self.ident = ident
        self.cmd = cmd
        self.payload = payload

    def encode(self) -> bytes:
        data = struct.pack('<ii', self.ident, self.cmd) + \
            self.payload.encode('ascii') + b'\x00\x00'
        ln = struct.pack('<i', len(data))
        return ln + data

    @staticmethod
    def decode(data: bytes) -> (object, int):
        if len(data) < 14:
            return (None, 14)

        ln = struct.unpack('<i', data[:4])[0] + 4
        if len(data) < ln:
            return (None, ln)

        ident, cmd = struct.unpack('<ii', data[4:12])
        payload = data[12:-2].decode('ascii')

        padding = data[-2:]
        if padding != b'\x00\x00':
            raise InvalidPacketException()

        return (Packet(ident, cmd, payload), 0)


class RCON:

    _socket: Socket
    _addr: str
    _port: int
    _passwd: str

    def __init__(self, addr: str, passwd: str):
        self._socket = Socket(socket.AF_INET, socket.SOCK_STREAM)
        self._passwd = passwd
        addr_split = addr.split(':', 1)
        self._addr = addr_split[0]
        self._port = int(addr_split[1]) if len(addr_split) > 1 \
            else DEFAULT_RCON_PORT

    def connect(self):
        self._socket.connect((self._addr, self._port))
        self._login()

    def _send_packet(self, packet: Packet):
        data = packet.encode()
        # print('← {}'.format(data))
        self._socket.sendall(data)

    def _receive_packet(self) -> Packet:
        data = b''
        while True:
            packet, ln = Packet.decode(data)
            if packet and ln == 0:
                return packet
            else:
                while len(data) < ln:
                    data += self._socket.recv(ln - len(data))
                # print('→ {}'.format(data))

    def _login(self):
        self._send_packet(Packet(0, CMD_LOGIN, self._passwd))
        res = self._receive_packet()
        if res.ident != 0:
            raise AuthenticationException()

    def command(self, cmd: str) -> str:
        self._send_packet(Packet(0, CMD_RUN, cmd))
        self._send_packet(Packet(1, CMD_RESPONSE, ''))

        res = ''
        while True:
            packet = self._receive_packet()
            # print(packet.ident)
            if packet.ident != 0:
                break
            res += packet.payload

        return res

    def close(self):
        self._socket.close()
