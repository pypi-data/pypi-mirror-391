# DeviceServer.DockerApi

All URIs are relative to *http://localhost/DeviceServer*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_container_logs**](DockerApi.md#get_container_logs) | **GET** /Docker/container/logs | GET a Docker container&#39;s logs
[**get_docker_container_names**](DockerApi.md#get_docker_container_names) | **GET** /Docker/containers | GET all Docker containers
[**get_docker_containers_metrics**](DockerApi.md#get_docker_containers_metrics) | **GET** /Docker/containers/metrics | GET Docker container uptimes, versions, statuses and logs for each container


# **get_container_logs**
> bytearray get_container_logs(container_name, timestamps=timestamps, from_datetime=from_datetime, to_datetime=to_datetime, tail=tail)

GET a Docker container's logs

Returns a container's log.

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
    api_instance = DeviceServer.DockerApi(api_client)
    container_name = 'container_name_example' # str | Container's name
    timestamps = True # bool | Show timestamps (optional)
    from_datetime = '2018-03-20T09:12:28Z' # str | Show logs since a given datetime (optional)
    to_datetime = '2018-04-20T09:12:28Z' # str | Show logs that occurred before the given datetime (optional)
    tail = 1000 # int | Show the most recent number of lines (optional) (default to 1000)

    try:
        # GET a Docker container's logs
        api_response = api_instance.get_container_logs(container_name, timestamps=timestamps, from_datetime=from_datetime, to_datetime=to_datetime, tail=tail)
        print("The response of DockerApi->get_container_logs:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DockerApi->get_container_logs: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **container_name** | **str**| Container&#39;s name | 
 **timestamps** | **bool**| Show timestamps | [optional] 
 **from_datetime** | **str**| Show logs since a given datetime | [optional] 
 **to_datetime** | **str**| Show logs that occurred before the given datetime | [optional] 
 **tail** | **int**| Show the most recent number of lines | [optional] [default to 1000]

### Return type

**bytearray**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/octet-stream

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

# **get_docker_container_names**
> object get_docker_container_names()

GET all Docker containers

Returns a list of all Docker containers running on the host.

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
    api_instance = DeviceServer.DockerApi(api_client)

    try:
        # GET all Docker containers
        api_response = api_instance.get_docker_container_names()
        print("The response of DockerApi->get_docker_container_names:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DockerApi->get_docker_container_names: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

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

# **get_docker_containers_metrics**
> object get_docker_containers_metrics()

GET Docker container uptimes, versions, statuses and logs for each container

Returns a list of all Docker containers uptimes and versions.

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
    api_instance = DeviceServer.DockerApi(api_client)

    try:
        # GET Docker container uptimes, versions, statuses and logs for each container
        api_response = api_instance.get_docker_containers_metrics()
        print("The response of DockerApi->get_docker_containers_metrics:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DockerApi->get_docker_containers_metrics: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

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

