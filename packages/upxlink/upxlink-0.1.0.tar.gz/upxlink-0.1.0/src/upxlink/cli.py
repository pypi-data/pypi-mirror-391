"""
    This file is part of upXlink
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

import sys
import enum
import re
import json

import cmd

from .entities import *
from .connection import Connector
from . import __version__

def is_mac_address(s: str) -> bool:
    return re.compile(r'^[0-9A-Fa-f]{2}(:[0-9A-Fa-f]{2}){5}$').match(s) is not None

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

class upXlinkCmdline(cmd.Cmd):
    intro = f"upXlink version {__version__}\n"
    intro += "Type help or ? to list commands.\n"

    def __init__(self, connector: Connector):
        super().__init__()
        self.connector = connector
        self.connection = connector.connection
        self.prompt = f"(upxlink@{self.connection.vin})> "

    def _pretty_print_response(self, response: str | bytes):
        try:
            parsed = json.loads(response)
        except json.JSONDecodeError:
            print(response)
        else:
            print(json.dumps(parsed, indent=2))

    def do_get(self, line):
        """Get data from the car. Usage: get <uri>"""
        uri = line.strip()
        if not uri:
            print("Usage: get <uri>")
            return
        try:
            response = self.connection.get(uri)
            self._pretty_print_response(response)
        except Exception as e:
            print(f"Error: {e}")

    def do_post(self, line):
        """Post data to the car. Usage: post <uri> <json_data>"""
        parts = line.strip().split(' ', 1)
        if len(parts) != 2:
            print("Usage: post <uri> <json_data>")
            return
        uri, json_data = parts
        try:
            data_dict = json.loads(json_data)
        except json.JSONDecodeError as e:
            print(f"Invalid JSON data: {e}")
            return
        try:
            response = self.connection.post(uri, data_dict)
            self._pretty_print_response(response)
        except Exception as e:
            print(f"Error: {e}")

    def do_about(self, line):
        """Show information about the upXlink tool."""
        print(f"upXlink version {__version__}")
        print("A tool to interact with your vehicle")
        print("Copyright (C) 2025 Alexander Hahn (github.com/hahnworks)")

        print(
            "This program is free software: you can redistribute it and/or modify "
            "it under the terms of the European Union Public License (EUPL), version 1.2."
        )
        print(
            "This program is distributed in the hope that it will be useful, "
            "but WITHOUT ANY WARRANTY; without even the implied warranty of "
            "MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. "
            "See the European Union Public License for more details."
        )
            
    def do_battery(self, line):
        """Get battery status."""
        try:
            battery = BatteryData.get_from_interface(self.connection.interface)
            print(battery.fancy_print())
        except Exception as e:
            print(f"Error: {e}")

    def do_info(self, line):
        """Get vehicle info."""
        try:
            vehicleinfo = VehicleInfo.get_from_interface(self.connection.interface)
            print(vehicleinfo.fancy_print())
        except Exception as e:
            print(f"Error: {e}")

    def do_range(self, line):
        """Get vehicle range."""
        try:
            rangedata = RangeData.get_from_interface(self.connection.interface)
            print(rangedata.fancy_print())
        except Exception as e:
            print(f"Error: {e}")

    def do_chargingmanager(self, line):
        try:
            charging_manager = ChargingManager(self.connection.interface)
            print(charging_manager.pretty_print())
        except Exception as e:
            print(f"Error: {e}")

    def do_EOF(self, line):
        """Exit the command line interface."""
        print("Exiting.")
        return True

    def do_exit(self, line):
        """Exit the command line interface."""
        print("Exiting.")
        return True

def main():
    if len(sys.argv) < 2 or not is_mac_address(sys.argv[1]):
        print(f"Usage: python {sys.argv[0]} <bluetooth-mac-address>")
        exit(1)

    addr = sys.argv[1]

    # set up interface
    connector = Connector.create(addr)
    if not connector.open():
        print("Failed to open connection to car.")
        connector.close()
        exit(1)

    cli = upXlinkCmdline(connector)
    cli.cmdloop()

    connector.close()

if __name__ == "__main__":
    main()
    exit(0)

