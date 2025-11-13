# Drivee Client

A Python client library for automation and control of EV Wallbox chargers via the Drivee cloud API.

[![PyPI version](https://badge.fury.io/py/drivee-client.svg)](https://badge.fury.io/py/drivee-client)
[![Python Support](https://img.shields.io/pypi/pyversions/drivee-client.svg)](https://pypi.org/project/drivee-client/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

```bash
pip install drivee-client
```

## Quick Start

```python
import asyncio
from drivee_client import DriveeClient

async def main():
    async with DriveeClient("username", "password") as client:
        await client.init()
        
        # Get charge point info
        charge_point = await client.get_charge_point()
        print(f"Charge point: {charge_point.name}")
        print(f"Status: {charge_point.evse.status}")
        
        # Start charging
        response = await client.start_charging()
        print(f"Started session: {response.session.id}")
        
        # Get charging history
        history = await client.get_charging_history()
        for session in history.sessions:
            print(f"Session {session.id}: {session.energy/1000:.2f}kWh")

if __name__ == "__main__":
    asyncio.run(main())
```

## Features

- **Async/await support** - Built with `aiohttp` for non-blocking I/O
- **Type-safe** - Full type hints with Pydantic models
- **Error handling** - Comprehensive error handling with custom exceptions
- **Rate limiting** - Built-in retry logic with exponential backoff
- **Clean architecture** - Separation of DTOs and business models
- **Domain validation** - Business rule validation in model layer

## Architecture

The client library follows a clear separation of concerns with three main layers:

### Data Transfer Objects (DTOs)

Located in `dtos/`, these are pure data classes that:

- Match the exact structure of API responses
- Use Pydantic for validation and serialization
- Have no business logic
- Follow naming convention: All DTO classes end with 'DTO' suffix
- Are only used within the model layer

### Business Models

Located in `models/`, these classes:

- Encapsulate DTOs and provide business logic
- Expose only business-relevant properties and methods
- Use Protocol-based typing for DTO interfaces
- Handle all business rules and validations
- Are the only classes exposed to the Home Assistant integration

### API Client

The `drivee_client.py` handles:

- REST API communication
- Authentication
- Request/response mapping to DTOs
- Error handling and retries

## Installation

1. Copy the `custom_components/drivee` folder to your Home Assistant's `custom_components` directory.
2. Restart Home Assistant.

## Configuration

1. Go to Home Assistant's Settings > Devices & Services
2. Click "Add Integration"
3. Search for "Drivee"
4. Enter your Drivee API base URL
5. (Optional) Enter your API key if required

## Usage

After configuration, you can control your Drivee device through Home Assistant's interface. The integration will create a switch entity that you can use to control your device.

## Development

To develop or modify this integration:

1. Clone this repository
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Make your changes
4. Test the integration locally
5. Copy the modified files to your Home Assistant's `custom_components` directory

## License

MIT License
