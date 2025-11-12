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

import ssl
from requests.adapters import HTTPAdapter
from urllib3 import PoolManager
import enum

class SSLContextTarget(enum.Enum):
    REGISTRATION = 1
    CONNECTION = 2

def build_ssl_context(target : SSLContextTarget, credentials = None) -> ssl.SSLContext:
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.maximum_version = ssl.TLSVersion.TLSv1_2
    context.options &= ~ssl.OP_NO_TLSv1_2
    context.options |= getattr(ssl, "OP_LEGACY_SERVER_CONNECT", 0) # UnsafeLegacyServerConnect

    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    if target == SSLContextTarget.REGISTRATION:
        context.set_ciphers("ECDHE-RSA-AES128-GCM-SHA256")
    elif target == SSLContextTarget.CONNECTION:
        if credentials is None:
            raise ValueError("Credentials must be provided for upXlinkSSLContextTarget.CONNECTION")
        context.set_ciphers("PSK-AES128-CBC-SHA256")
        context.set_psk_client_callback(lambda hint: (credentials.username.encode(), credentials.password.encode()))

    return context

class SSLAdapter(HTTPAdapter):
    def __init__(self, ssl_context=None, **kwargs):
        self.ssl_context = ssl_context
        super().__init__(**kwargs)

    def init_poolmanager(self, *args, **kwargs):
        kwargs['ssl_context'] = self.ssl_context
        return super().init_poolmanager(*args, **kwargs)

    def proxy_manager_for(self, *args, **kwargs):
        kwargs['ssl_context'] = self.ssl_context
        return super().proxy_manager_for(*args, **kwargs)