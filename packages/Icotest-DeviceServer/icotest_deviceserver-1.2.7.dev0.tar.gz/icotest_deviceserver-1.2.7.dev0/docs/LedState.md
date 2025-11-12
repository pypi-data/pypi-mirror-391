# LedState


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**state** | **bool** |  | [optional] 

## Example

```python
from DeviceServer.models.led_state import LedState

# TODO update the JSON string below
json = "{}"
# create an instance of LedState from a JSON string
led_state_instance = LedState.from_json(json)
# print the JSON string representation of the object
print(LedState.to_json())

# convert the object into a dict
led_state_dict = led_state_instance.to_dict()
# create an instance of LedState from a dict
led_state_from_dict = LedState.from_dict(led_state_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


