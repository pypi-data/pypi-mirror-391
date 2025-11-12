"""
    This file is part of MIBBridge
    Copyright (C) 2025 Alexander Hahn

    This program is free software: you can redistribute it and/or modify
    it under the terms of the European Union Public License (EUPL), version 1.2.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    European Union Public License for more details.

    You should have received a copy of the European Union Public License
    along with this program. If not, see <https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12>.
"""

import socket, threading
import bluetooth
import enum
import logging

class CarSegmentType(enum.Enum):
    TRANSMIT = 0
    OPEN = 1
    CLOSE = 2
    HEARTBEAT = 3
    
class IncompleteCarSegmentError(Exception):
    pass

class CarSegment:
    def __init__(self, a:int, b: int, car_segment_type: CarSegmentType, data: bytes):
        self.a = a
        self.b = b
        self.car_segment_type = car_segment_type
        self.data = data

    @staticmethod
    def from_bytes(data: bytes):
        if len(data) < 3:
            raise IncompleteCarSegmentError("Frame too short, size: "+ str(len(data)))
        else:
            a = int.from_bytes(data[0:2], 'little')
            car_segment_type = CarSegmentType(int.from_bytes(data[2:3], 'little'))

        if car_segment_type == CarSegmentType.HEARTBEAT or car_segment_type == CarSegmentType.CLOSE:
            return CarSegment(a, 0, car_segment_type, b'')

        if car_segment_type == CarSegmentType.OPEN:
            if len(data) < 5:
                raise IncompleteCarSegmentError("Frame too short for OPEN segment")
            b = int.from_bytes(data[3:5], 'little')
            return CarSegment(a, b, car_segment_type, b'')

        # car_segment_type == CarSegmentType.TRANSMIT

        if len(data) < 5:
            raise IncompleteCarSegmentError("Frame too short for TRANSMIT segment")

        b = int.from_bytes(data[3:5], 'little')
        data = data[5:5+b]
        
        if len(data) < b:
            raise IncompleteCarSegmentError("Announced data length larger than data available")
        return CarSegment(a, b, car_segment_type, data)

    def to_bytes(self) -> bytes:
        if self.car_segment_type == CarSegmentType.HEARTBEAT:
            return self.a.to_bytes(2, 'little') + self.car_segment_type.value.to_bytes(1, 'little')
        else:
            rval = b''
            rval += self.a.to_bytes(2, 'little')
            rval += self.car_segment_type.value.to_bytes(1, 'little')
            if self.car_segment_type == CarSegmentType.OPEN:
                rval += self.b.to_bytes(2, 'little')
            elif self.car_segment_type == CarSegmentType.TRANSMIT:
                rval += (len(self.data)).to_bytes(2, 'little')
                rval += self.data

            return rval

class CarConnectionState(enum.Enum):
    CLOSED_BY_CAR = 1
    CLOSED_BY_CLIENT = 2
    OPEN = 3

class CarConnection:
    def __init__(self, lport:int, bport:int, rport:int, connection_socket: socket.socket):
        self.lport = lport # client source port (connection comes from...)
        self.bport = bport # bridge port (where this proxy listens on...)
        self.rport = rport # remote port (car side)
        self.connection_socket = connection_socket
        self.state = CarConnectionState.OPEN

class LogLevel(enum.Enum):
    DEBUG = 1
    INFO = 2
    WARNING = 3
    ERROR = 4
    CRITICAL = 5

class MIBBridge:
    def __init__(self, car_socket : (bluetooth.BluetoothSocket | socket.socket), mapping: dict[int, int], logger=logging.getLogger("MIBBridge")):
        self.car_socket = car_socket
        self.car_socket_send_lock = threading.Lock()
        self.mapping = mapping

        self.connections = {}
        self.connections_lock = threading.Lock()
        self.tcp_sockets = {}

        self._tcp_socket_loop_threads = []
        self._tcp_connection_threads = []

        self.running = False
        self.running_bt_loop = False

        self.logger = logger
        
    def log(self, level: LogLevel, message: str):
        if self.logger is not None:
            if level == LogLevel.DEBUG:
                self.logger.debug(message)
            elif level == LogLevel.INFO:
                self.logger.info(message)
            elif level == LogLevel.WARNING:
                self.logger.warning(message)
            elif level == LogLevel.ERROR:
                self.logger.error(message)
            elif level == LogLevel.CRITICAL:
                self.logger.critical(message)
        
    def unregister_connection(self, lport: int):
        with self.connections_lock:
            if lport in self.connections:
                del self.connections[lport]

    def register_connection(self, connection: CarConnection):
        with self.connections_lock:
            self.connections[connection.lport] = connection
            
    def get_connection(self, lport: int) -> (CarConnection | None):
        with self.connections_lock:
            return self.connections.get(lport, None)

    def car_send(self, segment: CarSegment):
        with self.car_socket_send_lock:
            self.log(LogLevel.DEBUG, f"Sending data to car: {segment.to_bytes().hex()}")
            self.car_socket.sendall(segment.to_bytes())

    def tcp_socket_loop(self, tcp_socket, bport, rport):
        tcp_socket.settimeout(1.0)
        while self.running:
            try:
                connection_socket, addr = tcp_socket.accept()
            except socket.timeout:
                continue
            t = threading.Thread(target=self.handle_tcp_connection, args=(connection_socket, addr[1], bport, rport))
            t.start()
            self._tcp_connection_threads.append(t)

    def handle_tcp_connection(self, connection_socket, lport, bport, rport): # called on incoming tcp connection
        with connection_socket:
            self.log(LogLevel.INFO, f"New connection: {lport}->{bport}:{rport}")

            segment = CarSegment(lport, rport, CarSegmentType.OPEN, b'')
            self.car_send(segment)

            connection = CarConnection(lport, bport, rport, connection_socket)
            self.register_connection(connection)

            # data send loop
            try:
                tcp_data = connection_socket.recv(65535)
            except Exception as e:
                tcp_data = b''

            while tcp_data:
                segment = CarSegment(lport, rport, CarSegmentType.TRANSMIT, tcp_data)
                self.car_send(segment)
                try:
                    tcp_data = connection_socket.recv(65535)
                except Exception as e:
                    break
            # TCP connection closed

            segment = CarSegment(lport, rport, CarSegmentType.CLOSE, b'')

            if connection.state == CarConnectionState.OPEN:
                self.log(LogLevel.DEBUG, f"Connection {lport}->{bport}:{rport} closed by client, sending CLOSE to car.")
                connection.state = CarConnectionState.CLOSED_BY_CLIENT
                self.car_send(segment)

            if connection.state == CarConnectionState.CLOSED_BY_CAR:
                self.log(LogLevel.DEBUG, "Acknowledging CLOSE initiated by car.")
                self.car_send(segment)
                self.log(LogLevel.INFO, f"Connection {lport}->{bport}:{rport} unregistered.")
                self.unregister_connection(lport)
                
    def handle_car_segment(self, segment: CarSegment):
        if segment.car_segment_type == CarSegmentType.HEARTBEAT:
            self.log(LogLevel.DEBUG, "Returning heartbeat.")
            self.car_send(segment)
            return

        # parsing succeded and not a heartbeat:
        lport = segment.a

        carconnection = self.get_connection(lport)

        if carconnection is not None:
            connection_socket = carconnection.connection_socket

            if segment.car_segment_type == CarSegmentType.TRANSMIT:
                self.log(LogLevel.DEBUG, f"Forwarding data for lport={lport} to client: {segment.data.hex()}")
                try:
                    connection_socket.sendall(segment.data)
                except Exception as e:
                    self.log(LogLevel.ERROR, f"Failed sending data to client. Reason: {str(e)}")

            elif segment.car_segment_type == CarSegmentType.CLOSE:
                if carconnection.state == CarConnectionState.OPEN:
                    self.log(LogLevel.DEBUG, f"CLOSE received from car for lport={lport}, closing connection.")
                    carconnection.state = CarConnectionState.CLOSED_BY_CAR
                    connection_socket.shutdown(socket.SHUT_RDWR)
                    connection_socket.close()

                elif carconnection.state == CarConnectionState.CLOSED_BY_CLIENT:
                    self.log(LogLevel.DEBUG, f"Got acknowledgement of close of {lport}->{carconnection.bport}:{carconnection.rport} from car.")
                    self.log(LogLevel.INFO, f"Connection {lport}->{carconnection.bport}:{carconnection.rport} unregistered.")
                    self.unregister_connection(lport)
        else:
            self.log(LogLevel.WARNING, f"Received segment for unknown connection lport={lport}: {segment.to_bytes().hex()}")

    def car_socket_loop(self): # runs forever
        # initial heartbeat
        self.car_send(CarSegment(0, 0, CarSegmentType.HEARTBEAT, b''))

        self.car_socket.settimeout(1.0)

        buffer = b''

        # keep running until stopped and buffer is empty
        while self.running_bt_loop or buffer:
            try:
                bt_data = self.car_socket.recv(65535)
            except socket.timeout:
                continue
            except bluetooth.btcommon.BluetoothError as e:
                continue
            except Exception as e:
                self.log(LogLevel.ERROR, f"Bluetooth socket error: {str(e)}")
                break

            self.log(LogLevel.DEBUG, f"Received data from car: {bt_data.hex()}")

            buffer += bt_data
            car_segment_buffer = []

            while buffer:
                try:
                    segment = CarSegment.from_bytes(buffer)
                    segment_size = len(segment.to_bytes())
                    buffer = buffer[segment_size:]
                    car_segment_buffer.append(segment)
                except IncompleteCarSegmentError:
                    break
            
            for segment in car_segment_buffer:
                self.handle_car_segment(segment)

    def start(self):
        active_mapping = {}
        for bport, rport in list(self.mapping.items()):
            tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                tcp_socket.bind(("127.0.0.1", bport))
            except Exception as e:
                self.log(LogLevel.ERROR, f"Failed to bind TCP socket for bport={bport}. Dropping port from mapping.")
                try:
                    tcp_socket.close()
                except:
                    pass
                continue
            tcp_socket.listen()
            self.tcp_sockets[bport] = tcp_socket
            active_mapping[bport] = rport

        self.mapping = active_mapping

        # start threads
        self.running = True
        self.running_bt_loop = True

        self._car_socket_thread = threading.Thread(target=self.car_socket_loop, args=())
        self._car_socket_thread.start()

        for bport in self.mapping.keys():
            t = threading.Thread(target=self.tcp_socket_loop, args=(self.tcp_sockets[bport], bport, self.mapping[bport]))
            t.start()
            self._tcp_socket_loop_threads.append(t)

    def stop(self):
        if not self.running:
            return

        # stop listening for connections
        self.running = False
        for t in self._tcp_socket_loop_threads:
            t.join()

        # kill open connections
        for lport in list(self.connections.keys()):
            connection = self.get_connection(lport)
            if connection is not None:
                try:
                    connection.connection_socket.shutdown(socket.SHUT_RDWR)
                    connection.connection_socket.close()
                except:
                    pass
                # for tcp_socket_loop this looks like the client closed the connection
                # unregistering and sending CLOSE will be handled by tcp_socket_loop
        for t in self._tcp_connection_threads:
            t.join()

        # the only thread running now is car_socket_loop
        self.running_bt_loop = False
        self._car_socket_thread.join()