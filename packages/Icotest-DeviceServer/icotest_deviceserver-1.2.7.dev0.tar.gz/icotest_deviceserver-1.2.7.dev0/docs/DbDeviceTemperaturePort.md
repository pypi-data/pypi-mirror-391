# DbDeviceTemperaturePort

Describes State of a temperature port in database

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**device_id** | **str** |  | 
**temperature_port_index** | **int** |  | 
**label** | **str** |  | [optional] 
**temperature_port_id** | **str** |  | 

## Example

```python
from DeviceServer.models.db_device_temperature_port import DbDeviceTemperaturePort

# TODO update the JSON string below
json = "{}"
# create an instance of DbDeviceTemperaturePort from a JSON string
db_device_temperature_port_instance = DbDeviceTemperaturePort.from_json(json)
# print the JSON string representation of the object
print(DbDeviceTemperaturePort.to_json())

# convert the object into a dict
db_device_temperature_port_dict = db_device_temperature_port_instance.to_dict()
# create an instance of DbDeviceTemperaturePort from a dict
db_device_temperature_port_from_dict = DbDeviceTemperaturePort.from_dict(db_device_temperature_port_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


