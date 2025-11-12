# DbDeviceLed

Describes State of a led in database

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**device_id** | **str** |  | 
**led_index** | **int** |  | 
**label** | **str** |  | [optional] 
**led_id** | **str** |  | 

## Example

```python
from DeviceServer.models.db_device_led import DbDeviceLed

# TODO update the JSON string below
json = "{}"
# create an instance of DbDeviceLed from a JSON string
db_device_led_instance = DbDeviceLed.from_json(json)
# print the JSON string representation of the object
print(DbDeviceLed.to_json())

# convert the object into a dict
db_device_led_dict = db_device_led_instance.to_dict()
# create an instance of DbDeviceLed from a dict
db_device_led_from_dict = DbDeviceLed.from_dict(db_device_led_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


