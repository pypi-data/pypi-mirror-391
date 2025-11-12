# DbUploadFirmwareState

Upload firmware state

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**device_id** | **str** |  | 
**device_serial** | **str** |  | 
**device_type** | **str** |  | 
**upload_state** | **str** | Current state of the firmware upload process. States: - IDLE: Ready for a new upload. - IN_PROGRESS: Upload is currently in progress. - COMPLETED: Upload finished successfully. - FAILED: Upload failed.  | 

## Example

```python
from DeviceServer.models.db_upload_firmware_state import DbUploadFirmwareState

# TODO update the JSON string below
json = "{}"
# create an instance of DbUploadFirmwareState from a JSON string
db_upload_firmware_state_instance = DbUploadFirmwareState.from_json(json)
# print the JSON string representation of the object
print(DbUploadFirmwareState.to_json())

# convert the object into a dict
db_upload_firmware_state_dict = db_upload_firmware_state_instance.to_dict()
# create an instance of DbUploadFirmwareState from a dict
db_upload_firmware_state_from_dict = DbUploadFirmwareState.from_dict(db_upload_firmware_state_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


