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

from pathlib import Path

class Credentials:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

    @staticmethod
    def from_string(s: str):
        parts = s.strip().split(",")
        if len(parts) != 2:
            raise ValueError("Invalid credentials string")
        return Credentials(parts[0], parts[1])

    def __repr__(self):
        return f"{self.username},{self.password}"
    
    def __str__(self) -> str:
        return self.__repr__()
    
class CredentialsManager:
    def __init__(self, filename=None):
        if filename is None:
            filename = str(Path.home() / ".upxlink_credentials")
        self.filename = filename

    def touch_credentials_file(self):
        try:
            open(self.filename, 'a').close()
        except:
            print(f"Failed accessing credential storage file {self.filename}")

    def load_credentials_dict(self) -> dict[str, Credentials]:
        self._credentials = {}
        self.touch_credentials_file()
        
        with open(self.filename, 'r') as f:
            for line in f:
                try:
                    vin, cred_str = line.strip().split('=')
                except:
                    continue
                self._credentials[vin] = Credentials.from_string(cred_str)
        return self._credentials
    
    def save_credentials_dict(self, credentials: dict[str, Credentials]):
        self.touch_credentials_file()

        with open(self.filename, 'w') as f:
            for vin, cred in credentials.items():
                f.write(f"{vin}={cred}\n")
    
    def get_credentials(self, vin: str) -> Credentials | None:
        self._credentials = self.load_credentials_dict()
        return self._credentials.get(vin, None)
    
    def store_credentials(self, vin: str, credentials: Credentials):
        self._credentials = self.load_credentials_dict()
        self._credentials[vin] = credentials
        self.save_credentials_dict(self._credentials)