# VPN Detector API
<img width="658" height="732" alt="image" src="https://github.com/user-attachments/assets/3ced9652-7a7a-42f4-bdca-0574dfc1178b" />

FastAPI application for detecting VPN usage by comparing IP address geolocation with client timezone.

## How It Works

The application detects VPN usage using the following algorithm:
1. Gets the client's IP address
2. Determines geolocation and timezone by IP through the ip-api.com API
3. Compares the timezone from geolocation with the client's reported timezone
4. If the difference exceeds the threshold value (default 1 hour), it's considered that a VPN is being used

## Installation and Running

### Local Running with UV

```bash
# Install UV (if not already installed)
pip install uv

# Install dependencies
uv pip install -r pyproject.toml

# Run the application
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Running with Docker

```bash
# Build the image
docker build -t vpn-detector .

# Run the container
docker run -d -p 8000:8000 --name vpn-detector vpn-detector
```

### Running with Docker Compose

```bash
# Start
docker-compose up -d

# Stop
docker-compose down
```

## API Endpoints

### GET /
API information

### GET /health
Service health check

### GET /detect
Detect VPN

**Parameters:**
- `timezone` (optional): Client timezone (e.g., 'Asia/Omsk')
- `threshold` (optional): Threshold for hour difference to determine VPN (default 1.0)

**Example request:**
```bash
curl "http://localhost:8000/detect?timezone=Asia/Omsk&threshold=1.0"
```

### POST /detect
Detect VPN

**Request body:**
```json
{
    "timezone": "Asia/Omsk",
    "threshold": 1.0
}
```

**Example request:**
```bash
curl -X POST "http://localhost:8000/detect" \
     -H "Content-Type: application/json" \
     -d '{"timezone": "Asia/Omsk", "threshold": 1.0}'
```

## Example Response

```json
{
    "client_ip": "1.2.3.4",
    "ip_location": {
        "timezone": "America/New_York",
        "country": "United States",
        "city": "New York",
        "lat": 40.7128,
        "lon": -74.0060
    },
    "vpn_analysis": {
        "is_vpn_detected": true,
        "ip_timezone": "America/New_York",
        "ip_utc_offset": -5.0,
        "client_timezone": "Asia/Omsk",
        "client_utc_offset": 6.0,
        "difference_hours": 11.0,
        "confidence": "high"
    },
    "timestamp": "2024-01-01T12:00:00.000000"
}
```

## Confidence Levels

- **high**: Difference > 3 hours - high probability of VPN
- **medium**: Difference > 1 hour - medium probability of VPN
- **low**: Difference <= 1 hour - low probability of VPN

## API Documentation

After starting the application, interactive documentation is available:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

```bash
# Install development dependencies
uv pip install -e ".[dev]"

# Run tests
pytest
```

## Features

- Uses the free ip-api.com API for geolocation (45 requests per minute limit)
- Supports proxied requests (X-Forwarded-For, X-Real-IP)
- Local IP addresses (127.0.0.1, 192.168.x.x, 10.x.x.x) are not checked for VPN
