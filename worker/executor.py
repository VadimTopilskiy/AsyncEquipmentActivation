import asyncio
import httpx
from aio_pika import connect_robust, Message, DeliveryMode
from aio_pika.exceptions import AMQPConnectionError

RABBITMQ_URL = "amqp://user:password@rabbitmq/"
TASK_QUEUE = "task_queue"
RESULT_QUEUE = "task_results"
MAX_RETRIES = 3


async def wait_for_rabbitmq(max_attempts=10):
    for attempt in range(1, max_attempts + 1):
        try:
            connection = await connect_robust(RABBITMQ_URL)
            await connection.close()
            print("RabbitMQ доступен.")
            return
        except AMQPConnectionError:
            print(f"Ожидаем RabbitMQ... попытка {attempt}/{max_attempts}")
            await asyncio.sleep(3)
    raise Exception("RabbitMQ недоступен после 10 попыток.")


async def process_task(body: bytes):
    payload = body.decode()
    task_id, equipment_id, json_payload = payload.split("|", 2)

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            async with httpx.AsyncClient(verify=False, timeout=65.0) as client:
                response = await client.post(
                    f"http://service_a:8001/api/v1/equipment/cpe/{equipment_id}",
                    content=json_payload,
                    headers={"Content-Type": "application/json"},
                )
            if response.status_code == 200:
                return f"{task_id}:COMPLETED"
            else:
                return f"{task_id}:FAILED"
        except Exception as e:
            print(f"Попытка {attempt}: ошибка {e}")
            if attempt == MAX_RETRIES:
                return f"{task_id}:FAILED"
            await asyncio.sleep(2 ** attempt)  # экспоненциальная задержка


async def main():
    await wait_for_rabbitmq()

    connection = await connect_robust(RABBITMQ_URL)
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=10)

    task_queue = await channel.declare_queue(TASK_QUEUE, durable=True)
    result_exchange = channel.default_exchange

    print("Worker готов к обработке задач.")

    async with task_queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                result = await process_task(message.body)
                print("Отправка результата:", result)
                await result_exchange.publish(
                    Message(
                        body=result.encode(),
                        delivery_mode=DeliveryMode.PERSISTENT,
                    ),
                    routing_key=RESULT_QUEUE
                )


if __name__ == "__main__":
    asyncio.run(main())
