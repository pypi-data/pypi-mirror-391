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

import json
import requests

from .ssl import SSLAdapter, build_ssl_context, SSLContextTarget
from .credentials import CredentialsManager, Credentials
from .entities import *

from mibbridge import MIBBridge
import bluetooth

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from .interface import Interface

class upXlinkError(Exception):
    pass

class Connection:
    session : requests.Session | None = None
    vin : str | None = None
    credentials : Credentials | None = None
    interface : Interface

    def __init__(self, **kwargs):
        credential_storage  = kwargs.get("credential_storage", None)
        if credential_storage is None:
            raise ValueError("credential_storage must be provided")
        self.credentials_storage : CredentialsManager = credential_storage
        
        self.host = kwargs.get("host", "127.0.0.1")
        self.http_port = kwargs.get("http_port", 4080)
        self.https_port = kwargs.get("https_port", 4443)

        self.interface = self.create_interface()

    def get(self, uri : str) -> bytes:
        url = f"https://{self.host}:{self.https_port}/{uri}"
        if self.session is None:
            raise upXlinkError("Not connected")
        result = self.session.get(url, verify=False).content
        return result
    
    def post(self, uri: str, data: dict) -> bytes:
        url = f"https://{self.host}:{self.https_port}/{uri}"
        if self.session is None:
            raise upXlinkError("Not connected")
        result = self.session.post(url, json=data, verify=False).content
        return result

    def create_interface(self) -> Interface:
        return Interface(get=self.get, post=self.post)   

    def get_vin(self) -> str:
        url = f"http://{self.host}:{self.http_port}/car/info/vin"
        headers = {
            "Connection": "close"
        }
        result = requests.get(url, headers=headers)
        if result.status_code != 200:
            raise upXlinkError("Failed to get VIN")
        else:
            self.vin = result.text.strip()
        return self.vin
    
    def get_registration_url(self) -> str:
        print("Requesting registration url")
        response = requests.post(f"http://{self.host}:{self.http_port}/auth/registration", headers={"Connection": "close"})
        if response.status_code != 303:
            raise upXlinkError("Did not get redirect.")
        registration_url = response.headers.get("content-location", None)
        if registration_url is None:
            raise upXlinkError("No Location header in registration response.")
        return registration_url
    
    def register(self) -> Credentials | None:
        if self.vin is None:
            raise upXlinkError("No VIN, cannot register.")

        registration_url = self.get_registration_url()
        context = build_ssl_context(SSLContextTarget.REGISTRATION)

        session = requests.Session()
        session.mount("https://", SSLAdapter(ssl_context=context))
        print("Please confirm registration on the car's display...")
        try:
            r = session.get(f"https://{self.host}:{self.https_port}" + registration_url, headers={"Connection": "close"}, verify=False)
        except Exception as e:
            print("Registration request failed:", e)
            return None

        result = r.content.decode()
        self.credentials = Credentials.from_string(result)

        print("Registered: ", self.credentials)

        self.credentials_storage.store_credentials(self.vin, self.credentials)

        return self.credentials

    def connect(self, uri="/") -> (dict | None):
        self.get_vin()

        if self.vin is None:
            print("Failed to get VIN.")
            return None
        print("Car VIN: ", self.vin)

        self.credentials = self.credentials_storage.get_credentials(self.vin)

        if self.credentials is None:
            print("No credentials found for VIN:", self.vin)
            print("Registering...")
            self.credentials = self.register()
            if self.credentials is not None:
                self.credentials_storage.store_credentials(self.vin, self.credentials)
            else:
                print("Registration failed.")
                return None

        print("Using credentials for VIN ", self.vin)

        context = build_ssl_context(SSLContextTarget.CONNECTION, credentials=self.credentials)
        self.session = requests.Session()
        self.session.mount("https://", SSLAdapter(ssl_context=context))
        r = self.session.get(f"https://{self.host}:{self.https_port}/{uri}", verify=False)

        return json.loads(r.content.decode())

    def close(self):
        if self.session is not None:
            self.session.close()
            self.session = None
            
class Connector():
    running : bool = False

    def __init__(self, connection: Connection, bridge : MIBBridge, bt_sock : bluetooth.BluetoothSocket, mac : str):
        self.connection = connection
        self.bridge = bridge
        self.bt_sock = bt_sock
        self.mac = mac

    @staticmethod
    def create(mac, credential_path = None) -> 'Connector':
        bt_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        bridge = MIBBridge(bt_sock, {4080: 80, 4443: 443})
        credentials = CredentialsManager(credential_path)
        connection = Connection(credential_storage=credentials)
        return Connector(connection, bridge, bt_sock, mac)

    def open(self) -> bool:
        if self.running:
            return True

        self.running = True

        try:
            self._connect_bt()
        except Exception as e:
            print("Bluetooth connection failed.")
            return False

        try:
            self._connect_bridge()
        except Exception as e:
            print("Failed establishing bridge.")
            return False

        if self._connect_connection() is None:
            print("Failed connecting to car via established tunnel.")
            return False

        return True

    def close(self):
        if not self.running:
            return
        self.connection.close()
        self.bridge.stop()
        self.bt_sock.close()
        self.running = False
        
    def _connect_bt(self):
        self.bt_sock.connect((self.mac, 5))

    def _connect_bridge(self):
        self.bridge.start()
        if self.bridge.mapping != {4080: 80, 4443: 443}:
            self.bridge.stop()
            raise upXlinkError("Failed binding all required ports.")

    def _connect_connection(self):
        return self.connection.connect()
