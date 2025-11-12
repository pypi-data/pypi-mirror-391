# DeviceTxBuffer

Device message buffer model used for API and database. Internal usage.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**message_id** | **str** |  | 
**timestamp** | **int** |  | [optional] 
**device_message** | **str** |  | [optional] 
**device_id** | **str** |  | [optional] 
**device_serial** | **str** |  | [optional] 
**device_type** | **str** |  | [optional] 

## Example

```python
from DeviceServer.models.device_tx_buffer import DeviceTxBuffer

# TODO update the JSON string below
json = "{}"
# create an instance of DeviceTxBuffer from a JSON string
device_tx_buffer_instance = DeviceTxBuffer.from_json(json)
# print the JSON string representation of the object
print(DeviceTxBuffer.to_json())

# convert the object into a dict
device_tx_buffer_dict = device_tx_buffer_instance.to_dict()
# create an instance of DeviceTxBuffer from a dict
device_tx_buffer_from_dict = DeviceTxBuffer.from_dict(device_tx_buffer_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


