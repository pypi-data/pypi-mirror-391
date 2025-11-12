# PutDeviceDeviceIdDescription200Response


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**message** | **str** | Confirmation message | [optional] 
**updated_description** | **str** | The updated description of the device | [optional] 

## Example

```python
from DeviceServer.models.put_device_device_id_description200_response import PutDeviceDeviceIdDescription200Response

# TODO update the JSON string below
json = "{}"
# create an instance of PutDeviceDeviceIdDescription200Response from a JSON string
put_device_device_id_description200_response_instance = PutDeviceDeviceIdDescription200Response.from_json(json)
# print the JSON string representation of the object
print(PutDeviceDeviceIdDescription200Response.to_json())

# convert the object into a dict
put_device_device_id_description200_response_dict = put_device_device_id_description200_response_instance.to_dict()
# create an instance of PutDeviceDeviceIdDescription200Response from a dict
put_device_device_id_description200_response_from_dict = PutDeviceDeviceIdDescription200Response.from_dict(put_device_device_id_description200_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


