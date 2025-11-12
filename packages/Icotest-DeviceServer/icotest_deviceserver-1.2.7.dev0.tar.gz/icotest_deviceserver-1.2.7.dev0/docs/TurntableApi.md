# DeviceServer.TurntableApi

All URIs are relative to *http://localhost/DeviceServer*

Method | HTTP request | Description
------------- | ------------- | -------------
[**turntable_get_device_rotation_angle**](TurntableApi.md#turntable_get_device_rotation_angle) | **GET** /Turntable/{device_id}/Rotation | GET Rotation Angle
[**turntable_get_device_rotation_speed**](TurntableApi.md#turntable_get_device_rotation_speed) | **GET** /Turntable/{device_id}/Speed | GET Turntable Speed
[**turntable_get_image**](TurntableApi.md#turntable_get_image) | **GET** /Turntable/{device_id}/Image | GET Image
[**turntable_get_image_names**](TurntableApi.md#turntable_get_image_names) | **GET** /Turntable/{device_id}/ImageNames | GET Image Names
[**turntable_get_turntable_calibration_data**](TurntableApi.md#turntable_get_turntable_calibration_data) | **GET** /Turntable/{device_id}/Calibration | GET Turntable Calibration Values
[**turntable_put_auto_calibrate_turntable**](TurntableApi.md#turntable_put_auto_calibrate_turntable) | **PUT** /Turntable/{device_id}/Calibration | PUT Calibration
[**turntable_put_device_rotation_angle**](TurntableApi.md#turntable_put_device_rotation_angle) | **PUT** /Turntable/{device_id}/Rotation | PUT Rotation
[**turntable_put_device_rotation_angle_continuous**](TurntableApi.md#turntable_put_device_rotation_angle_continuous) | **PUT** /Turntable/{device_id}/ContiniousRotation | PUT Continious Rotation
[**turntable_put_device_rotation_speed**](TurntableApi.md#turntable_put_device_rotation_speed) | **PUT** /Turntable/{device_id}/Speed | PUT Turntable Speed
[**turntable_put_halt_rotation**](TurntableApi.md#turntable_put_halt_rotation) | **PUT** /Turntable/{device_id}/HaltRotation | PUT Halt Rotation


# **turntable_get_device_rotation_angle**
> object turntable_get_device_rotation_angle(device_id)

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
    api_instance = DeviceServer.TurntableApi(api_client)
    device_id = 'device_id_example' # str | 

    try:
        # GET Rotation Angle
        api_response = api_instance.turntable_get_device_rotation_angle(device_id)
        print("The response of TurntableApi->turntable_get_device_rotation_angle:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TurntableApi->turntable_get_device_rotation_angle: %s\n" % e)
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

# **turntable_get_device_rotation_speed**
> object turntable_get_device_rotation_speed(device_id)

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
    api_instance = DeviceServer.TurntableApi(api_client)
    device_id = 'device_id_example' # str | 

    try:
        # GET Turntable Speed
        api_response = api_instance.turntable_get_device_rotation_speed(device_id)
        print("The response of TurntableApi->turntable_get_device_rotation_speed:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TurntableApi->turntable_get_device_rotation_speed: %s\n" % e)
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

# **turntable_get_image**
> bytearray turntable_get_image(device_id, image_name=image_name)

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
    api_instance = DeviceServer.TurntableApi(api_client)
    device_id = 'device_id_example' # str | 
    image_name = 'image_name_example' # str | Image Name (optional)

    try:
        # GET Image
        api_response = api_instance.turntable_get_image(device_id, image_name=image_name)
        print("The response of TurntableApi->turntable_get_image:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TurntableApi->turntable_get_image: %s\n" % e)
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

# **turntable_get_image_names**
> object turntable_get_image_names(device_id)

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
    api_instance = DeviceServer.TurntableApi(api_client)
    device_id = 'device_id_example' # str | 

    try:
        # GET Image Names
        api_response = api_instance.turntable_get_image_names(device_id)
        print("The response of TurntableApi->turntable_get_image_names:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TurntableApi->turntable_get_image_names: %s\n" % e)
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

# **turntable_get_turntable_calibration_data**
> object turntable_get_turntable_calibration_data(device_id)

GET Turntable Calibration Values

Get the calibration data for the Device.

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
    api_instance = DeviceServer.TurntableApi(api_client)
    device_id = 'device_id_example' # str | 

    try:
        # GET Turntable Calibration Values
        api_response = api_instance.turntable_get_turntable_calibration_data(device_id)
        print("The response of TurntableApi->turntable_get_turntable_calibration_data:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TurntableApi->turntable_get_turntable_calibration_data: %s\n" % e)
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

# **turntable_put_auto_calibrate_turntable**
> str turntable_put_auto_calibrate_turntable(device_id)

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
    api_instance = DeviceServer.TurntableApi(api_client)
    device_id = 'device_id_example' # str | 

    try:
        # PUT Calibration
        api_response = api_instance.turntable_put_auto_calibrate_turntable(device_id)
        print("The response of TurntableApi->turntable_put_auto_calibrate_turntable:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TurntableApi->turntable_put_auto_calibrate_turntable: %s\n" % e)
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

# **turntable_put_device_rotation_angle**
> str turntable_put_device_rotation_angle(device_id, target_angle)

PUT Rotation

Put rotation state of Turntable

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
    api_instance = DeviceServer.TurntableApi(api_client)
    device_id = 'device_id_example' # str | 
    target_angle = 56 # int | Target Angle

    try:
        # PUT Rotation
        api_response = api_instance.turntable_put_device_rotation_angle(device_id, target_angle)
        print("The response of TurntableApi->turntable_put_device_rotation_angle:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TurntableApi->turntable_put_device_rotation_angle: %s\n" % e)
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

# **turntable_put_device_rotation_angle_continuous**
> str turntable_put_device_rotation_angle_continuous(device_id, target_angle, direction=direction)

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
    api_instance = DeviceServer.TurntableApi(api_client)
    device_id = 'device_id_example' # str | 
    target_angle = 56 # int | Target Angle
    direction = 56 # int | Direction of rotation (optional)

    try:
        # PUT Continious Rotation
        api_response = api_instance.turntable_put_device_rotation_angle_continuous(device_id, target_angle, direction=direction)
        print("The response of TurntableApi->turntable_put_device_rotation_angle_continuous:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TurntableApi->turntable_put_device_rotation_angle_continuous: %s\n" % e)
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

# **turntable_put_device_rotation_speed**
> str turntable_put_device_rotation_speed(device_id, speed)

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
    api_instance = DeviceServer.TurntableApi(api_client)
    device_id = 'device_id_example' # str | 
    speed = 3.4 # float | Desired Speed

    try:
        # PUT Turntable Speed
        api_response = api_instance.turntable_put_device_rotation_speed(device_id, speed)
        print("The response of TurntableApi->turntable_put_device_rotation_speed:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TurntableApi->turntable_put_device_rotation_speed: %s\n" % e)
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

# **turntable_put_halt_rotation**
> str turntable_put_halt_rotation(device_id)

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
    api_instance = DeviceServer.TurntableApi(api_client)
    device_id = 'device_id_example' # str | 

    try:
        # PUT Halt Rotation
        api_response = api_instance.turntable_put_halt_rotation(device_id)
        print("The response of TurntableApi->turntable_put_halt_rotation:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TurntableApi->turntable_put_halt_rotation: %s\n" % e)
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

