# HostConfig


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**host_name** | **str** |  | 
**ip_address** | **str** |  | 
**net_mask** | **str** |  | 
**gateway** | **str** |  | 
**static** | **bool** |  | 

## Example

```python
from DeviceServer.models.host_config import HostConfig

# TODO update the JSON string below
json = "{}"
# create an instance of HostConfig from a JSON string
host_config_instance = HostConfig.from_json(json)
# print the JSON string representation of the object
print(HostConfig.to_json())

# convert the object into a dict
host_config_dict = host_config_instance.to_dict()
# create an instance of HostConfig from a dict
host_config_from_dict = HostConfig.from_dict(host_config_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


