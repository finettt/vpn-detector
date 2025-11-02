"""
API Endpoints for VPN Detector
"""

from fastapi import APIRouter, Request
from typing import Optional
from datetime import datetime

from src.core.detector import get_client_ip, get_ip_location, is_vpn_detected

router = APIRouter()


@router.get("/health")
async def health_check():
    """Service health check"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@router.get("/detect")
async def detect_vpn_get(
    request: Request, timezone: Optional[str] = None, threshold: float = 1.0
):
    """
    Detect VPN (GET request)

    Args:
        timezone: Client timezone (e.g., 'Asia/Omsk')
        threshold: Threshold for hour difference to determine VPN (default 1.0)
    """
    client_ip = get_client_ip(request)

    # Get geolocation by IP
    location = await get_ip_location(client_ip)

    # If timezone not specified, use UTC
    if not timezone:
        timezone = "UTC"

    # Analyze for VPN
    vpn_analysis = is_vpn_detected(
        ip_timezone=location["timezone"], client_timezone=timezone, threshold=threshold
    )

    return {
        "client_ip": client_ip,
        "ip_location": location,
        "vpn_analysis": vpn_analysis,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.post("/detect")
async def detect_vpn_post(request: Request, data: dict):
    """
    Detect VPN (POST request)

    Body:
        {
            "timezone": "Asia/Omsk",  // required
            "threshold": 1.0  // optional
        }
    """
    client_ip = get_client_ip(request)
    timezone = data.get("timezone", "UTC")
    threshold = data.get("threshold", 1.0)

    # Get geolocation by IP
    location = await get_ip_location(client_ip)

    # Analyze for VPN
    vpn_analysis = is_vpn_detected(
        ip_timezone=location["timezone"], client_timezone=timezone, threshold=threshold
    )

    return {
        "client_ip": client_ip,
        "ip_location": location,
        "vpn_analysis": vpn_analysis,
        "timestamp": datetime.utcnow().isoformat(),
    }
