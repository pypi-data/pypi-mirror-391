"""Data models for Elli API"""

from typing import Optional

from pydantic import BaseModel


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    id_token: str
    token_type: str
    expires_in: int
    scope: str


class ChargingSession(BaseModel):
    """Charging session data from Elli API."""

    id: str
    station_id: str
    start_date_time: str

    # Energy and power data
    energy_consumption_wh: Optional[int] = None
    momentary_charging_speed_watts: Optional[int] = None

    # Session state
    lifecycle_state: Optional[str] = None
    charging_state: Optional[str] = None

    # Authentication and authorization
    connector_id: Optional[int] = None
    authentication_method: Optional[str] = None
    authorization_mode: Optional[str] = None
    rfid_card_id: Optional[str] = None
    rfid_card_serial_number: Optional[str] = None

    # Timestamps
    end_date_time: Optional[str] = None
    last_updated: Optional[str] = None


class Station(BaseModel):
    id: str
    name: str
    serial_number: Optional[str] = None
    model: Optional[str] = None
    firmware_version: Optional[str] = None
