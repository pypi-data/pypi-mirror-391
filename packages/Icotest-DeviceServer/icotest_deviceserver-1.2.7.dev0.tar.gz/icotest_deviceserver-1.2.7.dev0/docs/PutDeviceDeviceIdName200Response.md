# PutDeviceDeviceIdName200Response


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**message** | **str** | Confirmation message | [optional] 
**updated_name** | **str** | The updated name of the device | [optional] 

## Example

```python
from DeviceServer.models.put_device_device_id_name200_response import PutDeviceDeviceIdName200Response

# TODO update the JSON string below
json = "{}"
# create an instance of PutDeviceDeviceIdName200Response from a JSON string
put_device_device_id_name200_response_instance = PutDeviceDeviceIdName200Response.from_json(json)
# print the JSON string representation of the object
print(PutDeviceDeviceIdName200Response.to_json())

# convert the object into a dict
put_device_device_id_name200_response_dict = put_device_device_id_name200_response_instance.to_dict()
# create an instance of PutDeviceDeviceIdName200Response from a dict
put_device_device_id_name200_response_from_dict = PutDeviceDeviceIdName200Response.from_dict(put_device_device_id_name200_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


