# DeviceLed

Describes the State of a led for API.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**led_index** | **int** |  | 
**label** | **str** |  | [optional] 
**state_index** | **int** |  | [optional] 
**state_count** | **int** |  | [optional] 
**led_id** | **str** |  | 
**state_label** | **str** |  | [optional] 

## Example

```python
from DeviceServer.models.device_led import DeviceLed

# TODO update the JSON string below
json = "{}"
# create an instance of DeviceLed from a JSON string
device_led_instance = DeviceLed.from_json(json)
# print the JSON string representation of the object
print(DeviceLed.to_json())

# convert the object into a dict
device_led_dict = device_led_instance.to_dict()
# create an instance of DeviceLed from a dict
device_led_from_dict = DeviceLed.from_dict(device_led_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


