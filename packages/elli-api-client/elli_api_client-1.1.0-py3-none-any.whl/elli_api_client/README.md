# Elli API Client

[![PyPI version](https://badge.fury.io/py/elli-api-client.svg)](https://badge.fury.io/py/elli-api-client)
[![Python versions](https://img.shields.io/pypi/pyversions/elli-api-client.svg)](https://pypi.org/project/elli-api-client/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Python client library for the Elli Charging API with OAuth2 PKCE authentication.

> **Note:** This package is ready for use in Home Assistant HACS integrations!
> All dependencies (httpx, pydantic, pydantic-settings) are automatically installed.

## Installation

```bash
pip install elli-api-client
```

## Usage

```python
from elli_api_client import ElliAPIClient

# Create client (loads config from .env)
with ElliAPIClient() as client:
    # Login
    token = client.login("your.email@example.com", "your_password")

    # Get stations
    stations = client.get_stations()
    for station in stations:
        print(f"Station: {station.name} ({station.id})")

    # Get charging sessions
    sessions = client.get_charging_sessions(include_momentary_speed=True)
    for session in sessions:
        if session.lifecycle_state == "active":  # Active session
            print(f"Currently charging: {session.energy_consumption_wh / 1000:.2f} kWh")
            if session.momentary_charging_speed_watts:
                print(f"Power: {session.momentary_charging_speed_watts / 1000:.2f} kW")
            if session.charging_state:
                print(f"State: {session.charging_state}")

    # Get accumulated data for a station
    data = client.get_accumulated_charging(station_id="your-station-id")
    print(f"Total energy: {data['energy_consumption_wh'] / 1000:.2f} kWh")
```

## Configuration

Configuration is loaded from environment variables (`.env` file):

```env
# Required
ELLI_EMAIL=your.email@example.com
ELLI_PASSWORD=your_password

# Optional OAuth2 settings (defaults work for official Elli app)
ELLI_AUTH_BASE_URL=https://login.elli.eco
ELLI_API_BASE_URL=https://api.elli.eco
ELLI_CLIENT_ID=vFGCyS5GUbctkPk1FfcNH6TrDtyfUCwX
ELLI_REDIRECT_URI=com.elli.ios.emsp://login.elli.eco/ios/com.elli.ios.emsp/callback
ELLI_AUDIENCE=https://api.elli.eco/
ELLI_SCOPE=offline_access openid profile
```

**Note:** All configuration values have sensible defaults from the official Elli iOS app.

## Models

### TokenResponse
- `access_token: str`
- `refresh_token: str`
- `id_token: str`
- `token_type: str`
- `expires_in: int`
- `scope: str`

### Station
- `id: str`
- `name: str`
- `serial_number: Optional[str]`
- `model: Optional[str]`
- `firmware_version: Optional[str]`

### ChargingSession
- `id: str`
- `station_id: str`
- `start_date_time: str`
- `energy_consumption_wh: Optional[int]` - Energy consumed in this session (Wh)
- `momentary_charging_speed_watts: Optional[int]` - Current charging power (W)
- `lifecycle_state: Optional[str]` - Session lifecycle state (active, completed, aborted)
- `charging_state: Optional[str]` - Current charging state (charging, paused, idle)
- `connector_id: Optional[int]` - Connector number
- `authentication_method: Optional[str]` - Authentication method (private_card_owned, app)
- `authorization_mode: Optional[str]` - Authorization mode
- `rfid_card_id: Optional[str]` - RFID card ID
- `rfid_card_serial_number: Optional[str]` - RFID card serial number
- `end_date_time: Optional[str]` - Session end time
- `last_updated: Optional[str]` - Last update timestamp
