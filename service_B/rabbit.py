import aio_pika
from config import RABBITMQ_URL, RESULT_QUEUE
from models import TaskStore
import asyncio

task_store = TaskStore()


async def consume_results():
    while True:
        try:
            connection = await aio_pika.connect_robust(RABBITMQ_URL)
            channel = await connection.channel()
            queue = await channel.declare_queue(RESULT_QUEUE, durable=True)

            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    async with message.process():
                        payload = message.body.decode()
                        print("Got result:", payload)
                        task_id, status = payload.split(":", 1)
                        await task_store.update_task(task_id, status)
        except Exception as e:
            print("⚠️ Failed to connect to RabbitMQ. Retrying in 5s...", str(e))
            await asyncio.sleep(5)
