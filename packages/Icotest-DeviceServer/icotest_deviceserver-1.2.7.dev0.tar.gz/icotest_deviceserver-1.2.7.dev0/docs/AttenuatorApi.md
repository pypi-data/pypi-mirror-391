# DeviceServer.AttenuatorApi

All URIs are relative to *http://localhost/DeviceServer*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_attenuator_module_state**](AttenuatorApi.md#get_attenuator_module_state) | **GET** /Attenuator/{device_id}/Attenuate | GET attenuation state
[**get_channel_attenuation**](AttenuatorApi.md#get_channel_attenuation) | **GET** /Attenuator/{device_id}/AttenuateChannel | GET attenuation channel state
[**put_attenuator_module_state**](AttenuatorApi.md#put_attenuator_module_state) | **PUT** /Attenuator/{device_id}/Attenuate | PUT attenuation state
[**put_channel_attenuation**](AttenuatorApi.md#put_channel_attenuation) | **PUT** /Attenuator/{device_id}/AttenuateChannel | PUT attenuation state


# **get_attenuator_module_state**
> AttenuationState get_attenuator_module_state(device_id, channel_index, module_index)

GET attenuation state

Get attenuation state by module index.

### Example


```python
import DeviceServer
from DeviceServer.models.attenuation_state import AttenuationState
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
    api_instance = DeviceServer.AttenuatorApi(api_client)
    device_id = 'device_id_example' # str | 
    channel_index = 56 # int | channel index
    module_index = 56 # int | module index

    try:
        # GET attenuation state
        api_response = api_instance.get_attenuator_module_state(device_id, channel_index, module_index)
        print("The response of AttenuatorApi->get_attenuator_module_state:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AttenuatorApi->get_attenuator_module_state: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **device_id** | **str**|  | 
 **channel_index** | **int**| channel index | 
 **module_index** | **int**| module index | 

### Return type

[**AttenuationState**](AttenuationState.md)

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

# **get_channel_attenuation**
> ChannelAttenuationState get_channel_attenuation(device_id, channel_index)

GET attenuation channel state

Get attenuation state sof selected channel

### Example


```python
import DeviceServer
from DeviceServer.models.channel_attenuation_state import ChannelAttenuationState
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
    api_instance = DeviceServer.AttenuatorApi(api_client)
    device_id = 'device_id_example' # str | 
    channel_index = 56 # int | channel index

    try:
        # GET attenuation channel state
        api_response = api_instance.get_channel_attenuation(device_id, channel_index)
        print("The response of AttenuatorApi->get_channel_attenuation:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AttenuatorApi->get_channel_attenuation: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **device_id** | **str**|  | 
 **channel_index** | **int**| channel index | 

### Return type

[**ChannelAttenuationState**](ChannelAttenuationState.md)

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

# **put_attenuator_module_state**
> str put_attenuator_module_state(device_id, channel_index, module_index, value)

PUT attenuation state

Put attenuation state of selected module

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
    api_instance = DeviceServer.AttenuatorApi(api_client)
    device_id = 'device_id_example' # str | 
    channel_index = 56 # int | channel index
    module_index = 56 # int | module index
    value = 56 # int | attenuation value

    try:
        # PUT attenuation state
        api_response = api_instance.put_attenuator_module_state(device_id, channel_index, module_index, value)
        print("The response of AttenuatorApi->put_attenuator_module_state:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AttenuatorApi->put_attenuator_module_state: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **device_id** | **str**|  | 
 **channel_index** | **int**| channel index | 
 **module_index** | **int**| module index | 
 **value** | **int**| attenuation value | 

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

# **put_channel_attenuation**
> str put_channel_attenuation(device_id, channel_index, value)

PUT attenuation state

Put attenuation state of selected channel

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
    api_instance = DeviceServer.AttenuatorApi(api_client)
    device_id = 'device_id_example' # str | 
    channel_index = 56 # int | channel index
    value = 56 # int | attenuation value

    try:
        # PUT attenuation state
        api_response = api_instance.put_channel_attenuation(device_id, channel_index, value)
        print("The response of AttenuatorApi->put_channel_attenuation:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AttenuatorApi->put_channel_attenuation: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **device_id** | **str**|  | 
 **channel_index** | **int**| channel index | 
 **value** | **int**| attenuation value | 

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

