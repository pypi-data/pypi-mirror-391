# DeviceTemperaturePort

Describes the State of a temperature port for API.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**temperature_port_index** | **int** |  | 
**label** | **str** |  | [optional] 
**temperature_port_id** | **str** |  | 
**value** | **float** |  | [optional] 

## Example

```python
from DeviceServer.models.device_temperature_port import DeviceTemperaturePort

# TODO update the JSON string below
json = "{}"
# create an instance of DeviceTemperaturePort from a JSON string
device_temperature_port_instance = DeviceTemperaturePort.from_json(json)
# print the JSON string representation of the object
print(DeviceTemperaturePort.to_json())

# convert the object into a dict
device_temperature_port_dict = device_temperature_port_instance.to_dict()
# create an instance of DeviceTemperaturePort from a dict
device_temperature_port_from_dict = DeviceTemperaturePort.from_dict(device_temperature_port_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


