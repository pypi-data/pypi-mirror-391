# earth_rover_mini_plus_sdk

API for the Earth Rover Mini+. Uploaded to PyPi, installable using pip.

## Installation

Windows:
```bash
py -m pip install earth_rover_mini_plus_sdk
```

Unix/MacOS:
```bash
python3 -m pip install earth_rover_mini_plus_sdk
```

## Example Usage

Below is an example of how to use the code.

```python
from earth_rover_mini_plus_sdk import API

async def main():
    rover = API("192.168.11.1", 8888)
    await rover.connect()

    await rover.safe_ping()
    # await rover.ctrl_packet(60, 0)
    await asyncio.sleep(2)
    # await rover.ctrl_packet(0, 0)
    await rover.move(3, 60, 360)
    await asyncio.sleep(1)
    await rover.imu_mag_read()

    await rover.disconnect()
```
