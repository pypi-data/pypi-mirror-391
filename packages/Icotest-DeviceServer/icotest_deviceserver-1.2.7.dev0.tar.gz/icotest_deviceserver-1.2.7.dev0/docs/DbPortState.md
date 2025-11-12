# DbPortState

Version of port state for use with database rather than API

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**port_state_id** | **str** |  | 
**port_id** | **str** |  | 
**label** | **str** |  | 
**index** | **int** |  | 

## Example

```python
from DeviceServer.models.db_port_state import DbPortState

# TODO update the JSON string below
json = "{}"
# create an instance of DbPortState from a JSON string
db_port_state_instance = DbPortState.from_json(json)
# print the JSON string representation of the object
print(DbPortState.to_json())

# convert the object into a dict
db_port_state_dict = db_port_state_instance.to_dict()
# create an instance of DbPortState from a dict
db_port_state_from_dict = DbPortState.from_dict(db_port_state_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


