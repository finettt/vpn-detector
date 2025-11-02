"""
Core VPN detection logic
"""

import httpx
from datetime import datetime
import pytz
from fastapi import Request


def get_client_ip(request: Request) -> str:
    """Get client IP address"""
    # Check headers for proxy/load balancers
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()

    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    # Fallback to direct IP
    if request.client:
        return request.client.host

    return "unknown"


async def get_ip_location(ip: str) -> dict:
    """Get geolocation by IP address"""
    if (
        ip == "unknown"
        or ip.startswith("127.")
        or ip.startswith("192.168.")
        or ip.startswith("10.")
    ):
        return {
            "timezone": "UTC",
            "country": "Local",
            "city": "Local",
            "lat": 0,
            "lon": 0,
        }

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"http://ip-api.com/json/{ip}?fields=status,country,city,timezone,lat,lon"
            )
            data = response.json()

            if data.get("status") == "success":
                return {
                    "timezone": data.get("timezone", "UTC"),
                    "country": data.get("country", "Unknown"),
                    "city": data.get("city", "Unknown"),
                    "lat": data.get("lat", 0),
                    "lon": data.get("lon", 0),
                }
    except Exception as e:
        print(f"Error getting geolocation: {e}")

    return {
        "timezone": "UTC",
        "country": "Unknown",
        "city": "Unknown",
        "lat": 0,
        "lon": 0,
    }


def calculate_timezone_offset(timezone_name: str) -> float:
    """Calculate UTC offset for timezone in hours"""
    try:
        tz = pytz.timezone(timezone_name)
        now = datetime.now(tz)
        offset = now.utcoffset()
        if offset:
            return offset.total_seconds() / 3600
    except Exception:
        pass
    return 0


def is_vpn_detected(
    ip_timezone: str, client_timezone: str, threshold: float = 1.0
) -> dict:
    """
    Determine if VPN is being used

    Args:
        ip_timezone: Timezone based on IP geolocation
        client_timezone: Client timezone
        threshold: Threshold for hour difference to determine VPN

    Returns:
        dict with analysis results
    """
    ip_offset = calculate_timezone_offset(ip_timezone)
    client_offset = calculate_timezone_offset(client_timezone)

    difference = abs(ip_offset - client_offset)

    # If difference exceeds threshold, VPN is likely being used
    is_vpn = difference > threshold

    return {
        "is_vpn_detected": is_vpn,
        "ip_timezone": ip_timezone,
        "ip_utc_offset": ip_offset,
        "client_timezone": client_timezone,
        "client_utc_offset": client_offset,
        "difference_hours": round(difference, 2),
        "confidence": "high"
        if difference > 3
        else "medium"
        if difference > threshold
        else "low",
    }
