# Trip Ninja SDK

The Trip Ninja Python SDK is used for interacting with the Trip Ninja API 
through a easy-to-use library and suite of tools.

## Installing

**Python 3.10 or higher is required**

### Linux/MacOS
```
python3 -m pip install -U tn_sdk
```

### Windows
```
py -3 -m pip install -U tn_sdk
```


## Quick Example

```python
import json
import tn_sdk

tn_client = tn_sdk.TnApi()
request_data = {
    "trip_id": "",
    "datasource_responses": {
        "4b69b995e699534c1c644381b760c990795efff9": [
            {
                "pricing_solution_id": "e494c1f1d172380259a61b05990d61cbb68b35a9",
                "total_price": 392.22,
                "segment_source": "travelport",
                "is_private_fare": False,
                "refundable": False,
                "segments": [
                    [
                        {
                            "departure_time": "2025-11-15T16:40:00.000-04:00",
                            "departure_timestamp": 1763239200,
                            "arrival_time": "2025-11-15T17:35:00.000-05:00",
                            "arrival_timestamp": 1763246100,
                            "flight_number": "667",
                            "operating_carrier": "AC",
                            "transportation_type": "flight",
                            "fare_type": "PublicFare",
                            "cabin_class": "E",
                            "from_iata": "YHZ",
                            "to_iata": "YUL"
                        },
                        {
                            "departure_time": "2025-11-15T18:20:00.000-05:00",
                            "departure_timestamp": 1763248800,
                            "arrival_time": "2025-11-15T20:50:00.000-08:00",
                            "arrival_timestamp": 1763268600,
                            "flight_number": "311",
                            "operating_carrier": "AC",
                            "transportation_type": "flight",
                            "fare_type": "PublicFare",
                            "cabin_class": "E",
                            "from_iata": "YUL",
                            "to_iata": "YVR"
                        }
                    ]
                ],
                "baggage": None
            },
        ],
    }
}
request_data_json = json.dumps(request_data)
# JSON encoded string representing the request data
compressed_data = tn_client.prepare_data_for_generate_solutions(request_data_json)
# Compresses the data and returns the compressed_data
```

### Responses
```
# Compressed Data 
eJztlEGL2zAQhe/7K4zPm0WSLdnSrZSWHnoopS20ZTEjW3KcKLaR5C1lyX8vclJnw7pxw9JbBbpI8968EZ/9eBNFURR72/RFU8UiisFVetxbs3HrSm83sDY/tnrjDFQaNmAqp+Pbg64CD64bbKkKq1zftU65WESP4+1YkUrGJedUMc5pkpa4ZGma5FhmDJWco4xTpbXmsYi+T6qwTh6TV2+bsmnrwnVm8E3XHhOrlKcl1rjCGUlyRCgHhiWinKOK4VJKlsuEAj+GPrP0nQdTBGMViyjh5I6QmTKn6p1qfXGYNTT1Fh6U6Tvr52wbFzwfwKtCgw0CDcapmUqr9NBWIM2lomN79+yRfq/50/lnPHOuVA/WD1YVvtmNgxFE6ArjFaafMBMpEgjdIYRWKBUIzcx6wc552PWxiHDGEpJwgtCCHGx4NDObJRMJnbLQv8jy1OwsScrwYhJtmnrti3bYSWVDFMaypYZdryz4AGgZeh90r14vybyF1gWQYGTa/+zH2Q8JlsSBrknyYZCmKd8G4BZkJcimLUoDLjAVv1lsY7td0YCHUP313bfFmbpT9ef38R+L97f/BtxcEHQVLBfATfP8JeASJOgpS/4ScFnOrgc3wfg/uH5C8Qpwv3y8AO7szf2z0/uZv7mEuoY6DN4OxpzdP/kejsr9zf4XgRWmhw==
```

### Unsuccessful Response
```
InvalidDataException: [INVALID_DATA] Input must be a JSON-encoded string
```

---


# Development

## Setup

From an active virtual env, `cd` into the directory
```
pip install -e .
```

> `-e` installs it in [editable](https://pip.pypa.io/en/stable/topics/local-project-installs/#editable-installs) mode. 
> Meaning it will update as you modify the source code without having to re-run the installation command.
