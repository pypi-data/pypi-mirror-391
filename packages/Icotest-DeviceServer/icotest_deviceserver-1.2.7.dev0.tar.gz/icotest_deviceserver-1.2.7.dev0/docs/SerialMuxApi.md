# DeviceServer.SerialMuxApi

All URIs are relative to *http://localhost/DeviceServer*

Method | HTTP request | Description
------------- | ------------- | -------------
[**put_serial_test_message**](SerialMuxApi.md#put_serial_test_message) | **PUT** /SerialMux/{device_id}/Ports/{port_index}/SerialMessage | Serial Message Test


# **put_serial_test_message**
> str put_serial_test_message(device_id, port_index, serial_message)

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
    api_instance = DeviceServer.SerialMuxApi(api_client)
    device_id = 'device_id_example' # str | Device ID
    port_index = 3.4 # float | Port Index
    serial_message = 'serial_message_example' # str | Serial message to SerialUSB

    try:
        # Serial Message Test
        api_response = api_instance.put_serial_test_message(device_id, port_index, serial_message)
        print("The response of SerialMuxApi->put_serial_test_message:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SerialMuxApi->put_serial_test_message: %s\n" % e)
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

