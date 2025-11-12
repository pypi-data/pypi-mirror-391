# RelayState


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**state** | **bool** |  | [optional] 

## Example

```python
from DeviceServer.models.relay_state import RelayState

# TODO update the JSON string below
json = "{}"
# create an instance of RelayState from a JSON string
relay_state_instance = RelayState.from_json(json)
# print the JSON string representation of the object
print(RelayState.to_json())

# convert the object into a dict
relay_state_dict = relay_state_instance.to_dict()
# create an instance of RelayState from a dict
relay_state_from_dict = RelayState.from_dict(relay_state_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


