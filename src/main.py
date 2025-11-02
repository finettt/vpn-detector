"""
FastAPI VPN Detector
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from src.api.router import router as api_router

app = FastAPI(
    title="VPN Detector API",
    description="VPN detection based on the difference between IP geolocation and client timezone",
    version="1.0.0",
)

app.include_router(api_router, prefix="/api")
app.mount("/static", StaticFiles(directory="src/static"), name="static")


@app.get("/")
async def read_index():
    return FileResponse("src/static/index.html")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
