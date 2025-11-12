# DevicePort

Describes the State of a port for API.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**port_id** | **str** |  | 
**port_index** | **int** |  | 
**label** | **str** |  | [optional] 
**state_count** | **int** |  | [optional] 
**state_index** | **int** |  | [optional] 
**state_label** | **str** |  | [optional] 

## Example

```python
from DeviceServer.models.device_port import DevicePort

# TODO update the JSON string below
json = "{}"
# create an instance of DevicePort from a JSON string
device_port_instance = DevicePort.from_json(json)
# print the JSON string representation of the object
print(DevicePort.to_json())

# convert the object into a dict
device_port_dict = device_port_instance.to_dict()
# create an instance of DevicePort from a dict
device_port_from_dict = DevicePort.from_dict(device_port_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


