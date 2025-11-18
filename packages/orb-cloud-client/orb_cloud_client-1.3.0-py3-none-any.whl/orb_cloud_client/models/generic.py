# 20251111 This file is here for historic reasons, and backward compatibility.
# this can safely be removed in the future if needed. Make sure to validate the
# imports in other files before doing so.

from __future__ import annotations

from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from .server import OrganizationDeviceResponse, DatasetsRequest, OrganizationsResponse as Organization
from .db import AccountPlan, AccountPlanLimits, AccountConfigEntitlements # noqa
from .config import Datasets, DataPush, DataAPI  # noqa


class IsConnected(Enum):
    integer_0 = 0
    integer_1 = 1


class GeoIPInfo(BaseModel):
    city: Optional[str] = Field(None, examples=['Kirkland'])
    state: Optional[str] = Field(None, examples=['Washington'])
    country: Optional[str] = Field(None, examples=['United States'])
    isp_name: Optional[str] = Field(None, examples=['Comcast Cable'])
    latitude: Optional[float] = Field(None, examples=[47.6784])
    longitude: Optional[float] = Field(None, examples=[-122.1857])
    country_code: Optional[str] = Field(None, examples=['US'])


class DeviceInfo(BaseModel):
    name: Optional[str] = Field(None, examples=['hardy-nca1515'])
    version: Optional[str] = Field(None, examples=['v1.2.3'])
    cpu_count: Optional[int] = Field(None, examples=[4])
    full_name: Optional[str] = Field(
        None, description='device full hostname', examples=['hardy-nca1515']
    )
    operating_system: Optional[str] = Field(None, examples=['linux'])


class NetworkInterface(BaseModel):
    name: Optional[str] = Field(None, examples=[''])
    type: Optional[str] = Field(None, examples=['Ethernet'])
    local_ip: Optional[str] = Field(
        None,
        description='Local IP address of the network interface',
        examples=['192.168.207.172'],
    )
    mac_address: Optional[str] = Field(
        None,
        description='MAC address of the network interface',
        examples=['00:90:0b:a5:de:2a'],
    )


class OrbScore(BaseModel):
    score: Optional[float] = Field(
        None, description='Raw score value', examples=[0.8283297399160232]
    )
    display: Optional[int] = Field(
        None, description='Display score (0-100)', examples=[91]
    )
    included: Optional[bool] = Field(
        None,
        description='Whether there are enough measurements on the subject score that it is conclusive',
        examples=[True],
    )
    value: Optional[float] = Field(
        None,
        description='Raw measurement value (present in leaf components)',
        examples=[38965.44888204175],
    )
    components: Optional[Dict[str, OrbScore]] = Field(
        None, description='Score components breakdown (nested OrbScore objects)'
    )
    duration_ms: Optional[int] = Field(
        None, description='Duration of measurement in milliseconds', examples=[60000]
    )
    score_version: Optional[str] = Field(
        None, description='Version of scoring algorithm', examples=['1.2.0']
    )


class TriggerSpeedtestRequest(BaseModel):
    pass

class Error(BaseModel):
    message: str = Field(
        ..., description='Error message', examples=['Invalid organization ID']
    )
    code: Optional[str] = Field(
        None, description='Error code', examples=['INVALID_ORG_ID']
    )

class SummaryTags(BaseModel):
    geoip: Optional[GeoIPInfo] = None
    device_info: Optional[DeviceInfo] = None
    network_interface: Optional[NetworkInterface] = None

class DeviceSummary(BaseModel):
    tags: Optional[SummaryTags] = None
    version: Optional[str] = Field(
        None, description='Summary version', examples=['0.1.0']
    )
    orb_score: Optional[OrbScore] = None
    created_ts: Optional[int] = Field(
        None, description='Timestamp when summary was created', examples=[1757391432134]
    )
    orb_scores: Optional[List[OrbScore]] = Field(
        None, description='Array of Orb scores for different time windows'
    )

class TempDatasetsRequest(DatasetsRequest):
		duration: str = Field(
				..., description='Duration for temporary dataset configuration', examples=['1h']
		)

class Device(OrganizationDeviceResponse):
    orb_id: str = Field(
        ...,
        description='Unique Orb device identifier',
        examples=['cjwbntmuy97ta4rx3mbrjf2gj8j7'],
    )
    name: str = Field(..., description='Device name', examples=['hardy-house'])
    is_connected: IsConnected = Field(
        ...,
        description='Connection status (0 = disconnected, 1 = connected)',
        examples=[1],
    )
    is_connected_updated_at: Optional[int] = Field(
        None,
        description='Timestamp when connection status was last updated',
        examples=[1757368500851],
    )
    can_notify: Optional[bool] = Field(
        None, description='Whether the device can send notifications', examples=[False]
    )
    summary: DeviceSummary
    created_ts: Optional[int] = Field(
        None, description='Timestamp when device was created', examples=[1757368560803]
    )
    tags: Optional[List[str]] = Field(
        None, description='Device tags', examples=[['dt=Default Configuration']]
    )
    config: Optional[Dict[str, List[str]]] = Field(
        None,
        description='Device configuration user overrides (map of strings to arrays of strings)',
        examples=[
            {
                'datasets.datasets': ['responsiveness_1s', 'speed_results'],
                'datasets.cloud_push': ['identifiable=true', 'responsiveness_1s'],
            }
        ],
    )

OrbScore.model_rebuild()
