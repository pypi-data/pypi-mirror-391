# DbButtonState

Version of button state for use with database rather than API

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**button_state_id** | **str** |  | 
**button_id** | **str** |  | 
**label** | **str** |  | 
**index** | **int** |  | 

## Example

```python
from DeviceServer.models.db_button_state import DbButtonState

# TODO update the JSON string below
json = "{}"
# create an instance of DbButtonState from a JSON string
db_button_state_instance = DbButtonState.from_json(json)
# print the JSON string representation of the object
print(DbButtonState.to_json())

# convert the object into a dict
db_button_state_dict = db_button_state_instance.to_dict()
# create an instance of DbButtonState from a dict
db_button_state_from_dict = DbButtonState.from_dict(db_button_state_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


