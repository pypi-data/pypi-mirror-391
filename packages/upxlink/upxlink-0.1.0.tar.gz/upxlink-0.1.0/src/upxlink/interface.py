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

from typing import Callable

class Interface():
    def __init__(self, get: Callable, post: Callable):
        self.getfunc = get
        self.postfunc = post

    def get(self, uri: str) -> bytes:
        return self.getfunc(uri)
    
    def post(self, uri: str, data: dict) -> bytes:
        return self.postfunc(uri, data)