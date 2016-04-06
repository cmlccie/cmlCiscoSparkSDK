cmlCiscoSparkSDK
==================

Overview
--------
Provides classes for representing Cisco Spark API interfaces and JSON objects as native Python objects and method calls.

* Leverages iterators and RFC5988 web linking to provide efficient 'paging' of response data.

* All Cisco Spark JSON objects and attributes are represented as native python objects.
   * As new Cisco Spark attributes are added and returned by the Spark cloud service, they will be automatically available in the respective Python objects - no library update required.
   * New object types can be quickly created and modeled by subclassing the provided SparkDataObject or JSONData base classes.
   * API methods can easily be set to return your custom sub-classed objects (return_type=YourClass).

* Create API connection objects that encapsulate all neccessary API elements (URLs, authentication, headers, and RESTful request parameters) into a simple 'connection object.'
   * API defaults are provided to make getting connected simple, and can be easily overridden if needed.
   * The only setting required to get connected is your Cisco Spark Authentication Token (see [developer.ciscospark.com](https://developer.ciscospark.com/getting-started.html)).
   * All API calls are provided as simple method calls on the API connection objects.

### Examples

```python
from cmlCiscoSparkSDK import CiscoSparkAPI

authentication_token = "abcdefg..."
api = CiscoSparkAPI(authentication_token)

rooms = api.get_rooms(max=10)    # Returns an iterator providing support for RFC5988 paging

for room in rooms:               # Efficiently iterates through returned objects
    print room.title             # JSON objects are represented as native Python objects
```


ToDo
----
* Extend the provided SparkDataObjects (Room, Person, etc.) to incorporate relevant API method calls.
* Provide a 'client' convenience class to expose API calls as simple properties and iterators.
* Documentation (module, class, and function docstrings and examples).
* Complete package and module custom exception classes.