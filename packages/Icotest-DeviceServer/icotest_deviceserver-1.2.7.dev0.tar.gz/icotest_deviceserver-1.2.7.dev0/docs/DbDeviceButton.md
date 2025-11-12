# DbDeviceButton

Describes State of a button in database

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**device_id** | **str** |  | 
**button_index** | **int** |  | 
**label** | **str** |  | [optional] 
**button_id** | **str** |  | 

## Example

```python
from DeviceServer.models.db_device_button import DbDeviceButton

# TODO update the JSON string below
json = "{}"
# create an instance of DbDeviceButton from a JSON string
db_device_button_instance = DbDeviceButton.from_json(json)
# print the JSON string representation of the object
print(DbDeviceButton.to_json())

# convert the object into a dict
db_device_button_dict = db_device_button_instance.to_dict()
# create an instance of DbDeviceButton from a dict
db_device_button_from_dict = DbDeviceButton.from_dict(db_device_button_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


