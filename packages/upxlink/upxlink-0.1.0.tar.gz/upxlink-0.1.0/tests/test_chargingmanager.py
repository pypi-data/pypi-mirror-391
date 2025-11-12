import pytest

from upxlink.entities.chargingmanager import *

def test_profile_parsing_with_power_provider():
    profile_data = {
        "id": "8269b474-006f-43bc-8989-b38c4c2248b0",
        "name": "Ladeort 3",
        "uri": "/chargingmanager/profiles/8269b474-006f-43bc-8989-b38c4c2248b0",
        "operations": [
            "charge",
            "climate"
        ],
        "maxCurrent": 16,
        "minLevel": 0,
        "minType": "level",
        "targetLevel": 100,
        "targetingType": "level",
        "temperature": 10.0,
        "temperatureUnit": "C",
        "powerProvider": {
            "id": "c8876782-d0b6-493f-a975-9f1be7006607",
            "name": "",
            "uri": "/chargingmanager/providers/c8876782-d0b6-493f-a975-9f1be7006607"
        }
    }

    profile = ChargingManagerProfile.from_json(profile_data, None)
    assert profile.uri == "/chargingmanager/profiles/8269b474-006f-43bc-8989-b38c4c2248b0"
    assert profile.name == "Ladeort 3"
    assert profile.id == "8269b474-006f-43bc-8989-b38c4c2248b0"
    assert profile.max_current == ChargingManagerProfileMaxCurrent(16)
    assert profile.target_level == ChargingManagerProfileTargetLevel.HUNDRED_PERCENT
    assert profile.operations == ChargingManagerProfileOperations.CHARGE_AND_CLIMATE
    assert profile.power_provider == "c8876782-d0b6-493f-a975-9f1be7006607"

def test_profile_parsing_without_power_provider():
    profile_data = {
        "id": "63cf948c-a903-47d7-9ee1-05642177be20",
        "name": "Ladelimit 80, HVAC",
        "uri": "/chargingmanager/profiles/63cf948c-a903-47d7-9ee1-05642177be20",
        "operations": [
            "charge",
            "climate"
        ],
        "maxCurrent": 32,
        "minLevel": 0,
        "minType": "level",
        "targetLevel": 80,
        "targetingType": "level",
        "temperature": 10.0,
        "temperatureUnit": "C"
    }

    profile = ChargingManagerProfile.from_json(profile_data, None)
    assert profile.uri == "/chargingmanager/profiles/63cf948c-a903-47d7-9ee1-05642177be20"
    assert profile.name == "Ladelimit 80, HVAC"
    assert profile.id == "63cf948c-a903-47d7-9ee1-05642177be20"
    assert profile.max_current == ChargingManagerProfileMaxCurrent(32)
    assert profile.target_level == ChargingManagerProfileTargetLevel.EIGHTY_PERCENT
    assert profile.operations == ChargingManagerProfileOperations.CHARGE_AND_CLIMATE
    assert profile.power_provider is None

def test_default_profile_parsing():
    profile_data = {
        "id": "3900b210-79cf-4ca1-8280-99a482f2803a",
        "name": "Optionen",
        "uri": "/chargingmanager/profiles/3900b210-79cf-4ca1-8280-99a482f2803a",
        "operations": [
            "climateExtSupply",
            "climate"
        ],
        "maxCurrent": 32,
        "minLevel": 100,
        "minType": "level",
        "targetLevel": 0,
        "targetingType": "level",
        "temperature": 30.0,
        "temperatureUnit": "C"
    }

    profile = ChargingManagerDefaultProfile.from_json(profile_data, None)
    assert profile.uri == "/chargingmanager/profiles/3900b210-79cf-4ca1-8280-99a482f2803a"
    assert profile.max_current == ChargingManagerProfileMaxCurrent.THIRTY_TWO_AMPS
    assert profile.min_level == ChargingManagerProfileMinLevel.HUNDRED_PERCENT
    assert profile.climate_on_battery is True
    assert profile.temperature == ChargingManagerProfileTemperature(30.0)

def test_timer_parsing():
    timer_data = {
        "id": "20a560c1-815e-4f10-873c-160eed6027a6",
        "name": "Timer1",
        "uri": "/chargingmanager/timers/20a560c1-815e-4f10-873c-160eed6027a6",
        "viewoption": {
            "id": "9e390366-55d8-41ad-b5ad-c0f5a577ba2b",
            "name": "chargeTimer_1",
            "uri": "/car/viewoptions/9e390366-55d8-41ad-b5ad-c0f5a577ba2b"
        },
        "state": "idle",
        "departureTime": "06:35:00",
        "profile": {
            "id": "63cf948c-a903-47d7-9ee1-05642177be20",
            "name": "Ladelimit 80, HVAC",
            "uri": "/chargingmanager/profiles/63cf948c-a903-47d7-9ee1-05642177be20"
        },
        "cyclic": True,
        "weekdays": [
            "monday",
            "tuesday",
            "thursday",
            "friday"
        ],
        "chargeScheduleState": "idle",
        "climateScheduleState": "idle"
    }

    timer = ChargingManagerTimer.from_json(timer_data, None)
    assert timer.id == "20a560c1-815e-4f10-873c-160eed6027a6"
    assert timer.index == 1
    assert timer.uri == "/chargingmanager/timers/20a560c1-815e-4f10-873c-160eed6027a6"
    assert timer.active is False
    assert timer.cyclic is True
    assert timer.weekdays.array == WeekdayArray([True, True, False, True, True, False, False]).array
    assert timer.departure_time == datetime.strptime("06:35:00", "%H:%M:%S")
    assert timer.departure_date is None
    assert timer.profile == "63cf948c-a903-47d7-9ee1-05642177be20"

def test_power_provider():
    # Reformatted provider_data for better readability and PEP8 compliance
    provider_data = {
        "id": "c8876782-d0b6-493f-a975-9f1be7006607",
        "name": "",
        "uri": "/chargingmanager/providers/c8876782-d0b6-493f-a975-9f1be7006607",
        "clientName": "",
        "weekdays": [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday"
        ],
        "cyclic": False,
        "preferredTimeStart": "22:00:00",
        "preferredTimeEnd": "05:00:00"
    }

    provider = ChargingManagerPowerProvider.from_json(provider_data, None)
    assert provider.id == "c8876782-d0b6-493f-a975-9f1be7006607"
    assert provider.uri == "/chargingmanager/providers/c8876782-d0b6-493f-a975-9f1be7006607"
    assert provider.cyclic == False
    assert provider.weekdays.array == WeekdayArray([True, True, True, True, True, True, True]).array
    assert provider.start_time == datetime.strptime("22:00:00", "%H:%M:%S")
    assert provider.end_time == datetime.strptime("05:00:00", "%H:%M:%S")
