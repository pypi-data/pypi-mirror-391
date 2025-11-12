# DeviceButton

Describes the State of a button for API.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**button_index** | **int** |  | 
**label** | **str** |  | [optional] 
**state_index** | **int** |  | [optional] 
**state_count** | **int** |  | [optional] 
**button_id** | **str** |  | 
**state_label** | **str** |  | [optional] 

## Example

```python
from DeviceServer.models.device_button import DeviceButton

# TODO update the JSON string below
json = "{}"
# create an instance of DeviceButton from a JSON string
device_button_instance = DeviceButton.from_json(json)
# print the JSON string representation of the object
print(DeviceButton.to_json())

# convert the object into a dict
device_button_dict = device_button_instance.to_dict()
# create an instance of DeviceButton from a dict
device_button_from_dict = DeviceButton.from_dict(device_button_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


