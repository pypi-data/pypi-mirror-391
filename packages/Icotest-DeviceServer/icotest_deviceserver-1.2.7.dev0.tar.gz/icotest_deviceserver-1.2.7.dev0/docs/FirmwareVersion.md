# FirmwareVersion


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**version** | **str** |  | [optional] 

## Example

```python
from DeviceServer.models.firmware_version import FirmwareVersion

# TODO update the JSON string below
json = "{}"
# create an instance of FirmwareVersion from a JSON string
firmware_version_instance = FirmwareVersion.from_json(json)
# print the JSON string representation of the object
print(FirmwareVersion.to_json())

# convert the object into a dict
firmware_version_dict = firmware_version_instance.to_dict()
# create an instance of FirmwareVersion from a dict
firmware_version_from_dict = FirmwareVersion.from_dict(firmware_version_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


