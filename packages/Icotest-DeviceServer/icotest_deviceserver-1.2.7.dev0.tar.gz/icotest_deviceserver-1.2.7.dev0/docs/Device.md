# Device

Model representing a device, used for both API interactions and database storage. This model includes attributes such as device ID, index, name, type, and various counts (ports, buttons, LEDs), as well as a serial number. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**device_id** | **str** |  | 
**device_index** | **int** |  | 
**device_type** | **str** |  | [optional] 
**device_serial** | **str** |  | [optional] 
**name** | **str** |  | 
**description** | **str** |  | [optional] 
**port_count** | **int** | Number of ports available on device | [optional] 
**button_count** | **int** | Number of buttons available on device | [optional] 
**led_count** | **int** | Number of leds available on device | [optional] 
**temperature_port_count** | **int** | Number of temperature ports available on device | [optional] 

## Example

```python
from DeviceServer.models.device import Device

# TODO update the JSON string below
json = "{}"
# create an instance of Device from a JSON string
device_instance = Device.from_json(json)
# print the JSON string representation of the object
print(Device.to_json())

# convert the object into a dict
device_dict = device_instance.to_dict()
# create an instance of Device from a dict
device_from_dict = Device.from_dict(device_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


