# earth_rover_mini_sdk

API for the Earth Rover Mini. Uploaded to PyPi, installable using pip.

## Installation

Windows:
```bash
py -m pip install earth_rover_mini_sdk
```

Unix/MacOS:
```bash
python3 -m pip install earth_rover_mini_sdk
```

## Example Usage

Below is an example of how to use the code.

```python
from earth_rover_mini_sdk import EarthRoverMini_API

def main():
    rover = EarthRoverMini_API("192.168.11.1", 8888)

    rover.connect()

    print("\n[TEST] Ping test:")

    rover.safe_ping()

    print("\n[TEST] Move test (3s at speed=60, angular=360):")

    rover.move(1, 60, 0)

    rover.disconnect()
```
