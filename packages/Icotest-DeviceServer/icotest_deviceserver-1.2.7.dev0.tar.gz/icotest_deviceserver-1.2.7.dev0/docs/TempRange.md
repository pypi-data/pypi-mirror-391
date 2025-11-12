# TempRange



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**minimum** | **float** |  | [optional] 
**maximum** | **float** |  | [optional] 

## Example

```python
from DeviceServer.models.temp_range import TempRange

# TODO update the JSON string below
json = "{}"
# create an instance of TempRange from a JSON string
temp_range_instance = TempRange.from_json(json)
# print the JSON string representation of the object
print(TempRange.to_json())

# convert the object into a dict
temp_range_dict = temp_range_instance.to_dict()
# create an instance of TempRange from a dict
temp_range_from_dict = TempRange.from_dict(temp_range_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


