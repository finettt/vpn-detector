"""
API Endpoints for VPN Detector
"""

from fastapi import APIRouter, Request
from typing import Optional
from datetime import datetime

from src.core.detector import get_ip_location, is_vpn_detected

router = APIRouter()


@router.get("/health")
async def health_check():
    """Service health check"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@router.post("/detect")
async def detect_vpn_post(data: dict):
    """
    Detect VPN (POST request)

    Body:
        {
            "ip": "8.8.8.8", // required
            "timezone": "America/New_York",  // required
            "threshold": 1.0  // optional
        }
    """
    client_ip = data.get("ip")
    if not client_ip:
        return {"error": "Client IP not provided"}

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
