# aiosatisfactory

This is an async Python library for Satisfactory dedicated server's APIs.

This work is based off the official documentation that is provided with the game files or is also available on the official [wiki](https://satisfactory.wiki.gg)

## Lightweight API [(docs)](https://satisfactory.wiki.gg/wiki/Dedicated_servers/Lightweight_Query_API)
This API should be used to poll the server state before making most of the https requests \
No errors are raised but you must check if the query was succesful

### Usage:
```python
from aiosatisfactory import SatisfactoryServer
import time

client = SatisfactoryServer("server.ip")
query = await client.lightweight.query(time.time_ns()) #We use time to generate a Cookie
    if query is not None:
        print(query.response)
```

## Https API [(docs)](https://satisfactory.wiki.gg/wiki/Dedicated_servers/HTTPS_API)
This API requires the *session* parameter to be set in the *SatisfactoryServer* constructor \
It does raise an *ErrorResponse* exeption if the function you try to execute fails

### Usage:
```python
import asyncio
from aiosatisfactory import SatisfactoryServer

async def main():

    with aiohttp.ClientSession() as session:
        client = SatisfactoryServer("server.ip", session=session)
        try:
            response = await client.https.api.health_check()
            print(response.health)
        except ErrorResponse as e:
            print(f"Error: {e.error_code, e.error_message, e.error_details}")

asyncio.run(main())
```