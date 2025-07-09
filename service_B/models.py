from typing import Dict
from uuid import uuid4
import asyncio


class TaskStore:
    def __init__(self):
        self._tasks: Dict[str, Dict] = {}
        self._lock = asyncio.Lock()

    async def create_task(self, equipment_id: str, parameters: dict) -> str:
        task_id = str(uuid4())
        async with self._lock:
            self._tasks[task_id] = {
                "equipment_id": equipment_id,
                "parameters": parameters,
                "status": "PENDING"
            }
        return task_id

    async def update_task(self, task_id: str, status: str):
        async with self._lock:
            if task_id in self._tasks:
                self._tasks[task_id]["status"] = status

    async def get_status(self, task_id: str):
        async with self._lock:
            return self._tasks.get(task_id)
