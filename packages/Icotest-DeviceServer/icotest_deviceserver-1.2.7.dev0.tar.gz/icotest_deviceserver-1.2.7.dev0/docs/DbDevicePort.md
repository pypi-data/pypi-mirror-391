# DbDevicePort

Describes State of a port in database

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**port_id** | **str** |  | 
**port_index** | **int** |  | 
**device_id** | **str** |  | 
**label** | **str** |  | [optional] 
**state_index** | **int** |  | [optional] 

## Example

```python
from DeviceServer.models.db_device_port import DbDevicePort

# TODO update the JSON string below
json = "{}"
# create an instance of DbDevicePort from a JSON string
db_device_port_instance = DbDevicePort.from_json(json)
# print the JSON string representation of the object
print(DbDevicePort.to_json())

# convert the object into a dict
db_device_port_dict = db_device_port_instance.to_dict()
# create an instance of DbDevicePort from a dict
db_device_port_from_dict = DbDevicePort.from_dict(db_device_port_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


