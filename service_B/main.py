from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import asyncio
import aio_pika
from config import RABBITMQ_URL, TASK_QUEUE
from rabbit import task_store, consume_results
from fastapi.responses import Response

app = FastAPI()


class ConfigRequest(BaseModel):
    timeoutInSeconds: int
    parameters: dict


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(consume_results())


@app.post("/api/v1/equipment/cpe/{id}")
async def configure_equipment(id: str, request: ConfigRequest):
    if not id or len(id) < 6:
        raise HTTPException(status_code=400, detail="Invalid ID format")
    task_id = await task_store.create_task(id, request.parameters)
    try:
        conn = await aio_pika.connect_robust(RABBITMQ_URL)
        channel = await conn.channel()
        await channel.default_exchange.publish(
            aio_pika.Message(
                body=f"{task_id}|{id}|{request.json()}".encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            ),
            routing_key=TASK_QUEUE
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Queue error: {str(e)}")
    return JSONResponse(content={"code": 200, "taskId": task_id})


@app.get("/api/v1/equipment/cpe/{id}/task/{task_id}")
async def get_status(id: str, task_id: str):
    task = await task_store.get_status(task_id)

    if not task:
        return JSONResponse(
            status_code=404,
            content={"code": 404, "message": "Task not found"}
        )

    if task.get("equipment_id") != id:
        return JSONResponse(
            status_code=404,
            content={"code": 404, "message": "Equipment not found for given task"}
        )

    status = task.get("status", "PENDING")

    if status == "PENDING":
        return Response(status_code=204)
    elif status == "FAILED":
        return JSONResponse(status_code=200, content={"code": 500, "message": "Internal provisioning exception"})

    return JSONResponse(content={"code": 200, "message": "Completed"})
