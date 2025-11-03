"""
Core VPN detection logic
"""

import httpx
from datetime import datetime
import pytz
from fastapi import Request


async def get_ip_location(ip: str) -> dict:
    """Get geolocation by IP address"""
    async with httpx.AsyncClient(timeout=5.0) as client:
        is_local_ip = (
            ip == "unknown"
            or ip.startswith("127.")
            or ip.startswith("192.168.")
            or ip.startswith("10.")
        )

        effective_ip = ip
        if is_local_ip:
            try:
                # For local IPs, fetch the public IP to allow for local testing
                response = await client.get("https://api.ipify.org?format=json")
                response.raise_for_status()
                effective_ip = response.json()["ip"]
            except Exception as e:
                print(f"Error getting public IP from ipify: {e}")
                # Fallback to local if ipify fails
                return {
                    "timezone": "UTC",
                    "country": "Local",
                    "city": "Local",
                    "lat": 0,
                    "lon": 0,
                }

        try:
            # Get geolocation from the effective IP
            response = await client.get(
                f"http://ip-api.com/json/{effective_ip}?fields=status,country,city,timezone,lat,lon"
            )
            response.raise_for_status()
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
            print(f"Error getting geolocation for IP {effective_ip}: {e}")

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
