import pytest

from upxlink.entities.entities import *

def test_battery_data_parsing():
    data = {  
        "id": "f3fe8882-b666-478e-8e83-38354461ef9c",  
        "name": "BEV battery",  
        "uri": "/car/batteries/f3fe8882-b666-478e-8e83-38354461ef9c",  
        "soc": 84.0,  
        "socUnit": "percent"  
        }
    
    battery = BatteryData.from_json(data, None)
    assert battery.name == "BEV battery"
    assert battery.soc == 84.0

def test_vehicle_info_parsing():
    data = {  
        "id": "eebec8a3-c881-4cd6-a37f-5c4b8326c56d",  
        "name": "info",  
        "uri": "/car/info/eebec8a3-c881-4cd6-a37f-5c4b8326c56d",  
        "vehicleDate": "01 Nov 2025",  
        "vehicleIdenticationNumber": "MATSRSECBFQTIXLFYF",  
        "vehicleTime": "16:19:34",  
        "vehicleType": "VW120",  
        "language": "de"  
    } 

    vehicle_info = VehicleInfo.from_json(data, None)
    assert vehicle_info.vin == "MATSRSECBFQTIXLFYF"
    assert vehicle_info.date == "01 Nov 2025"
    assert vehicle_info.time == "16:19:34"
    assert vehicle_info.type == "VW120"
    assert vehicle_info.language == "de"

def test_range_data_parsing():
    data = {
        "id": "f6426b5c-b992-4b36-ad50-2efe014733ba",
        "name": "BEV range",
        "uri": "/car/ranges/f6426b5c-b992-4b36-ad50-2efe014733ba",
        "value": 189.0,
        "valueUnit": "km",
        "energystorage": {
            "id": "f3fe8882-b666-478e-8e83-38354461ef9c",
            "name": "BEV battery",
            "uri": "/car/batteries/f3fe8882-b666-478e-8e83-38354461ef9c"
        },
        "engine": {
            "id": "cf4f41a4-0677-4a2b-8009-510c5ac13f72",
            "name": "electric",
            "uri": "/car/engines/cf4f41a4-0677-4a2b-8009-510c5ac13f72"
        }
    }

    range_data = RangeData.from_json(data, None)
    assert range_data.name == "BEV range"
    assert range_data.value == 189.0
    assert range_data.unit == "km"