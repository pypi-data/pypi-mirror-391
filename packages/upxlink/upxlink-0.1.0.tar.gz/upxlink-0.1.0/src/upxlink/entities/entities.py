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

from __future__ import annotations

import json
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import Type, TypeVar, Callable

T = TypeVar('T', bound='VehicleData')

from ..interface import Interface

@dataclass
class VehicleData(ABC):
    _interface : Interface = field(repr=False)
    uri : str
    
    @classmethod
    def from_json(cls : Type[T], data: dict, interface: Interface | None) -> T:
        list = cls.get_fields_from_json(data)
        uri = data.get("uri", "")
        list.insert(0, interface)
        list.insert(1, uri)
        return cls(*list)

    @staticmethod 
    @abstractmethod
    def get_from_interface(interface: Interface) -> VehicleData:
        pass

    @staticmethod
    @abstractmethod
    def get_fields_from_json(data: dict) -> list:
        pass

    def refresh(self) -> None:
        if self._interface is None:
            raise ValueError("No interface available to refresh data")
        response = json.loads(self._interface.get(self.uri))
        if response is not None and "data" in response:
            self = self.from_json(response["data"], self._interface)

@dataclass
class BatteryData(VehicleData):
    name: str
    soc: float

    @staticmethod 
    def get_fields_from_json(data: dict) -> list:
        name = data.get("name", "")
        soc = data.get("soc", -1.0)
        return [name, soc]
    
    @staticmethod
    def get_from_interface(interface: Interface, uri="/car/batteries") -> BatteryData:
        response = json.loads(interface.get(uri))
        if response is not None and "data" in response:
            return BatteryData.from_json(response["data"][0], interface)
        else:
            raise ValueError("Failed to get battery data")
    
    def fancy_print(self) -> str:
        r = ""
        r += f"=== Battery ===\n"
        r += f"Name: {self.name}\n"
        r += f"SoC: {self.soc:.2f} %\n"
        r += f"[{'#' * int(self.soc // 5)}{'-' * (20 - int(self.soc // 5))}] \n"
        return r

@dataclass
class VehicleInfo(VehicleData):
    vin: str
    date : str
    time: str
    type : str
    language: str

    @staticmethod
    def get_from_interface(interface: Interface, uri="/car/info") -> VehicleInfo:
        response = json.loads(interface.get(uri))
        if response is not None and "data" in response:
            return VehicleInfo.from_json(response["data"][0], interface)
        else:
            raise ValueError("Failed to get car info")

    @staticmethod 
    def get_fields_from_json(data: dict) -> list:
        vin = data.get("vehicleIdenticationNumber", "")
        date = data.get("vehicleDate", "")
        time = data.get("vehicleTime", "")
        type = data.get("vehicleType", "")
        language = data.get("language", "")
        return [vin, date, time, type, language]
    
    def fancy_print(self) -> str:
        r = ""
        r += f"=== Car Info ===\n"
        r += f"VIN: {self.vin}\n"
        r += f"Type: {self.type}\n"
        r += f"Date & Time: {self.date} {self.time}\n"
        r += f"Language: {self.language}\n"
        return r

@dataclass
class RangeData(VehicleData):
    name : str
    value : float
    unit : str

    @staticmethod
    def get_from_interface(interface: Interface, uri="/car/ranges") -> RangeData:
        response = json.loads(interface.get(uri))
        if response is not None and "data" in response:
            return RangeData.from_json(response["data"][0], interface)
        else:
            raise ValueError("Failed to get range data")

    @staticmethod 
    def get_fields_from_json(data: dict) -> list:
        name = data.get("name", "")
        value = data.get("value", -1.0)
        unit = data.get("valueUnit", "")
        # engine = EngineData.from_json(data.get("engine", {}))
        return [name, value, unit]

    def fancy_print(self) -> str:
        r = ""
        r += f"=== Range ===\n"
        r += f"Name: {self.name}\n"
        r += f"Value: {self.value} {self.unit}\n"
        return r    
