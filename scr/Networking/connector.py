import re
import socket
import threading

from Networking.bits import Bits


class Event:
    def __init__(self, data):
        self.data = data

    def __len__(self):
        return -(-len(self.data)//8)


class Reciever:
    def __init__(self, sock, callback):
        self.running = True
        self.alowed_to_recv = False
        self.callback = callback
        self.sock = sock
        thread = threading.Thread(target=self.start)
        thread.deamon = True
        thread.start()

    def start(self):
        while self.running:
            if self.alowed_to_recv:
                try:
                    data = self.sock.recv(1024)
                    self.generate_event(Bits.from_bytes(data))
                except Exception as error:
                    print(error)
                    raise error

    def go(self):
        self.alowed_to_recv = True

    def stop(self):
        self.alowed_to_recv = False

    def kill(self):
        self.running = False

    def generate_event(self, data):
        event = Event(data)
        self.callback(event)


class Connector:
    def __init__(self, ip=None, port=None, server=False):
        self.connected = False
        self.ip = ip
        self.port = port
        self.our_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.receive_callback = None
        if server:
            if port is None:
                raise ValueError("If server, you need to specify the port.")
            self.our_sock.bind(("localhost", port))
            self.our_sock.listen(1)
            thread = threading.Thread(target=self.wait_for_connection)
            thread.deamon = True
            thread.start()
        elif (ip is None) or (port is None):
            raise ValueError("If not server, you need to specify port and ip.")
        else:
            self.our_sock.connect((ip, port))
            self.their_sock = self.our_sock
            self.recver = Reciever(self.their_sock, self.recieve)
            self.recver.go()
            self.connected = True

    def bind(self, function):
        self.receive_callback = function

    def unbind(self):
        self.receive_callback = None

    def recieve(self, event):
        if self.receive_callback is not None:
            self.receive_callback(event)

    def send_data(self, data):
        if not self.connected:
            return None
            raise ValueError("Socket not connected.")
        self.their_sock.send(data)

    def wait_for_connection(self):
        self.their_sock, self.their_address = self.our_sock.accept()
        self.recver = Reciever(self.their_sock, self.recieve)
        self.recver.go()
        self.connected = True

    def kill(self):
        if self.connected:
            self.recver.stop()
            self.recver.kill()
            try:
                self.our_sock.close()
                self.their_sock.close()
            except:
                pass


def get_ip():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect(("8.8.8.8", 80))
    ip = sock.getsockname()[0]
    sock.close()
    return ip
