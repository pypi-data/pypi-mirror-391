# DbLedState

Version of led state for use with database rather than API

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**led_state_id** | **str** |  | 
**led_id** | **str** |  | 
**label** | **str** |  | 
**index** | **int** |  | 

## Example

```python
from DeviceServer.models.db_led_state import DbLedState

# TODO update the JSON string below
json = "{}"
# create an instance of DbLedState from a JSON string
db_led_state_instance = DbLedState.from_json(json)
# print the JSON string representation of the object
print(DbLedState.to_json())

# convert the object into a dict
db_led_state_dict = db_led_state_instance.to_dict()
# create an instance of DbLedState from a dict
db_led_state_from_dict = DbLedState.from_dict(db_led_state_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


