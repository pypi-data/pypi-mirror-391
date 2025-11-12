# PortState

Represents possible port states.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**index** | **int** | State number between 1 to 100 | 
**label** | **str** | Label for state can be set on per port basis | [optional] 

## Example

```python
from DeviceServer.models.port_state import PortState

# TODO update the JSON string below
json = "{}"
# create an instance of PortState from a JSON string
port_state_instance = PortState.from_json(json)
# print the JSON string representation of the object
print(PortState.to_json())

# convert the object into a dict
port_state_dict = port_state_instance.to_dict()
# create an instance of PortState from a dict
port_state_from_dict = PortState.from_dict(port_state_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


