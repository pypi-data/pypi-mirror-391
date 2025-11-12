# DeviceServer.DevicesApi

All URIs are relative to *http://localhost/DeviceServer*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_current**](DevicesApi.md#get_current) | **GET** /Devices/{device_id}/Currents/{current_index} | GET current reading of device
[**get_device_device_id_buttons**](DevicesApi.md#get_device_device_id_buttons) | **GET** /Devices/{device_id}/Buttons | GET all buttons for device
[**get_device_device_id_leds**](DevicesApi.md#get_device_device_id_leds) | **GET** /Devices/{device_id}/Leds | GET all leds for Device
[**get_device_device_id_ports**](DevicesApi.md#get_device_device_id_ports) | **GET** /Devices/{device_id}/Ports | GET all Ports for Device
[**get_device_device_id_temperature_ports**](DevicesApi.md#get_device_device_id_temperature_ports) | **GET** /Devices/{device_id}/Temparatures | GET all temperature ports for device
[**get_device_id_port_index**](DevicesApi.md#get_device_id_port_index) | **GET** /Devices/{device_id}/Ports/{port_index} | GET status of port
[**get_device_port_current**](DevicesApi.md#get_device_port_current) | **GET** /Devices/{device_id}/Ports/{port_index}/Currents | GET current reading of device Port
[**get_device_port_module_led_state**](DevicesApi.md#get_device_port_module_led_state) | **GET** /Devices/{device_id}/Ports/{port_index}/Modules/{module_index}/Leds | GET state of Port Module Led
[**get_device_port_module_relay_state**](DevicesApi.md#get_device_port_module_relay_state) | **GET** /Devices/{device_id}/Ports/{port_index}/Modules/{module_index}/Relays/{relay_index} | GET state of Port Module Relay
[**get_device_port_voltage**](DevicesApi.md#get_device_port_voltage) | **GET** /Devices/{device_id}/Ports/{port_index}/Voltages | GET voltage reading of device Port
[**get_device_rotation_angle**](DevicesApi.md#get_device_rotation_angle) | **GET** /Devices/{device_id}/Rotation | GET Rotation Angle
[**get_device_rotation_speed**](DevicesApi.md#get_device_rotation_speed) | **GET** /Devices/{device_id}/Speed | GET Turntable Speed
[**get_device_uuid_deprecated**](DevicesApi.md#get_device_uuid_deprecated) | **GET** /Serial/{device_serial} | GET uuid from database
[**get_devices**](DevicesApi.md#get_devices) | **GET** /Devices | GET list of devices
[**get_devices_button**](DevicesApi.md#get_devices_button) | **GET** /Devices/{device_id}/Button/{button_index} | GET status of button
[**get_devices_index**](DevicesApi.md#get_devices_index) | **GET** /Devices/{device_id} | GET single device
[**get_devices_led**](DevicesApi.md#get_devices_led) | **GET** /Devices/{device_id}/Leds/{led_index} | GET status of Led
[**get_devices_temperature**](DevicesApi.md#get_devices_temperature) | **GET** /Devices/{device_id}/Temperature | GET temperature reading
[**get_fan_speed**](DevicesApi.md#get_fan_speed) | **GET** /Devices/{device_id}/Fan/{fan_index}/Speed | GET device fan speed
[**get_fan_target_temperature**](DevicesApi.md#get_fan_target_temperature) | **GET** /Devices/{device_id}/Fan/{fan_index}/TargetTemperature | GET device fan target temperature
[**get_fan_temperature**](DevicesApi.md#get_fan_temperature) | **GET** /Devices/{device_id}/Fan/{fan_index}/Temperature | GET device fan temperature
[**get_firmware_version**](DevicesApi.md#get_firmware_version) | **GET** /Devices/{device_id}/Firmware | GET Device Firmware Version
[**get_image**](DevicesApi.md#get_image) | **GET** /Devices/{device_id}/Image | GET Image
[**get_image_names**](DevicesApi.md#get_image_names) | **GET** /Devices/{device_id}/ImageNames | GET Image Names
[**get_message_from_rx_buffer_deprecated**](DevicesApi.md#get_message_from_rx_buffer_deprecated) | **GET** /Devices/messages/rx | GET message from RX table
[**get_message_from_tx_buffer_deprecated**](DevicesApi.md#get_message_from_tx_buffer_deprecated) | **GET** /Devices/messages/tx | GET message from TX table
[**get_port**](DevicesApi.md#get_port) | **GET** /Port/{port_id} | GET status of Port by id
[**get_port_led_state**](DevicesApi.md#get_port_led_state) | **GET** /Devices/{device_id}/Ports/{port_index}/Leds/{led_index} | GET state of Port LED
[**get_port_setup_status**](DevicesApi.md#get_port_setup_status) | **GET** /Devices/{device_id}/Ports/{port_index}/SetupStatus | GET setup status of Port
[**get_port_states**](DevicesApi.md#get_port_states) | **GET** /PortStates/{port_id} | GET port states by Port id
[**get_ports**](DevicesApi.md#get_ports) | **GET** /Ports | GET status of all ports
[**get_relay_state**](DevicesApi.md#get_relay_state) | **GET** /Devices/{device_id}/Relay | GET state of relay
[**get_temperature_range**](DevicesApi.md#get_temperature_range) | **GET** /Devices/{device_id}/Temperature/Range | GET Temperature Range
[**get_temperature_thresholds**](DevicesApi.md#get_temperature_thresholds) | **GET** /Devices/{device_id}/Temperature/Thresholds | GET Temperature Thresholds
[**get_turntable_calibration_data**](DevicesApi.md#get_turntable_calibration_data) | **GET** /Devices/{device_id}/Calibration | GET Turntable Calibration Values
[**get_voltage**](DevicesApi.md#get_voltage) | **GET** /Devices/{device_id}/Voltages/{voltage_index} | GET voltage reading of device
[**put_auto_calibrate_turntable**](DevicesApi.md#put_auto_calibrate_turntable) | **PUT** /Devices/{device_id}/Calibration | PUT Calibration
[**put_device_deprecated**](DevicesApi.md#put_device_deprecated) | **PUT** /Devices/AddDevice | PUT Add evice
[**put_device_device_id_description**](DevicesApi.md#put_device_device_id_description) | **PUT** /Device/{device_id}/Description | PUT a description for a Device
[**put_device_device_id_name**](DevicesApi.md#put_device_device_id_name) | **PUT** /Device/{device_id}/Name | PUT a name for a Device
[**put_device_id_label**](DevicesApi.md#put_device_id_label) | **PUT** /Device/{device_id}/Port/{port_index}/Label | PUT a Port label
[**put_device_port_module_led_state**](DevicesApi.md#put_device_port_module_led_state) | **PUT** /Devices/{device_id}/Ports/{port_index}/Modules/{module_index}/Leds | PUT state of Port Module LED
[**put_device_port_module_relay_state**](DevicesApi.md#put_device_port_module_relay_state) | **PUT** /Devices/{device_id}/Ports/{port_index}/Modules/{module_index}/Relays/{relay_index} | PUT state of Port Module Relay
[**put_device_rotation_angle**](DevicesApi.md#put_device_rotation_angle) | **PUT** /Devices/{device_id}/Rotation | PUT Rotation
[**put_device_rotation_angle_continuous**](DevicesApi.md#put_device_rotation_angle_continuous) | **PUT** /Devices/{device_id}/ContiniousRotation | PUT Continious Rotation
[**put_device_rotation_speed**](DevicesApi.md#put_device_rotation_speed) | **PUT** /Devices/{device_id}/Speed | PUT Turntable Speed
[**put_devices_led_index**](DevicesApi.md#put_devices_led_index) | **PUT** /Devices/{device_id}/Leds/{led_index} | PUT state of Led
[**put_devices_ports**](DevicesApi.md#put_devices_ports) | **PUT** /Devices/{device_id}/Ports/{port_index} | PUT state of port
[**put_halt_rotation**](DevicesApi.md#put_halt_rotation) | **PUT** /Devices/{device_id}/HaltRotation | PUT Halt Rotation
[**put_port_led_state**](DevicesApi.md#put_port_led_state) | **PUT** /Devices/{device_id}/Ports/{port_index}/Leds/{led_index} | PUT state of Port LED
[**put_port_port_id_label**](DevicesApi.md#put_port_port_id_label) | **PUT** /Port/{port_id}/Label | PUT the label for a Port
[**put_port_port_id_state_label**](DevicesApi.md#put_port_port_id_state_label) | **PUT** /Port/{port_id}/StateLabel | PUT state label
[**put_ports_pulse**](DevicesApi.md#put_ports_pulse) | **PUT** /Devices/{device_id}/Ports/{port_index}/Pulse | PUT Port into state for period of time
[**put_relay_state**](DevicesApi.md#put_relay_state) | **PUT** /Devices/{device_id}/Relay | PUT state of Relay
[**put_serial_test_message_deprecated**](DevicesApi.md#put_serial_test_message_deprecated) | **PUT** /Devices/{device_id}/Ports/{port_index}/SerialMessage | Serial Message Test
[**put_state_by_port_id**](DevicesApi.md#put_state_by_port_id) | **PUT** /Port/{port_id} | PUT state of port


# **get_current**
> float get_current(device_id, current_index)

GET current reading of device

Returns voltage reading by current_index.

### Example


```python
import DeviceServer
from DeviceServer.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost/DeviceServer
# See configuration.py for a list of all supported configuration parameters.
configuration = DeviceServer.Configuration(
    host = "http://localhost/DeviceServer"
)


# Enter a context with an instance of the API client
with DeviceServer.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = DeviceServer.DevicesApi(api_client)
    device_id = 'device_id_example' # str | UUID of device
    current_index = 56 # int | Index of Current port

    try:
        # GET current reading of device
        api_response = api_instance.get_current(device_id, current_index)
        print("The response of DevicesApi->get_current:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DevicesApi->get_current: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **device_id** | **str**| UUID of device | 
 **current_index** | **int**| Index of Current port | 

### Return type

**float**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**201** | Created |  -  |
**400** | Bad Request |  -  |
**401** | Unauthorized |  -  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |
**405** | Method Not Allowed |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_device_device_id_buttons**
> List[DeviceButton] get_device_device_id_buttons(device_id)

GET all buttons for device

Returns a list of all buttons attached to a device.

### Example


```python
import DeviceServer
from DeviceServer.models.device_button import DeviceButton
from DeviceServer.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost/DeviceServer
# See configuration.py for a list of all supported configuration parameters.
configuration = DeviceServer.Configuration(
    host = "http://localhost/DeviceServer"
)


# Enter a context with an instance of the API client
with DeviceServer.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = DeviceServer.DevicesApi(api_client)
    device_id = 'device_id_example' # str | UUID of device

    try:
        # GET all buttons for device
        api_response = api_instance.get_device_device_id_buttons(device_id)
        print("The response of DevicesApi->get_device_device_id_buttons:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DevicesApi->get_device_device_id_buttons: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **device_id** | **str**| UUID of device | 

### Return type

[**List[DeviceButton]**](DeviceButton.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**201** | Created |  -  |
**400** | Bad Request |  -  |
**401** | Unauthorized |  -  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |
**405** | Method Not Allowed |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_device_device_id_leds**
> List[DeviceLed] get_device_device_id_leds(device_id)

GET all leds for Device

Returns a list of all buttons attached to a Device.

### Example


```python
import DeviceServer
from DeviceServer.models.device_led import DeviceLed
from DeviceServer.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost/DeviceServer
# See configuration.py for a list of all supported configuration parameters.
configuration = DeviceServer.Configuration(
    host = "http://localhost/DeviceServer"
)


# Enter a context with an instance of the API client
with DeviceServer.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = DeviceServer.DevicesApi(api_client)
    device_id = 'device_id_example' # str | UUID of device

    try:
        # GET all leds for Device
        api_response = api_instance.get_device_device_id_leds(device_id)
        print("The response of DevicesApi->get_device_device_id_leds:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DevicesApi->get_device_device_id_leds: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **device_id** | **str**| UUID of device | 

### Return type

[**List[DeviceLed]**](DeviceLed.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**400** | Bad Request |  -  |
**401** | Unauthorized |  -  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |
**405** | Method Not Allowed |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_device_device_id_ports**
> List[DevicePort] get_device_device_id_ports(device_id)

GET all Ports for Device

Returns a list of all Ports attached to a Device.

### Example


```python
import DeviceServer
from DeviceServer.models.device_port import DevicePort
from DeviceServer.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost/DeviceServer
# See configuration.py for a list of all supported configuration parameters.
configuration = DeviceServer.Configuration(
    host = "http://localhost/DeviceServer"
)


# Enter a context with an instance of the API client
with DeviceServer.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = DeviceServer.DevicesApi(api_client)
    device_id = 'device_id_example' # str | UUID of device

    try:
        # GET all Ports for Device
        api_response = api_instance.get_device_device_id_ports(device_id)
        print("The response of DevicesApi->get_device_device_id_ports:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DevicesApi->get_device_device_id_ports: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **device_id** | **str**| UUID of device | 

### Return type

[**List[DevicePort]**](DevicePort.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**201** | Created |  -  |
**400** | Bad Request |  -  |
**401** | Unauthorized |  -  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |
**405** | Method Not Allowed |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_device_device_id_temperature_ports**
> List[DeviceTemperaturePort] get_device_device_id_temperature_ports(device_id)

GET all temperature ports for device

Returns a list of all temperature ports attached to a device.

### Example


```python
import DeviceServer
from DeviceServer.models.device_temperature_port import DeviceTemperaturePort
from DeviceServer.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost/DeviceServer
# See configuration.py for a list of all supported configuration parameters.
configuration = DeviceServer.Configuration(
    host = "http://localhost/DeviceServer"
)


# Enter a context with an instance of the API client
with DeviceServer.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = DeviceServer.DevicesApi(api_client)
    device_id = 'device_id_example' # str | UUID of device

    try:
        # GET all temperature ports for device
        api_response = api_instance.get_device_device_id_temperature_ports(device_id)
        print("The response of DevicesApi->get_device_device_id_temperature_ports:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DevicesApi->get_device_device_id_temperature_ports: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **device_id** | **str**| UUID of device | 

### Return type

[**List[DeviceTemperaturePort]**](DeviceTemperaturePort.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**201** | Created |  -  |
**400** | Bad Request |  -  |
**401** | Unauthorized |  -  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |
**405** | Method Not Allowed |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_device_id_port_index**
> DevicePort get_device_id_port_index(device_id, port_index)

GET status of port

Returns status of a Port.

### Example


```python
import DeviceServer
from DeviceServer.models.device_port import DevicePort
from DeviceServer.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost/DeviceServer
# See configuration.py for a list of all supported configuration parameters.
configuration = DeviceServer.Configuration(
    host = "http://localhost/DeviceServer"
)


# Enter a context with an instance of the API client
with DeviceServer.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = DeviceServer.DevicesApi(api_client)
    device_id = 'device_id_example' # str | UUID of device
    port_index = 56 # int | Index of port

    try:
        # GET status of port
        api_response = api_instance.get_device_id_port_index(device_id, port_index)
        print("The response of DevicesApi->get_device_id_port_index:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DevicesApi->get_device_id_port_index: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **device_id** | **str**| UUID of device | 
 **port_index** | **int**| Index of port | 

### Return type

[**DevicePort**](DevicePort.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**201** | Created |  -  |
**400** | Bad Request |  -  |
**401** | Unauthorized |  -  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |
**405** | Method Not Allowed |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_device_port_current**
> float get_device_port_current(device_id, port_index)

GET current reading of device Port

Returns current reading by port_index.

### Example


```python
import DeviceServer
from DeviceServer.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost/DeviceServer
# See configuration.py for a list of all supported configuration parameters.
configuration = DeviceServer.Configuration(
    host = "http://localhost/DeviceServer"
)


# Enter a context with an instance of the API client
with DeviceServer.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = DeviceServer.DevicesApi(api_client)
    device_id = 'device_id_example' # str | UUID of device
    port_index = 56 # int | Port Index

    try:
        # GET current reading of device Port
        api_response = api_instance.get_device_port_current(device_id, port_index)
        print("The response of DevicesApi->get_device_port_current:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DevicesApi->get_device_port_current: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **device_id** | **str**| UUID of device | 
 **port_index** | **int**| Port Index | 

### Return type

**float**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**201** | Created |  -  |
**400** | Bad Request |  -  |
**401** | Unauthorized |  -  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |
**405** | Method Not Allowed |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_device_port_module_led_state**
> object get_device_port_module_led_state(device_id, port_index, module_index)

GET state of Port Module Led

Returns state of Port Module Led.

### Example


```python
import DeviceServer
from DeviceServer.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost/DeviceServer
# See configuration.py for a list of all supported configuration parameters.
configuration = DeviceServer.Configuration(
    host = "http://localhost/DeviceServer"
)


# Enter a context with an instance of the API client
with DeviceServer.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = DeviceServer.DevicesApi(api_client)
    device_id = 'device_id_example' # str | UUID of device
    port_index = 56 # int | Index of Port
    module_index = 56 # int | Index of Module

    try:
        # GET state of Port Module Led
        api_response = api_instance.get_device_port_module_led_state(device_id, port_index, module_index)
        print("The response of DevicesApi->get_device_port_module_led_state:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DevicesApi->get_device_port_module_led_state: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **device_id** | **str**| UUID of device | 
 **port_index** | **int**| Index of Port | 
 **module_index** | **int**| Index of Module | 

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**201** | Created |  -  |
**400** | Bad Request |  -  |
**401** | Unauthorized |  -  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |
**405** | Method Not Allowed |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_device_port_module_relay_state**
> object get_device_port_module_relay_state(device_id, port_index, module_index, relay_index)

GET state of Port Module Relay

Returns state of Port Module Relay.

### Example


```python
import DeviceServer
from DeviceServer.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost/DeviceServer
# See configuration.py for a list of all supported configuration parameters.
configuration = DeviceServer.Configuration(
    host = "http://localhost/DeviceServer"
)


# Enter a context with an instance of the API client
with DeviceServer.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = DeviceServer.DevicesApi(api_client)
    device_id = 'device_id_example' # str | UUID of device
    port_index = 56 # int | Index of Port
    module_index = 56 # int | Index of Module
    relay_index = 56 # int | Index of Relay

    try:
        # GET state of Port Module Relay
        api_response = api_instance.get_device_port_module_relay_state(device_id, port_index, module_index, relay_index)
        print("The response of DevicesApi->get_device_port_module_relay_state:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DevicesApi->get_device_port_module_relay_state: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **device_id** | **str**| UUID of device | 
 **port_index** | **int**| Index of Port | 
 **module_index** | **int**| Index of Module | 
 **relay_index** | **int**| Index of Relay | 

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**201** | Created |  -  |
**400** | Bad Request |  -  |
**401** | Unauthorized |  -  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |
**405** | Method Not Allowed |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_device_port_voltage**
> float get_device_port_voltage(device_id, port_index)

GET voltage reading of device Port

Returns voltage reading by port_index.

### Example


```python
import DeviceServer
from DeviceServer.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost/DeviceServer
# See configuration.py for a list of all supported configuration parameters.
configuration = DeviceServer.Configuration(
    host = "http://localhost/DeviceServer"
)


# Enter a context with an instance of the API client
with DeviceServer.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = DeviceServer.DevicesApi(api_client)
    device_id = 'device_id_example' # str | UUID of device
    port_index = 56 # int | Port Index

    try:
        # GET voltage reading of device Port
        api_response = api_instance.get_device_port_voltage(device_id, port_index)
        print("The response of DevicesApi->get_device_port_voltage:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DevicesApi->get_device_port_voltage: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **device_id** | **str**| UUID of device | 
 **port_index** | **int**| Port Index | 

### Return type

**float**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**201** | Created |  -  |
**400** | Bad Request |  -  |
**401** | Unauthorized |  -  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |
**405** | Method Not Allowed |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_device_rotation_angle**
> object get_device_rotation_angle(device_id)

GET Rotation Angle

Get the rotation angle of the Turntable.

### Example


```python
import DeviceServer
from DeviceServer.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost/DeviceServer
# See configuration.py for a list of all supported configuration parameters.
configuration = DeviceServer.Configuration(
    host = "http://localhost/DeviceServer"
)


# Enter a context with an instance of the API client
with DeviceServer.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = DeviceServer.DevicesApi(api_client)
    device_id = 'device_id_example' # str | 

    try:
        # GET Rotation Angle
        api_response = api_instance.get_device_rotation_angle(device_id)
        print("The response of DevicesApi->get_device_rotation_angle:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DevicesApi->get_device_rotation_angle: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **device_id** | **str**|  | 

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**201** | Created |  -  |
**400** | Bad Request |  -  |
**401** | Unauthorized |  -  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |
**405** | Method Not Allowed |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_device_rotation_speed**
> object get_device_rotation_speed(device_id)

GET Turntable Speed

Get the configured Turntable speed.

### Example


```python
import DeviceServer
from DeviceServer.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost/DeviceServer
# See configuration.py for a list of all supported configuration parameters.
configuration = DeviceServer.Configuration(
    host = "http://localhost/DeviceServer"
)


# Enter a context with an instance of the API client
with DeviceServer.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = DeviceServer.DevicesApi(api_client)
    device_id = 'device_id_example' # str | 

    try:
        # GET Turntable Speed
        api_response = api_instance.get_device_rotation_speed(device_id)
        print("The response of DevicesApi->get_device_rotation_speed:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DevicesApi->get_device_rotation_speed: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **device_id** | **str**|  | 

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**201** | Created |  -  |
**400** | Bad Request |  -  |
**401** | Unauthorized |  -  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |
**405** | Method Not Allowed |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_device_uuid_deprecated**
> object get_device_uuid_deprecated(device_serial)

GET uuid from database

Query database for device_id by device_serial.

### Example


```python
import DeviceServer
from DeviceServer.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost/DeviceServer
# See configuration.py for a list of all supported configuration parameters.
configuration = DeviceServer.Configuration(
    host = "http://localhost/DeviceServer"
)


# Enter a context with an instance of the API client
with DeviceServer.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = DeviceServer.DevicesApi(api_client)
    device_serial = 'device_serial_example' # str | Serial number of device

    try:
        # GET uuid from database
        api_response = api_instance.get_device_uuid_deprecated(device_serial)
        print("The response of DevicesApi->get_device_uuid_deprecated:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DevicesApi->get_device_uuid_deprecated: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **device_serial** | **str**| Serial number of device | 

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**201** | Created |  -  |
**400** | Bad Request |  -  |
**401** | Unauthorized |  -  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |
**405** | Method Not Allowed |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_devices**
> List[Device] get_devices()

GET list of devices

Returns list of Devices.

### Example


```python
import DeviceServer
from DeviceServer.models.device import Device
from DeviceServer.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost/DeviceServer
# See configuration.py for a list of all supported configuration parameters.
configuration = DeviceServer.Configuration(
    host = "http://localhost/DeviceServer"
)


# Enter a context with an instance of the API client
with DeviceServer.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = DeviceServer.DevicesApi(api_client)

    try:
        # GET list of devices
        api_response = api_instance.get_devices()
        print("The response of DevicesApi->get_devices:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DevicesApi->get_devices: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**List[Device]**](Device.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**201** | Created |  -  |
**400** | Bad Request |  -  |
**401** | Unauthorized |  -  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |
**405** | Method Not Allowed |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_devices_button**
> DeviceButton get_devices_button(device_id, button_index)

GET status of button

Returns status of button.

### Example


```python
import DeviceServer
from DeviceServer.models.device_button import DeviceButton
from DeviceServer.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost/DeviceServer
# See configuration.py for a list of all supported configuration parameters.
configuration = DeviceServer.Configuration(
    host = "http://localhost/DeviceServer"
)


# Enter a context with an instance of the API client
with DeviceServer.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = DeviceServer.DevicesApi(api_client)
    device_id = 'device_id_example' # str | UUID of device
    button_index = 56 # int | Index of port

    try:
        # GET status of button
        api_response = api_instance.get_devices_button(device_id, button_index)
        print("The response of DevicesApi->get_devices_button:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DevicesApi->get_devices_button: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **device_id** | **str**| UUID of device | 
 **button_index** | **int**| Index of port | 

### Return type

[**DeviceButton**](DeviceButton.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**201** | Created |  -  |
**400** | Bad Request |  -  |
**401** | Unauthorized |  -  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |
**405** | Method Not Allowed |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_devices_index**
> Device get_devices_index(device_id)

GET single device

Gets information for a single device.

### Example


```python
import DeviceServer
from DeviceServer.models.device import Device
from DeviceServer.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost/DeviceServer
# See configuration.py for a list of all supported configuration parameters.
configuration = DeviceServer.Configuration(
    host = "http://localhost/DeviceServer"
)


# Enter a context with an instance of the API client
with DeviceServer.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = DeviceServer.DevicesApi(api_client)
    device_id = 'device_id_example' # str | UUID of device

    try:
        # GET single device
        api_response = api_instance.get_devices_index(device_id)
        print("The response of DevicesApi->get_devices_index:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DevicesApi->get_devices_index: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **device_id** | **str**| UUID of device | 

### Return type

[**Device**](Device.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**201** | Created |  -  |
**400** | Bad Request |  -  |
**401** | Unauthorized |  -  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |
**405** | Method Not Allowed |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_devices_led**
> DeviceLed get_devices_led(device_id, led_index)

GET status of Led

Returns status of Led

### Example


```python
import DeviceServer
from DeviceServer.models.device_led import DeviceLed
from DeviceServer.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost/DeviceServer
# See configuration.py for a list of all supported configuration parameters.
configuration = DeviceServer.Configuration(
    host = "http://localhost/DeviceServer"
)


# Enter a context with an instance of the API client
with DeviceServer.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = DeviceServer.DevicesApi(api_client)
    device_id = 'device_id_example' # str | UUID of device
    led_index = 56 # int | Index of LED

    try:
        # GET status of Led
        api_response = api_instance.get_devices_led(device_id, led_index)
        print("The response of DevicesApi->get_devices_led:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DevicesApi->get_devices_led: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **device_id** | **str**| UUID of device | 
 **led_index** | **int**| Index of LED | 

### Return type

[**DeviceLed**](DeviceLed.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**201** | Created |  -  |
**400** | Bad Request |  -  |
**401** | Unauthorized |  -  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |
**405** | Method Not Allowed |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_devices_temperature**
> float get_devices_temperature(device_id, thermometer_index=thermometer_index)

GET temperature reading

Get temperature reading from specified Device.

### Example


```python
import DeviceServer
from DeviceServer.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost/DeviceServer
# See configuration.py for a list of all supported configuration parameters.
configuration = DeviceServer.Configuration(
    host = "http://localhost/DeviceServer"
)


# Enter a context with an instance of the API client
with DeviceServer.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = DeviceServer.DevicesApi(api_client)
    device_id = 'device_id_example' # str | 
    thermometer_index = 56 # int | Index of the thermometer (1-7) (optional)

    try:
        # GET temperature reading
        api_response = api_instance.get_devices_temperature(device_id, thermometer_index=thermometer_index)
        print("The response of DevicesApi->get_devices_temperature:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DevicesApi->get_devices_temperature: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **device_id** | **str**|  | 
 **thermometer_index** | **int**| Index of the thermometer (1-7) | [optional] 

### Return type

**float**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**400** | Bad Request |  -  |
**401** | Unauthorized |  -  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |
**405** | Method Not Allowed |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_fan_speed**
> object get_fan_speed(device_id, fan_index)

GET device fan speed

Get the fan speed by fan_index. 

### Example


```python
import DeviceServer
from DeviceServer.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost/DeviceServer
# See configuration.py for a list of all supported configuration parameters.
configuration = DeviceServer.Configuration(
    host = "http://localhost/DeviceServer"
)


# Enter a context with an instance of the API client
with DeviceServer.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = DeviceServer.DevicesApi(api_client)
    device_id = 'device_id_example' # str | 
    fan_index = 'fan_index_example' # str | 

    try:
        # GET device fan speed
        api_response = api_instance.get_fan_speed(device_id, fan_index)
        print("The response of DevicesApi->get_fan_speed:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DevicesApi->get_fan_speed: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **device_id** | **str**|  | 
 **fan_index** | **str**|  | 

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**201** | Created |  -  |
**400** | Bad Request |  -  |
**401** | Unauthorized |  -  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |
**405** | Method Not Allowed |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_fan_target_temperature**
> object get_fan_target_temperature(device_id, fan_index)

GET device fan target temperature

Get the fan target temeprature by fan_index.

### Example


```python
import DeviceServer
from DeviceServer.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost/DeviceServer
# See configuration.py for a list of all supported configuration parameters.
configuration = DeviceServer.Configuration(
    host = "http://localhost/DeviceServer"
)


# Enter a context with an instance of the API client
with DeviceServer.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = DeviceServer.DevicesApi(api_client)
    device_id = 'device_id_example' # str | 
    fan_index = 'fan_index_example' # str | 

    try:
        # GET device fan target temperature
        api_response = api_instance.get_fan_target_temperature(device_id, fan_index)
        print("The response of DevicesApi->get_fan_target_temperature:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DevicesApi->get_fan_target_temperature: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **device_id** | **str**|  | 
 **fan_index** | **str**|  | 

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**201** | Created |  -  |
**400** | Bad Request |  -  |
**401** | Unauthorized |  -  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |
**405** | Method Not Allowed |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_fan_temperature**
> object get_fan_temperature(device_id, fan_index)

GET device fan temperature

Get the fan temperature by fan_index.

### Example


```python
import DeviceServer
from DeviceServer.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost/DeviceServer
# See configuration.py for a list of all supported configuration parameters.
configuration = DeviceServer.Configuration(
    host = "http://localhost/DeviceServer"
)


# Enter a context with an instance of the API client
with DeviceServer.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = DeviceServer.DevicesApi(api_client)
    device_id = 'device_id_example' # str | 
    fan_index = 'fan_index_example' # str | 

    try:
        # GET device fan temperature
        api_response = api_instance.get_fan_temperature(device_id, fan_index)
        print("The response of DevicesApi->get_fan_temperature:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DevicesApi->get_fan_temperature: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **device_id** | **str**|  | 
 **fan_index** | **str**|  | 

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**201** | Created |  -  |
**400** | Bad Request |  -  |
**401** | Unauthorized |  -  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |
**405** | Method Not Allowed |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_firmware_version**
> FirmwareVersion get_firmware_version(device_id)

GET Device Firmware Version

Get the device firmware version.

### Example


```python
import DeviceServer
from DeviceServer.models.firmware_version import FirmwareVersion
from DeviceServer.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost/DeviceServer
# See configuration.py for a list of all supported configuration parameters.
configuration = DeviceServer.Configuration(
    host = "http://localhost/DeviceServer"
)


# Enter a context with an instance of the API client
with DeviceServer.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = DeviceServer.DevicesApi(api_client)
    device_id = 'device_id_example' # str | Device ID

    try:
        # GET Device Firmware Version
        api_response = api_instance.get_firmware_version(device_id)
        print("The response of DevicesApi->get_firmware_version:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DevicesApi->get_firmware_version: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **device_id** | **str**| Device ID | 

### Return type

[**FirmwareVersion**](FirmwareVersion.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**400** | Bad Request |  -  |
**401** | Unauthorized |  -  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |
**405** | Method Not Allowed |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_image**
> bytearray get_image(device_id, image_name=image_name)

GET Image

Get the image from the provided name.

### Example


```python
import DeviceServer
from DeviceServer.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost/DeviceServer
# See configuration.py for a list of all supported configuration parameters.
configuration = DeviceServer.Configuration(
    host = "http://localhost/DeviceServer"
)


# Enter a context with an instance of the API client
with DeviceServer.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = DeviceServer.DevicesApi(api_client)
    device_id = 'device_id_example' # str | 
    image_name = 'image_name_example' # str | Image Name (optional)

    try:
        # GET Image
        api_response = api_instance.get_image(device_id, image_name=image_name)
        print("The response of DevicesApi->get_image:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DevicesApi->get_image: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **device_id** | **str**|  | 
 **image_name** | **str**| Image Name | [optional] 

### Return type

**bytearray**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: image/png, application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**201** | Created |  -  |
**400** | Bad Request |  -  |
**404** | Not Found |  -  |
**405** | Method Not Allowed |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_image_names**
> object get_image_names(device_id)

GET Image Names

Get the image names available on the Device.

### Example


```python
import DeviceServer
from DeviceServer.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost/DeviceServer
# See configuration.py for a list of all supported configuration parameters.
configuration = DeviceServer.Configuration(
    host = "http://localhost/DeviceServer"
)


# Enter a context with an instance of the API client
with DeviceServer.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = DeviceServer.DevicesApi(api_client)
    device_id = 'device_id_example' # str | 

    try:
        # GET Image Names
        api_response = api_instance.get_image_names(device_id)
        print("The response of DevicesApi->get_image_names:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DevicesApi->get_image_names: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **device_id** | **str**|  | 

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**201** | Created |  -  |
**400** | Bad Request |  -  |
**404** | Not Found |  -  |
**405** | Method Not Allowed |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_message_from_rx_buffer_deprecated**
> object get_message_from_rx_buffer_deprecated(device_id=device_id)

GET message from RX table

GET a message from the rx table.

### Example


```python
import DeviceServer
from DeviceServer.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost/DeviceServer
# See configuration.py for a list of all supported configuration parameters.
configuration = DeviceServer.Configuration(
    host = "http://localhost/DeviceServer"
)


# Enter a context with an instance of the API client
with DeviceServer.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = DeviceServer.DevicesApi(api_client)
    device_id = 'device_id_example' # str |  (optional)

    try:
        # GET message from RX table
        api_response = api_instance.get_message_from_rx_buffer_deprecated(device_id=device_id)
        print("The response of DevicesApi->get_message_from_rx_buffer_deprecated:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DevicesApi->get_message_from_rx_buffer_deprecated: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **device_id** | **str**|  | [optional] 

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**201** | Created |  -  |
**400** | Bad Request |  -  |
**401** | Unauthorized |  -  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |
**405** | Method Not Allowed |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_message_from_tx_buffer_deprecated**
> str get_message_from_tx_buffer_deprecated(device_id=device_id, device_serial=device_serial, device_type=device_type)

GET message from TX table

GET a message from the tx table.

### Example


```python
import DeviceServer
from DeviceServer.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost/DeviceServer
# See configuration.py for a list of all supported configuration parameters.
configuration = DeviceServer.Configuration(
    host = "http://localhost/DeviceServer"
)


# Enter a context with an instance of the API client
with DeviceServer.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = DeviceServer.DevicesApi(api_client)
    device_id = 'device_id_example' # str |  (optional)
    device_serial = 'device_serial_example' # str |  (optional)
    device_type = 'device_type_example' # str |  (optional)

    try:
        # GET message from TX table
        api_response = api_instance.get_message_from_tx_buffer_deprecated(device_id=device_id, device_serial=device_serial, device_type=device_type)
        print("The response of DevicesApi->get_message_from_tx_buffer_deprecated:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DevicesApi->get_message_from_tx_buffer_deprecated: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **device_id** | **str**|  | [optional] 
 **device_serial** | **str**|  | [optional] 
 **device_type** | **str**|  | [optional] 

### Return type

**str**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**201** | Created |  -  |
**400** | Bad Request |  -  |
**401** | Unauthorized |  -  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |
**405** | Method Not Allowed |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_port**
> DevicePort get_port(port_id)

GET status of Port by id

Returns status of port by port_id.

### Example


```python
import DeviceServer
from DeviceServer.models.device_port import DevicePort
from DeviceServer.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost/DeviceServer
# See configuration.py for a list of all supported configuration parameters.
configuration = DeviceServer.Configuration(
    host = "http://localhost/DeviceServer"
)


# Enter a context with an instance of the API client
with DeviceServer.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = DeviceServer.DevicesApi(api_client)
    port_id = 'port_id_example' # str | id of port to set

    try:
        # GET status of Port by id
        api_response = api_instance.get_port(port_id)
        print("The response of DevicesApi->get_port:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DevicesApi->get_port: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **port_id** | **str**| id of port to set | 

### Return type

[**DevicePort**](DevicePort.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**201** | Created |  -  |
**400** | Bad Request |  -  |
**401** | Unauthorized |  -  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |
**405** | Method Not Allowed |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_port_led_state**
> LedState get_port_led_state(device_id, port_index, led_index)

GET state of Port LED

Returns state of Led by Port Led Index.

### Example


```python
import DeviceServer
from DeviceServer.models.led_state import LedState
from DeviceServer.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost/DeviceServer
# See configuration.py for a list of all supported configuration parameters.
configuration = DeviceServer.Configuration(
    host = "http://localhost/DeviceServer"
)


# Enter a context with an instance of the API client
with DeviceServer.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = DeviceServer.DevicesApi(api_client)
    device_id = 'device_id_example' # str | UUID of device
    port_index = 56 # int | Index of Port
    led_index = 56 # int | Index of Led

    try:
        # GET state of Port LED
        api_response = api_instance.get_port_led_state(device_id, port_index, led_index)
        print("The response of DevicesApi->get_port_led_state:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DevicesApi->get_port_led_state: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **device_id** | **str**| UUID of device | 
 **port_index** | **int**| Index of Port | 
 **led_index** | **int**| Index of Led | 

### Return type

[**LedState**](LedState.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**201** | Created |  -  |
**400** | Bad Request |  -  |
**401** | Unauthorized |  -  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |
**405** | Method Not Allowed |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_port_setup_status**
> object get_port_setup_status(device_id, port_index)

GET setup status of Port

Returns setup and connection status of a Port.

### Example


```python
import DeviceServer
from DeviceServer.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost/DeviceServer
# See configuration.py for a list of all supported configuration parameters.
configuration = DeviceServer.Configuration(
    host = "http://localhost/DeviceServer"
)


# Enter a context with an instance of the API client
with DeviceServer.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = DeviceServer.DevicesApi(api_client)
    device_id = 'device_id_example' # str | UUID of device
    port_index = 56 # int | Index of port

    try:
        # GET setup status of Port
        api_response = api_instance.get_port_setup_status(device_id, port_index)
        print("The response of DevicesApi->get_port_setup_status:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DevicesApi->get_port_setup_status: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **device_id** | **str**| UUID of device | 
 **port_index** | **int**| Index of port | 

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**201** | Created |  -  |
**400** | Bad Request |  -  |
**401** | Unauthorized |  -  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |
**405** | Method Not Allowed |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_port_states**
> List[PortState] get_port_states(port_id)

GET port states by Port id

Gets a list of available port states for a port.

### Example


```python
import DeviceServer
from DeviceServer.models.port_state import PortState
from DeviceServer.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost/DeviceServer
# See configuration.py for a list of all supported configuration parameters.
configuration = DeviceServer.Configuration(
    host = "http://localhost/DeviceServer"
)


# Enter a context with an instance of the API client
with DeviceServer.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = DeviceServer.DevicesApi(api_client)
    port_id = 'port_id_example' # str | 

    try:
        # GET port states by Port id
        api_response = api_instance.get_port_states(port_id)
        print("The response of DevicesApi->get_port_states:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DevicesApi->get_port_states: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **port_id** | **str**|  | 

### Return type

[**List[PortState]**](PortState.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**201** | Created |  -  |
**400** | Bad Request |  -  |
**401** | Unauthorized |  -  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |
**405** | Method Not Allowed |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_ports**
> List[DevicePort] get_ports()

GET status of all ports

Returns status of all Devices' Ports 

### Example


```python
import DeviceServer
from DeviceServer.models.device_port import DevicePort
from DeviceServer.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost/DeviceServer
# See configuration.py for a list of all supported configuration parameters.
configuration = DeviceServer.Configuration(
    host = "http://localhost/DeviceServer"
)


# Enter a context with an instance of the API client
with DeviceServer.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = DeviceServer.DevicesApi(api_client)

    try:
        # GET status of all ports
        api_response = api_instance.get_ports()
        print("The response of DevicesApi->get_ports:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DevicesApi->get_ports: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**List[DevicePort]**](DevicePort.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**201** | Created |  -  |
**400** | Bad Request |  -  |
**401** | Unauthorized |  -  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |
**405** | Method Not Allowed |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_relay_state**
> RelayState get_relay_state(device_id, index)

GET state of relay

Get state of Relay at index.

### Example


```python
import DeviceServer
from DeviceServer.models.relay_state import RelayState
from DeviceServer.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost/DeviceServer
# See configuration.py for a list of all supported configuration parameters.
configuration = DeviceServer.Configuration(
    host = "http://localhost/DeviceServer"
)


# Enter a context with an instance of the API client
with DeviceServer.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = DeviceServer.DevicesApi(api_client)
    device_id = 'device_id_example' # str | 
    index = 56 # int | index of relay to get state of

    try:
        # GET state of relay
        api_response = api_instance.get_relay_state(device_id, index)
        print("The response of DevicesApi->get_relay_state:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DevicesApi->get_relay_state: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **device_id** | **str**|  | 
 **index** | **int**| index of relay to get state of | 

### Return type

[**RelayState**](RelayState.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**201** | Created |  -  |
**400** | Bad Request |  -  |
**401** | Unauthorized |  -  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |
**405** | Method Not Allowed |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_temperature_range**
> TempRange get_temperature_range(device_id)

GET Temperature Range

Get the minimum and maximum temperatures for a given hex thermometer

### Example


```python
import DeviceServer
from DeviceServer.models.temp_range import TempRange
from DeviceServer.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost/DeviceServer
# See configuration.py for a list of all supported configuration parameters.
configuration = DeviceServer.Configuration(
    host = "http://localhost/DeviceServer"
)


# Enter a context with an instance of the API client
with DeviceServer.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = DeviceServer.DevicesApi(api_client)
    device_id = 'device_id_example' # str | 

    try:
        # GET Temperature Range
        api_response = api_instance.get_temperature_range(device_id)
        print("The response of DevicesApi->get_temperature_range:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DevicesApi->get_temperature_range: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **device_id** | **str**|  | 

### Return type

[**TempRange**](TempRange.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**400** | Bad Request |  -  |
**401** | Unauthorized |  -  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |
**405** | Method Not Allowed |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_temperature_thresholds**
> List[float] get_temperature_thresholds(device_id)

GET Temperature Thresholds

Get the points at which the temperature enters danger zones.

### Example


```python
import DeviceServer
from DeviceServer.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost/DeviceServer
# See configuration.py for a list of all supported configuration parameters.
configuration = DeviceServer.Configuration(
    host = "http://localhost/DeviceServer"
)


# Enter a context with an instance of the API client
with DeviceServer.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = DeviceServer.DevicesApi(api_client)
    device_id = 'device_id_example' # str | the device id

    try:
        # GET Temperature Thresholds
        api_response = api_instance.get_temperature_thresholds(device_id)
        print("The response of DevicesApi->get_temperature_thresholds:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DevicesApi->get_temperature_thresholds: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **device_id** | **str**| the device id | 

### Return type

**List[float]**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**201** | Created |  -  |
**400** | Bad Request |  -  |
**401** | Unauthorized |  -  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |
**405** | Method Not Allowed |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_turntable_calibration_data**
> object get_turntable_calibration_data(device_id)

GET Turntable Calibration Values

Get the calibration data for the Device

### Example


```python
import DeviceServer
from DeviceServer.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost/DeviceServer
# See configuration.py for a list of all supported configuration parameters.
configuration = DeviceServer.Configuration(
    host = "http://localhost/DeviceServer"
)


# Enter a context with an instance of the API client
with DeviceServer.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = DeviceServer.DevicesApi(api_client)
    device_id = 'device_id_example' # str | 

    try:
        # GET Turntable Calibration Values
        api_response = api_instance.get_turntable_calibration_data(device_id)
        print("The response of DevicesApi->get_turntable_calibration_data:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DevicesApi->get_turntable_calibration_data: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **device_id** | **str**|  | 

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**400** | Bad Request |  -  |
**401** | Unauthorized |  -  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |
**405** | Method Not Allowed |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_voltage**
> float get_voltage(device_id, voltage_index)

GET voltage reading of device

Returns voltage reading on selected device.

### Example


```python
import DeviceServer
from DeviceServer.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost/DeviceServer
# See configuration.py for a list of all supported configuration parameters.
configuration = DeviceServer.Configuration(
    host = "http://localhost/DeviceServer"
)


# Enter a context with an instance of the API client
with DeviceServer.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = DeviceServer.DevicesApi(api_client)
    device_id = 'device_id_example' # str | UUID of device
    voltage_index = 56 # int | Index of Voltage port

    try:
        # GET voltage reading of device
        api_response = api_instance.get_voltage(device_id, voltage_index)
        print("The response of DevicesApi->get_voltage:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DevicesApi->get_voltage: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **device_id** | **str**| UUID of device | 
 **voltage_index** | **int**| Index of Voltage port | 

### Return type

**float**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**201** | Created |  -  |
**400** | Bad Request |  -  |
**401** | Unauthorized |  -  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |
**405** | Method Not Allowed |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **put_auto_calibrate_turntable**
> str put_auto_calibrate_turntable(device_id)

PUT Calibration

1 Click auto-calibration, before execution ensure physical zero.

### Example


```python
import DeviceServer
from DeviceServer.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost/DeviceServer
# See configuration.py for a list of all supported configuration parameters.
configuration = DeviceServer.Configuration(
    host = "http://localhost/DeviceServer"
)


# Enter a context with an instance of the API client
with DeviceServer.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = DeviceServer.DevicesApi(api_client)
    device_id = 'device_id_example' # str | 

    try:
        # PUT Calibration
        api_response = api_instance.put_auto_calibrate_turntable(device_id)
        print("The response of DevicesApi->put_auto_calibrate_turntable:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DevicesApi->put_auto_calibrate_turntable: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **device_id** | **str**|  | 

### Return type

**str**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**400** | Bad Request |  -  |
**401** | Unauthorized |  -  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |
**405** | Method Not Allowed |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **put_device_deprecated**
> str put_device_deprecated(device_id=device_id, config_file_name=config_file_name, device_serial=device_serial)

PUT Add evice

Add device to database.

### Example


```python
import DeviceServer
from DeviceServer.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost/DeviceServer
# See configuration.py for a list of all supported configuration parameters.
configuration = DeviceServer.Configuration(
    host = "http://localhost/DeviceServer"
)


# Enter a context with an instance of the API client
with DeviceServer.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = DeviceServer.DevicesApi(api_client)
    device_id = 'device_id_example' # str | Device UUID (optional)
    config_file_name = 'config_file_name_example' # str | Config file name (optional)
    device_serial = 'device_serial_example' # str | Device Serial (optional)

    try:
        # PUT Add evice
        api_response = api_instance.put_device_deprecated(device_id=device_id, config_file_name=config_file_name, device_serial=device_serial)
        print("The response of DevicesApi->put_device_deprecated:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DevicesApi->put_device_deprecated: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **device_id** | **str**| Device UUID | [optional] 
 **config_file_name** | **str**| Config file name | [optional] 
 **device_serial** | **str**| Device Serial | [optional] 

### Return type

**str**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**201** | Created |  -  |
**400** | Bad Request |  -  |
**401** | Unauthorized |  -  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |
**405** | Method Not Allowed |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **put_device_device_id_description**
> PutDeviceDeviceIdDescription200Response put_device_device_id_description(device_id, description)

PUT a description for a Device

Set a new descriptoin of a Device.

### Example


```python
import DeviceServer
from DeviceServer.models.put_device_device_id_description200_response import PutDeviceDeviceIdDescription200Response
from DeviceServer.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost/DeviceServer
# See configuration.py for a list of all supported configuration parameters.
configuration = DeviceServer.Configuration(
    host = "http://localhost/DeviceServer"
)


# Enter a context with an instance of the API client
with DeviceServer.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = DeviceServer.DevicesApi(api_client)
    device_id = 'e93a8ad5-c8dc-4069-8097-13feb8af9b65' # str | 
    description = 'description_example' # str | 

    try:
        # PUT a description for a Device
        api_response = api_instance.put_device_device_id_description(device_id, description)
        print("The response of DevicesApi->put_device_device_id_description:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DevicesApi->put_device_device_id_description: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **device_id** | **str**|  | 
 **description** | **str**|  | 

### Return type

[**PutDeviceDeviceIdDescription200Response**](PutDeviceDeviceIdDescription200Response.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**400** | Bad Request |  -  |
**401** | Unauthorized |  -  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |
**405** | Method Not Allowed |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **put_device_device_id_name**
> PutDeviceDeviceIdName200Response put_device_device_id_name(device_id, name)

PUT a name for a Device

Set a new name for a Device.

### Example


```python
import DeviceServer
from DeviceServer.models.put_device_device_id_name200_response import PutDeviceDeviceIdName200Response
from DeviceServer.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost/DeviceServer
# See configuration.py for a list of all supported configuration parameters.
configuration = DeviceServer.Configuration(
    host = "http://localhost/DeviceServer"
)


# Enter a context with an instance of the API client
with DeviceServer.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = DeviceServer.DevicesApi(api_client)
    device_id = 'device_id_example' # str | id of device 
    name = 'name_example' # str | name to apply to device

    try:
        # PUT a name for a Device
        api_response = api_instance.put_device_device_id_name(device_id, name)
        print("The response of DevicesApi->put_device_device_id_name:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DevicesApi->put_device_device_id_name: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **device_id** | **str**| id of device  | 
 **name** | **str**| name to apply to device | 

### Return type

[**PutDeviceDeviceIdName200Response**](PutDeviceDeviceIdName200Response.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**400** | Bad Request |  -  |
**401** | Unauthorized |  -  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |
**405** | Method Not Allowed |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **put_device_id_label**
> str put_device_id_label(device_id, port_index, label)

PUT a Port label

Sets the label for a Port by index.

### Example


```python
import DeviceServer
from DeviceServer.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost/DeviceServer
# See configuration.py for a list of all supported configuration parameters.
configuration = DeviceServer.Configuration(
    host = "http://localhost/DeviceServer"
)


# Enter a context with an instance of the API client
with DeviceServer.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = DeviceServer.DevicesApi(api_client)
    device_id = 'device_id_example' # str | 
    port_index = 56 # int | 
    label = 'Example lable' # str | new label for port

    try:
        # PUT a Port label
        api_response = api_instance.put_device_id_label(device_id, port_index, label)
        print("The response of DevicesApi->put_device_id_label:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DevicesApi->put_device_id_label: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **device_id** | **str**|  | 
 **port_index** | **int**|  | 
 **label** | **str**| new label for port | 

### Return type

**str**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**400** | Bad Request |  -  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |
**405** | Method Not Allowed |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **put_device_port_module_led_state**
> str put_device_port_module_led_state(device_id, port_index, module_index, state)

PUT state of Port Module LED

Set state of Port Module Led.

### Example


```python
import DeviceServer
from DeviceServer.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost/DeviceServer
# See configuration.py for a list of all supported configuration parameters.
configuration = DeviceServer.Configuration(
    host = "http://localhost/DeviceServer"
)


# Enter a context with an instance of the API client
with DeviceServer.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = DeviceServer.DevicesApi(api_client)
    device_id = 'device_id_example' # str | UUID of device
    port_index = 56 # int | Index of Port
    module_index = 56 # int | Index of Module
    state = True # bool | True = LED on, False = LED off

    try:
        # PUT state of Port Module LED
        api_response = api_instance.put_device_port_module_led_state(device_id, port_index, module_index, state)
        print("The response of DevicesApi->put_device_port_module_led_state:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DevicesApi->put_device_port_module_led_state: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **device_id** | **str**| UUID of device | 
 **port_index** | **int**| Index of Port | 
 **module_index** | **int**| Index of Module | 
 **state** | **bool**| True &#x3D; LED on, False &#x3D; LED off | 

### Return type

**str**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**201** | Created |  -  |
**400** | Bad Request |  -  |
**401** | Unauthorized |  -  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |
**405** | Method Not Allowed |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **put_device_port_module_relay_state**
> str put_device_port_module_relay_state(device_id, port_index, module_index, relay_index, state)

PUT state of Port Module Relay

Set state of Port Module Relay.

### Example


```python
import DeviceServer
from DeviceServer.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost/DeviceServer
# See configuration.py for a list of all supported configuration parameters.
configuration = DeviceServer.Configuration(
    host = "http://localhost/DeviceServer"
)


# Enter a context with an instance of the API client
with DeviceServer.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = DeviceServer.DevicesApi(api_client)
    device_id = 'device_id_example' # str | UUID of device
    port_index = 56 # int | Index of Port
    module_index = 56 # int | Index of Module
    relay_index = 56 # int | Index of Relay
    state = True # bool | True = LED on, False = LED off

    try:
        # PUT state of Port Module Relay
        api_response = api_instance.put_device_port_module_relay_state(device_id, port_index, module_index, relay_index, state)
        print("The response of DevicesApi->put_device_port_module_relay_state:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DevicesApi->put_device_port_module_relay_state: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **device_id** | **str**| UUID of device | 
 **port_index** | **int**| Index of Port | 
 **module_index** | **int**| Index of Module | 
 **relay_index** | **int**| Index of Relay | 
 **state** | **bool**| True &#x3D; LED on, False &#x3D; LED off | 

### Return type

**str**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**201** | Created |  -  |
**400** | Bad Request |  -  |
**401** | Unauthorized |  -  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |
**405** | Method Not Allowed |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **put_device_rotation_angle**
> str put_device_rotation_angle(device_id, target_angle)

PUT Rotation

Put rotation state of Turntable.

### Example


```python
import DeviceServer
from DeviceServer.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost/DeviceServer
# See configuration.py for a list of all supported configuration parameters.
configuration = DeviceServer.Configuration(
    host = "http://localhost/DeviceServer"
)


# Enter a context with an instance of the API client
with DeviceServer.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = DeviceServer.DevicesApi(api_client)
    device_id = 'device_id_example' # str | 
    target_angle = 56 # int | Target Angle

    try:
        # PUT Rotation
        api_response = api_instance.put_device_rotation_angle(device_id, target_angle)
        print("The response of DevicesApi->put_device_rotation_angle:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DevicesApi->put_device_rotation_angle: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **device_id** | **str**|  | 
 **target_angle** | **int**| Target Angle | 

### Return type

**str**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**400** | Bad Request |  -  |
**401** | Unauthorized |  -  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |
**405** | Method Not Allowed |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **put_device_rotation_angle_continuous**
> str put_device_rotation_angle_continuous(device_id, target_angle, direction=direction)

PUT Continious Rotation

Put continious rotation angle for Device.

### Example


```python
import DeviceServer
from DeviceServer.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost/DeviceServer
# See configuration.py for a list of all supported configuration parameters.
configuration = DeviceServer.Configuration(
    host = "http://localhost/DeviceServer"
)


# Enter a context with an instance of the API client
with DeviceServer.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = DeviceServer.DevicesApi(api_client)
    device_id = 'device_id_example' # str | 
    target_angle = 56 # int | Target Angle
    direction = 56 # int | Direction of rotation (optional)

    try:
        # PUT Continious Rotation
        api_response = api_instance.put_device_rotation_angle_continuous(device_id, target_angle, direction=direction)
        print("The response of DevicesApi->put_device_rotation_angle_continuous:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DevicesApi->put_device_rotation_angle_continuous: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **device_id** | **str**|  | 
 **target_angle** | **int**| Target Angle | 
 **direction** | **int**| Direction of rotation | [optional] 

### Return type

**str**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**400** | Bad Request |  -  |
**401** | Unauthorized |  -  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |
**405** | Method Not Allowed |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **put_device_rotation_speed**
> str put_device_rotation_speed(device_id, speed)

PUT Turntable Speed

Put the Turntable speed.

### Example


```python
import DeviceServer
from DeviceServer.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost/DeviceServer
# See configuration.py for a list of all supported configuration parameters.
configuration = DeviceServer.Configuration(
    host = "http://localhost/DeviceServer"
)


# Enter a context with an instance of the API client
with DeviceServer.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = DeviceServer.DevicesApi(api_client)
    device_id = 'device_id_example' # str | 
    speed = 3.4 # float | Desired Speed

    try:
        # PUT Turntable Speed
        api_response = api_instance.put_device_rotation_speed(device_id, speed)
        print("The response of DevicesApi->put_device_rotation_speed:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DevicesApi->put_device_rotation_speed: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **device_id** | **str**|  | 
 **speed** | **float**| Desired Speed | 

### Return type

**str**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**400** | Bad Request |  -  |
**401** | Unauthorized |  -  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |
**405** | Method Not Allowed |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **put_devices_led_index**
> str put_devices_led_index(device_id, led_index, state)

PUT state of Led

Set Led at index on selected Device

### Example


```python
import DeviceServer
from DeviceServer.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost/DeviceServer
# See configuration.py for a list of all supported configuration parameters.
configuration = DeviceServer.Configuration(
    host = "http://localhost/DeviceServer"
)


# Enter a context with an instance of the API client
with DeviceServer.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = DeviceServer.DevicesApi(api_client)
    device_id = 'device_id_example' # str | UUID of device
    led_index = 56 # int | Index of LED
    state = True # bool | True = LED on, False = LED off

    try:
        # PUT state of Led
        api_response = api_instance.put_devices_led_index(device_id, led_index, state)
        print("The response of DevicesApi->put_devices_led_index:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DevicesApi->put_devices_led_index: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **device_id** | **str**| UUID of device | 
 **led_index** | **int**| Index of LED | 
 **state** | **bool**| True &#x3D; LED on, False &#x3D; LED off | 

### Return type

**str**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**201** | Created |  -  |
**400** | Bad Request |  -  |
**401** | Unauthorized |  -  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |
**405** | Method Not Allowed |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **put_devices_ports**
> str put_devices_ports(device_id, port_index, state)

PUT state of port

Set state of Port.

### Example


```python
import DeviceServer
from DeviceServer.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost/DeviceServer
# See configuration.py for a list of all supported configuration parameters.
configuration = DeviceServer.Configuration(
    host = "http://localhost/DeviceServer"
)


# Enter a context with an instance of the API client
with DeviceServer.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = DeviceServer.DevicesApi(api_client)
    device_id = 'device_id_example' # str | UUID of device
    port_index = 56 # int | Index of port
    state = 56 # int | state id to switch to, 1 or more

    try:
        # PUT state of port
        api_response = api_instance.put_devices_ports(device_id, port_index, state)
        print("The response of DevicesApi->put_devices_ports:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DevicesApi->put_devices_ports: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **device_id** | **str**| UUID of device | 
 **port_index** | **int**| Index of port | 
 **state** | **int**| state id to switch to, 1 or more | 

### Return type

**str**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**201** | Created |  -  |
**400** | Bad Request |  -  |
**401** | Unauthorized |  -  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |
**405** | Method Not Allowed |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **put_halt_rotation**
> str put_halt_rotation(device_id)

PUT Halt Rotation

Stop the rotation of the Turntable.

### Example


```python
import DeviceServer
from DeviceServer.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost/DeviceServer
# See configuration.py for a list of all supported configuration parameters.
configuration = DeviceServer.Configuration(
    host = "http://localhost/DeviceServer"
)


# Enter a context with an instance of the API client
with DeviceServer.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = DeviceServer.DevicesApi(api_client)
    device_id = 'device_id_example' # str | 

    try:
        # PUT Halt Rotation
        api_response = api_instance.put_halt_rotation(device_id)
        print("The response of DevicesApi->put_halt_rotation:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DevicesApi->put_halt_rotation: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **device_id** | **str**|  | 

### Return type

**str**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**201** | Created |  -  |
**400** | Bad Request |  -  |
**404** | Not Found |  -  |
**405** | Method Not Allowed |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **put_port_led_state**
> str put_port_led_state(device_id, port_index, led_index, state)

PUT state of Port LED

Set state of Led by Port Led Index.

### Example


```python
import DeviceServer
from DeviceServer.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost/DeviceServer
# See configuration.py for a list of all supported configuration parameters.
configuration = DeviceServer.Configuration(
    host = "http://localhost/DeviceServer"
)


# Enter a context with an instance of the API client
with DeviceServer.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = DeviceServer.DevicesApi(api_client)
    device_id = 'device_id_example' # str | UUID of device
    port_index = 56 # int | Index of Port
    led_index = 56 # int | Index of Led
    state = True # bool | True = LED on, False = LED off

    try:
        # PUT state of Port LED
        api_response = api_instance.put_port_led_state(device_id, port_index, led_index, state)
        print("The response of DevicesApi->put_port_led_state:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DevicesApi->put_port_led_state: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **device_id** | **str**| UUID of device | 
 **port_index** | **int**| Index of Port | 
 **led_index** | **int**| Index of Led | 
 **state** | **bool**| True &#x3D; LED on, False &#x3D; LED off | 

### Return type

**str**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**201** | Created |  -  |
**400** | Bad Request |  -  |
**401** | Unauthorized |  -  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |
**405** | Method Not Allowed |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **put_port_port_id_label**
> str put_port_port_id_label(port_id, label=label)

PUT the label for a Port

Set the label for the Port by port_id.

### Example


```python
import DeviceServer
from DeviceServer.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost/DeviceServer
# See configuration.py for a list of all supported configuration parameters.
configuration = DeviceServer.Configuration(
    host = "http://localhost/DeviceServer"
)


# Enter a context with an instance of the API client
with DeviceServer.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = DeviceServer.DevicesApi(api_client)
    port_id = 'port_id_example' # str | id of port for which label applies
    label = 'label_example' # str | new label for the given port (optional)

    try:
        # PUT the label for a Port
        api_response = api_instance.put_port_port_id_label(port_id, label=label)
        print("The response of DevicesApi->put_port_port_id_label:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DevicesApi->put_port_port_id_label: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **port_id** | **str**| id of port for which label applies | 
 **label** | **str**| new label for the given port | [optional] 

### Return type

**str**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**201** | Created |  -  |
**400** | Bad Request |  -  |
**401** | Unauthorized |  -  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |
**405** | Method Not Allowed |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **put_port_port_id_state_label**
> str put_port_port_id_state_label(port_id, state_label=state_label, state_index=state_index)

PUT state label

Update the state label by state index on the port.

### Example


```python
import DeviceServer
from DeviceServer.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost/DeviceServer
# See configuration.py for a list of all supported configuration parameters.
configuration = DeviceServer.Configuration(
    host = "http://localhost/DeviceServer"
)


# Enter a context with an instance of the API client
with DeviceServer.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = DeviceServer.DevicesApi(api_client)
    port_id = 'port_id_example' # str | id of port for which state label applies
    state_label = 'state_label_example' # str | New state label for the given port (optional)
    state_index = 56 # int | State index  (optional)

    try:
        # PUT state label
        api_response = api_instance.put_port_port_id_state_label(port_id, state_label=state_label, state_index=state_index)
        print("The response of DevicesApi->put_port_port_id_state_label:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DevicesApi->put_port_port_id_state_label: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **port_id** | **str**| id of port for which state label applies | 
 **state_label** | **str**| New state label for the given port | [optional] 
 **state_index** | **int**| State index  | [optional] 

### Return type

**str**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**201** | Created |  -  |
**400** | Bad Request |  -  |
**401** | Unauthorized |  -  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |
**405** | Method Not Allowed |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **put_ports_pulse**
> str put_ports_pulse(device_id, port_index, time, state)

PUT Port into state for period of time

Pulse Port from one state to another for a period of time in seconds.

### Example


```python
import DeviceServer
from DeviceServer.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost/DeviceServer
# See configuration.py for a list of all supported configuration parameters.
configuration = DeviceServer.Configuration(
    host = "http://localhost/DeviceServer"
)


# Enter a context with an instance of the API client
with DeviceServer.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = DeviceServer.DevicesApi(api_client)
    device_id = 'device_id_example' # str | UUID of device
    port_index = 56 # int | Index of port
    time = 3.4 # float | time in seconds to press for 0.1 = 100ms
    state = 56 # int | state to switch to

    try:
        # PUT Port into state for period of time
        api_response = api_instance.put_ports_pulse(device_id, port_index, time, state)
        print("The response of DevicesApi->put_ports_pulse:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DevicesApi->put_ports_pulse: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **device_id** | **str**| UUID of device | 
 **port_index** | **int**| Index of port | 
 **time** | **float**| time in seconds to press for 0.1 &#x3D; 100ms | 
 **state** | **int**| state to switch to | 

### Return type

**str**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**201** | Created |  -  |
**400** | Bad Request |  -  |
**401** | Unauthorized |  -  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |
**405** | Method Not Allowed |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **put_relay_state**
> str put_relay_state(device_id, index, state)

PUT state of Relay

Put state of Relay at index

### Example


```python
import DeviceServer
from DeviceServer.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost/DeviceServer
# See configuration.py for a list of all supported configuration parameters.
configuration = DeviceServer.Configuration(
    host = "http://localhost/DeviceServer"
)


# Enter a context with an instance of the API client
with DeviceServer.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = DeviceServer.DevicesApi(api_client)
    device_id = 'device_id_example' # str | 
    index = 56 # int | index of relay to set state
    state = True # bool | state to put

    try:
        # PUT state of Relay
        api_response = api_instance.put_relay_state(device_id, index, state)
        print("The response of DevicesApi->put_relay_state:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DevicesApi->put_relay_state: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **device_id** | **str**|  | 
 **index** | **int**| index of relay to set state | 
 **state** | **bool**| state to put | 

### Return type

**str**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**400** | Bad Request |  -  |
**401** | Unauthorized |  -  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |
**405** | Method Not Allowed |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **put_serial_test_message_deprecated**
> str put_serial_test_message_deprecated(device_id, port_index, serial_message)

Serial Message Test

Send a serial message to the device SerialUSB bus.

### Example


```python
import DeviceServer
from DeviceServer.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost/DeviceServer
# See configuration.py for a list of all supported configuration parameters.
configuration = DeviceServer.Configuration(
    host = "http://localhost/DeviceServer"
)


# Enter a context with an instance of the API client
with DeviceServer.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = DeviceServer.DevicesApi(api_client)
    device_id = 'device_id_example' # str | Device ID
    port_index = 3.4 # float | Port Index
    serial_message = 'serial_message_example' # str | Serial message to SerialUSB

    try:
        # Serial Message Test
        api_response = api_instance.put_serial_test_message_deprecated(device_id, port_index, serial_message)
        print("The response of DevicesApi->put_serial_test_message_deprecated:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DevicesApi->put_serial_test_message_deprecated: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **device_id** | **str**| Device ID | 
 **port_index** | **float**| Port Index | 
 **serial_message** | **str**| Serial message to SerialUSB | 

### Return type

**str**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**400** | Bad Request |  -  |
**401** | Unauthorized |  -  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |
**405** | Method Not Allowed |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **put_state_by_port_id**
> str put_state_by_port_id(port_id, state)

PUT state of port

Set State of Port by id.

### Example


```python
import DeviceServer
from DeviceServer.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost/DeviceServer
# See configuration.py for a list of all supported configuration parameters.
configuration = DeviceServer.Configuration(
    host = "http://localhost/DeviceServer"
)


# Enter a context with an instance of the API client
with DeviceServer.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = DeviceServer.DevicesApi(api_client)
    port_id = 'port_id_example' # str | id of port to set
    state = 56 # int | state id to switch to, 1 or more

    try:
        # PUT state of port
        api_response = api_instance.put_state_by_port_id(port_id, state)
        print("The response of DevicesApi->put_state_by_port_id:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DevicesApi->put_state_by_port_id: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **port_id** | **str**| id of port to set | 
 **state** | **int**| state id to switch to, 1 or more | 

### Return type

**str**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**201** | Created |  -  |
**400** | Bad Request |  -  |
**401** | Unauthorized |  -  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |
**405** | Method Not Allowed |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

