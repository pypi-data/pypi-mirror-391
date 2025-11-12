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

import logging
import socket
import sys
import enum
import re
import bluetooth
import time

from .bridge import MIBBridge
from . import __version__

class AddressType(enum.Enum):
    MAC = 1
    SOCKET = 2
    OTHER = 3

def get_address_type(addr: str) -> AddressType:
    mac_pattern = re.compile(r'^[0-9A-Fa-f]{2}(:[0-9A-Fa-f]{2}){5}$')
    path_pattern = re.compile(r'^/[\w/.-]+$')

    if mac_pattern.match(addr):
        return AddressType.MAC
    elif path_pattern.match(addr):
        return AddressType.SOCKET
    else:
        return AddressType.OTHER

def main():
    if len(sys.argv) > 1:
        addr = sys.argv[1]
        mapping = {4080 : 80, 4443 : 443}
        if len(sys.argv) >= 3:
            s = sys.argv[2]
            try:
                mapping = {int(k): int(v) for k, v in (pair.split(":") for pair in s.split(","))}
            except Exception:
                print("Invalid mapping format. Use e.g. 4080:80,4443:443")
                exit(1)
    else:
        exec_name = sys.argv[0].split("/")[-1]
        print(f"\nUsage: python {exec_name} <bluetooth address> [mapping]\n\n"
              " - Address can be a MAC address or a unix socket path.\n"
              " - Mapping can be provided as <local port>:<remote port> pairs separated by commas, e.g. 4080:80,4443:443 (default)\n"
              "\n"
              "\n"
              f"Version v{__version__}\n"
              "See https://github.com/hahnworks/MIBBridge for more information.\n"
              "Copyright (c) 2025 Alexander Hahn <github.com/hahnworks>\n"
              "This program is licensed under the EUPL v1.2\n"
              );
        exit(1)

    logger = logging.getLogger("MIBBridge")
    logging.basicConfig(level=logging.INFO)

    addr_type = get_address_type(addr)
    if addr_type == AddressType.MAC:
        bt_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        bt_sock.connect((addr, 5))
        print("Bluetooth connected")
    elif addr_type == AddressType.SOCKET:
        bt_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        bt_sock.connect(addr) 
        print("Unix socket connected")
    else:
        print("Invalid address")
        exit(1)

    bridge = MIBBridge(bt_sock, mapping, logger=logger)

    try:
        bridge.start()
        logger.info("MIBBridge started. Press Ctrl+C to stop.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping MIBBridge due to keyboard interrupt...")
    finally:
        bridge.stop()
        logger.info("MIBBridge stopped.")
        try:
            bt_sock.close()
        except Exception:
            pass