# DeviceRxBuffer

Device message buffer model used for API and database

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**locator** | **str** |  | 
**state** | **str** |  | [optional] 
**timestamp_db_write** | **int** |  | [optional] 
**timestamp_hid_message** | **int** |  | [optional] 

## Example

```python
from DeviceServer.models.device_rx_buffer import DeviceRxBuffer

# TODO update the JSON string below
json = "{}"
# create an instance of DeviceRxBuffer from a JSON string
device_rx_buffer_instance = DeviceRxBuffer.from_json(json)
# print the JSON string representation of the object
print(DeviceRxBuffer.to_json())

# convert the object into a dict
device_rx_buffer_dict = device_rx_buffer_instance.to_dict()
# create an instance of DeviceRxBuffer from a dict
device_rx_buffer_from_dict = DeviceRxBuffer.from_dict(device_rx_buffer_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


