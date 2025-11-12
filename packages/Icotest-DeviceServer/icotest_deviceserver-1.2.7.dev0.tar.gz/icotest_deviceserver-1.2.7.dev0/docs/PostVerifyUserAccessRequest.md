# PostVerifyUserAccessRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**acc** | **int** |  | 
**clientid** | **str** |  | 
**topic** | **str** |  | 

## Example

```python
from DeviceServer.models.post_verify_user_access_request import PostVerifyUserAccessRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PostVerifyUserAccessRequest from a JSON string
post_verify_user_access_request_instance = PostVerifyUserAccessRequest.from_json(json)
# print the JSON string representation of the object
print(PostVerifyUserAccessRequest.to_json())

# convert the object into a dict
post_verify_user_access_request_dict = post_verify_user_access_request_instance.to_dict()
# create an instance of PostVerifyUserAccessRequest from a dict
post_verify_user_access_request_from_dict = PostVerifyUserAccessRequest.from_dict(post_verify_user_access_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


