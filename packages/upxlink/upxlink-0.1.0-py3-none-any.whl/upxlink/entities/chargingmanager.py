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
from upxlink.interface import Interface
from .entities import VehicleData
from datetime import datetime
from dataclasses import dataclass
import json
from enum import Enum

from ..interface import Interface

class WeekdayArray:
    array: list[bool]

    def __init__(self, weekdays: list[bool]):
        if len(weekdays) != 7:
            raise ValueError("WeekdayArray must have exactly 7 boolean values")
        self.array = weekdays
        
    @staticmethod
    def from_string_list(string_list: list[str]) -> 'WeekdayArray':
        mapping = {
            "monday": 0,
            "tuesday": 1,
            "wednesday": 2,
            "thursday": 3,
            "friday": 4,
            "saturday": 5,
            "sunday": 6
        }
        weekdays = [False] * 7
        for day in string_list:
            day_lower = day.lower()
            if day_lower in mapping:
                weekdays[mapping[day_lower]] = True
        return WeekdayArray(weekdays)

    def to_string_list(self) -> list[str]:
        mapping = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday"
        ]
        return [mapping[i] for i, active in enumerate(self.array) if active]
    
    def to_char_string(self) -> str:
        charlist = ['M', 'T', 'W', 'T', 'F', 'S', 'S']
        return ''.join([charlist[i] if active else '-' for i, active in enumerate(self.array)])

class ChargingManagerProfileTargetLevel(Enum):
    FIFTY_PERCENT = 50
    SIXTY_PERCENT = 60
    SEVENTY_PERCENT = 70
    EIGHTY_PERCENT = 80
    NINETY_PERCENT = 90
    HUNDRED_PERCENT = 100

class ChargingManagerProfileMinLevel(Enum):
    ZERO_PERCENT = 0
    TEN_PERCENT = 10
    TWENTY_PERCENT = 20
    THIRTY_PERCENT = 30
    FORTY_PERCENT = 40
    FIFTY_PERCENT = 50
    SIXTY_PERCENT = 60
    SEVENTY_PERCENT = 70
    EIGHTY_PERCENT = 80
    NINETY_PERCENT = 90
    HUNDRED_PERCENT = 100

class ChargingManagerProfileOperations(Enum):
    NOTHING = []
    CHARGE = ["charge"]
    CLIMATE = ["climate"]
    CHARGE_AND_CLIMATE = ["charge", "climate"]

class ChargingManagerProfileMaxCurrent(Enum):
    FIVE_AMPS = 5
    TEN_AMPS = 10
    THIRTEEN_AMPS = 13
    SIXTEEN_AMPS = 16
    THIRTY_TWO_AMPS = 32

class ChargingManagerProfileTemperature(Enum):
    LO = 15.0
    SIXTEEN = 16.0
    SEVENTEEN = 17.0
    EIGHTEEN = 18.0
    NINETEEN = 19.0
    TWENTY = 20.0
    TWENTY_ONE = 21.0
    TWENTY_TWO = 22.0
    TWENTY_THREE = 23.0
    TWENTY_FOUR = 24.0
    TWENTY_FIVE = 25.0
    TWENTY_SIX = 26.0
    TWENTY_SEVEN = 27.0
    TWENTY_EIGHT = 28.0
    TWENTY_NINE = 29.0
    HI = 30.0

@dataclass
class ChargingManagerPowerProvider(VehicleData):
    id: str
    cyclic: bool
    weekdays: WeekdayArray
    start_time: datetime
    end_time: datetime

    @staticmethod
    def get_fields_from_json(data: dict) -> list:
        id = data.get("id", "")
        cyclic = data.get("cyclic", False)
        weekdays = WeekdayArray.from_string_list(data.get("weekdays", []))
        start_time_str = data.get("preferredTimeStart", None)
        start_time = datetime.strptime(start_time_str, "%H:%M:%S") if start_time_str else None
        end_time_str = data.get("preferredTimeEnd", None)
        end_time = datetime.strptime(end_time_str, "%H:%M:%S") if end_time_str else None

        list = [id, cyclic, weekdays, start_time, end_time]
        if None in list:
            raise ValueError("Missing required fields in ChargingManagerPowerProvider JSON data")

        return list
    
    @staticmethod
    def get_from_interface(interface: Interface, uri=None) -> "ChargingManagerPowerProvider":
        if uri is None:
            raise ValueError("uri must not be None.")
        
        response = json.loads(interface.get(uri))
        return ChargingManagerPowerProvider.from_json(response, interface)
    
    def pretty_print(self, indentation=0, verbose=True, print_id=False) -> str:
        i = ' ' * indentation

        if verbose:
            r = ""
            r += f"{i}=== Power Provider ===\n"
            r += f"{i}ID: {self.id}\n"
            r += f"{i}URI: {self.uri}\n"
            r += f"{i}Cyclic: {self.cyclic}\n"
            r += f"{i}Weekdays: {', '.join(self.weekdays.to_string_list())}\n"
            r += f"{i}Start Time: {self.start_time.strftime('%H:%M:%S')}\n"
            r += f"{i}End Time: {self.end_time.strftime('%H:%M:%S')}\n"
        else:
            printable_id = f" ({self.id})" if print_id else ""
            cyclic_indicator = "[cycl]" if self.cyclic else "[once]"
            r = f"{i}- {cyclic_indicator} {self.start_time.strftime('%H:%M:%S')} - {self.end_time.strftime('%H:%M:%S')} @ {self.weekdays.to_char_string()}{printable_id}"
        return r

@dataclass
class ChargingManagerProfile(VehicleData):
    name : str
    id : str
    target_level : ChargingManagerProfileTargetLevel
    operations : ChargingManagerProfileOperations
    max_current : ChargingManagerProfileMaxCurrent
    power_provider : str | ChargingManagerPowerProvider | None

    @staticmethod
    def get_fields_from_json(data: dict) -> list:
        name = data.get("name", "")
        id = data.get("id", "")
        target_level_value = data.get("targetLevel", None)
        target_level = ChargingManagerProfileTargetLevel(target_level_value) if target_level_value else None
        operations_value = data.get("operations", [])
        operations = ChargingManagerProfileOperations(operations_value) if operations_value else None
        max_current_value = data.get("maxCurrent", None)
        max_current = ChargingManagerProfileMaxCurrent(max_current_value) if max_current_value else None

        list = [name, id, target_level, operations, max_current]

        if None in list:
            raise ValueError("Missing required fields in ChargingManagerProfile JSON data")

        power_provider_data = data.get("powerProvider", None)
        power_provider = power_provider_data.get("id", "") if power_provider_data else None
        list.append(power_provider)

        return list

    @staticmethod
    def get_from_interface(interface: Interface, uri=None) -> "ChargingManagerProfile":
        if uri is None:
            raise ValueError("uri must not be None.")
        
        response = json.loads(interface.get(uri))
        return ChargingManagerProfile.from_json(response, interface)
    
    def pretty_print(self, indentation=0, verbose=True, print_id=False) -> str:
        i = ' ' * indentation

        if verbose:
            r = ""
            r += f"{i}=== Charging Manager Profile ===\n"
            r += f"{i}Name: {self.name}\n"
            r += f"{i}ID: {self.id}\n"
            r += f"{i}URI: {self.uri}\n"
            r += f"{i}Target Level: {self.target_level.name} ({self.target_level.value}%)\n"
            r += f"{i}Operations: {', '.join(self.operations.value)}\n"
            r += f"{i}Max Current: {self.max_current.name} ({self.max_current.value}A)\n"
            if isinstance(self.power_provider, ChargingManagerPowerProvider):
                r += self.power_provider.pretty_print(indentation=indentation + 1)
            elif isinstance(self.power_provider, str):
                r += f"{i}Power Provider ID: {self.power_provider}\n"
            else:
                r += f"{i}Power Provider: None\n"
        else:
            operations_indicator = ""
            if self.operations == ChargingManagerProfileOperations.CHARGE:
                operations_indicator = f"🔌,--/--"
            elif self.operations == ChargingManagerProfileOperations.CLIMATE:
                operations_indicator = f"--,❄️/🔥"
            elif self.operations == ChargingManagerProfileOperations.CHARGE_AND_CLIMATE:
                operations_indicator = f"🔌,❄️/🔥"

            printable_id = f" ({self.id})" if print_id else ""

            r = f"{i}- \"{self.name:<20}\": {self.target_level.value:3}% @ {self.max_current.value:2}A, ops:({operations_indicator}){printable_id}"
        return r
    
    def resolve_power_provider(self, list: list[ChargingManagerPowerProvider]) -> None:
        if isinstance(self.power_provider, str):
            for provider in list:
                if provider.id == self.power_provider:
                    self.power_provider = provider
                    return
    
@dataclass
class ChargingManagerDefaultProfile(VehicleData):
    climate_on_battery : bool
    max_current : ChargingManagerProfileMaxCurrent
    min_level : ChargingManagerProfileMinLevel
    temperature : ChargingManagerProfileTemperature

    @staticmethod
    def get_fields_from_json(data: dict) -> list:
        operations_value = data.get("operations", None) 
        climate_on_battery = "climateExtSupply" in operations_value if operations_value else None
        max_current_value = data.get("maxCurrent", None)
        max_current = ChargingManagerProfileMaxCurrent(max_current_value) if max_current_value else None
        min_level_value = data.get("minLevel", None)
        min_level = ChargingManagerProfileMinLevel(min_level_value) if min_level_value else None
        temperature_value = data.get("temperature", None)
        temperature = ChargingManagerProfileTemperature(temperature_value) if temperature_value else None

        list = [climate_on_battery, max_current, min_level, temperature]

        if None in list:
            raise ValueError("Missing required fields in ChargingManagerDefaultProfile JSON data")

        return list

    @staticmethod 
    def get_from_interface(interface: Interface, uri=None) -> "ChargingManagerDefaultProfile":
        if uri is None:
            raise ValueError("uri must not be None.")
        
        response = json.loads(interface.get(uri))
        return ChargingManagerDefaultProfile.from_json(response, interface)
    
    def pretty_print(self, indentation=0, verbose=True, print_id=False) -> str:
        i = ' ' * indentation

        r = ""
        if verbose:
            r += f"{i}=== Charging Manager Default Profile ===\n"
        r += f"{i}Climate on Battery: {self.climate_on_battery}\n"
        r += f"{i}Max Current: {self.max_current.value:2}A\n"
        r += f"{i}Min Level: {self.min_level.value:3}%\n"
        r += f"{i}Temperature: {self.temperature.value:2}°C\n"
        return r

@dataclass
class ChargingManagerTimer(VehicleData):
    id : str
    index : int
    active : bool
    cyclic : bool
    weekdays : WeekdayArray
    departure_time : datetime
    departure_date : datetime | None
    profile : str | ChargingManagerProfile | None

    @staticmethod
    def get_fields_from_json(data: dict) -> list:
        id = data.get("id", "")
        name_value = data.get("name", "")
        index = int(name_value[-1]) if name_value else None
        state_value = data.get("state", "")
        active = True if state_value == "scheduled" else False
        cyclic_value = data.get("cyclic", False)
        cyclic = True if cyclic_value else False
        weekdays_value = data.get("weekdays", None)
        weekdays = WeekdayArray.from_string_list(weekdays_value) if weekdays_value else None
        departure_time_value = data.get("departureTime", None)
        departure_time = datetime.strptime(departure_time_value, "%H:%M:%S") if departure_time_value else None
        departure_date_value = data.get("departureDate", None)
        departure_date = datetime.strptime(departure_date_value, "%d %b %Y") if departure_date_value else None

        list = [id, index, active, cyclic, weekdays, departure_time]

        if None in list:
            raise ValueError("Missing required fields in ChargingManagerTimer JSON data")
        
        if not cyclic and departure_date is None:
            raise ValueError("Non-cyclic timers must not have a departure date.")

        profile_data = data.get("profile", None)
        profile = profile_data.get("id", "") if profile_data else None

        list.append(departure_date)
        list.append(profile)

        return list

    @staticmethod
    def get_from_interface(interface: Interface, uri=None) -> "ChargingManagerTimer":
        if uri is None:
            raise ValueError("uri must not be None.")
        
        response = json.loads(interface.get(uri))
        return ChargingManagerTimer.from_json(response, interface)
    
    def pretty_print(self, indentation=0, verbose=True, print_id=False) -> str:
        i = ' ' * indentation

        if verbose:
            r = ""
            r += f"{i}=== Charging Manager Timer ===\n"
            r += f"{i}Index: {self.index}\n"
            r += f"{i}Active: {self.active}\n"
            r += f"{i}Cyclic: {self.cyclic}\n"
            r += f"{i}Weekdays: {', '.join(self.weekdays.to_string_list())}\n"
            r += f"{i}Departure Time: {self.departure_time.strftime('%H:%M:%S')}\n"
            if self.departure_date:
                r += f"{i}Departure Date: {self.departure_date.strftime('%d %b %Y')}\n"
            else:
                r += f"{i}Departure Date: None\n"
            if isinstance(self.profile, ChargingManagerProfile):
                r += self.profile.pretty_print(indentation=indentation + 1)
            elif isinstance(self.profile, str):
                r += f"{i}Profile ID: {self.profile}\n"
            else:
                r += f"{i}Profile: None\n"
        else:
            cyclic_indicator = "[cycl]" if self.cyclic else "[once]"
            active_indicator = "[X]" if self.active else "[ ]"
            if self.profile != None:
                profile_description = f"\"{self.profile.name:<20}\"" if isinstance(self.profile, ChargingManagerProfile) else "id:" + self.profile
            else:
                profile_description = "No Profile (?!)"
            printable_id = f" ({self.id})" if print_id else ""
            r = f"{i}- {active_indicator} {cyclic_indicator} {self.departure_time.strftime('%H:%M:%S')} @ {self.weekdays.to_char_string()} for {profile_description}{printable_id}"
        return r
    
    def resolve_profile(self, list: list[ChargingManagerProfile]) -> None:
        if isinstance(self.profile, str):
            for profile in list:
                if profile.id == self.profile:
                    self.profile = profile
                    return
    
class ChargingManager():
    providers : list[ChargingManagerPowerProvider]
    profiles : list[ChargingManagerProfile]
    default_profile : ChargingManagerDefaultProfile
    timers : list[ChargingManagerTimer]
    _interface : Interface

    @staticmethod
    def _get_providers(interface: Interface) -> list[ChargingManagerPowerProvider]:
        response = json.loads(interface.get("/chargingmanager/providers"))
        providers = []
        if response is not None and "data" in response:
            for item in response["data"]:
                provider = ChargingManagerPowerProvider.from_json(item, interface)
                providers.append(provider)
        else:
            raise ValueError("Failed to get charging manager power providers")
        return providers

    @staticmethod 
    def _get_profiles(interface: Interface) -> list[ChargingManagerProfile]:
        response = json.loads(interface.get("/chargingmanager/profiles"))
        profiles = []
        if response is not None and "data" in response:
            default = True
            for item in response["data"]:
                if default:
                    default = False
                    continue  # Skip first
                profile = ChargingManagerProfile.from_json(item, interface)
                profiles.append(profile)
        else:
            raise ValueError("Failed to get charging manager profiles")
        return profiles
    
    @staticmethod
    def _get_default_profile(interface: Interface) -> ChargingManagerDefaultProfile:
        response = json.loads(interface.get("/chargingmanager/profiles"))
        if response is not None and "data" in response:
            default_data = response["data"][0]
            return ChargingManagerDefaultProfile.from_json(default_data, interface)
        else:
            raise ValueError("Failed to get default charging manager profile")

    @staticmethod    
    def _get_timers(interface: Interface) -> list[ChargingManagerTimer]:
        response = json.loads(interface.get("/chargingmanager/timers"))
        timers = []
        if response is not None and "data" in response:
            for item in response["data"]:
                timer = ChargingManagerTimer.from_json(item, interface)
                timers.append(timer)
        else:
            raise ValueError("Failed to get charging manager timers")
        return timers

    def __init__(self, interface: Interface):
        self._interface = interface
        self.providers = self._get_providers(interface)
        self.profiles = self._get_profiles(interface)
        self.default_profile = self._get_default_profile(interface)
        self.timers = self._get_timers(interface)

        for profile in self.profiles:
            profile.resolve_power_provider(self.providers)

        for timer in self.timers:
            timer.resolve_profile(self.profiles)

    def pretty_print(self, indentation=0, verbose=False, print_ids=False) -> str:
        i = ' ' * indentation

        r = ""
        r += f"{i}=== Charging Manager ===\n"

        r += f"{i}--- Default Profile ---\n"
        r += self.default_profile.pretty_print(indentation=indentation + 1, verbose=verbose, print_id=print_ids)
        r += "\n"

        r += f"{i}--- Timers ---\n"
        for timer in self.timers:
            r += timer.pretty_print(indentation=indentation + 1, verbose=verbose, print_id=print_ids)
            r += "\n"
        r += "\n"

        r += f"{i}--- Profiles ---\n"
        for profile in self.profiles:
            r += profile.pretty_print(indentation=indentation + 1, verbose=verbose, print_id=print_ids)
            r += "\n"
        r += "\n"

        r += f"{i}--- Power Providers ---\n"
        for provider in self.providers:
            r += provider.pretty_print(indentation=indentation + 1, verbose=verbose, print_id=print_ids)
            r += "\n"
        r += "\n"
        return r