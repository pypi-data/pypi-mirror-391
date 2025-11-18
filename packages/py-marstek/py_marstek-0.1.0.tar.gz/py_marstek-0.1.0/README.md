# py-marstek

Python client for Marstek energy storage systems. Provides asynchronous UDP helpers to discover devices and query status information.

## Features

- UDP broadcast discovery of Marstek devices
- Helpers to query ES mode, battery statistics, and PV status
- Simple command builder utilities
- Optional support for multi-interface broadcast via `psutil`

## Installation

```bash
pip install py-marstek
```

## Usage

```python
import asyncio
from pymarstek import MarstekUDPClient, get_es_mode

async def main():
    client = MarstekUDPClient()
    await client.async_setup()
    devices = await client.discover_devices()
    if not devices:
        print("No devices found")
        return

    device_ip = devices[0]["ip"]
    response = await client.send_request(get_es_mode(), device_ip, 30000)
    print(response)

    await client.async_cleanup()

asyncio.run(main())
```

## License

Apache-2.0
