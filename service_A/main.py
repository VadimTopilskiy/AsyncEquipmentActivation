from fastapi import FastAPI
import asyncio
import random
from fastapi.responses import JSONResponse

app = FastAPI()


@app.post("/api/v1/equipment/cpe/{id}")
async def configure(id: str):
    await asyncio.sleep(60)
    if random.choice([True, False]):
        return JSONResponse(status_code=200, content={"code": 200, "message": "success"})
    return JSONResponse(status_code=500, content={"code": 500, "message": "Internal provisioning exception"})
