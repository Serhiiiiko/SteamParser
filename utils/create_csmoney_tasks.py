# utils/create_csmoney_tasks.py
import asyncio

from common.env_var import EnvVar
from common.redis_connector import RedisConnector
from price_monitoring.models.csmoney import CsmoneyTask
from price_monitoring.parsers.csmoney.task_scheduler import RedisTaskScheduler


def generate_tasks() -> list[CsmoneyTask]:
    # CS.MONEY API has changed - using the main domain now
    # The old inventories.cs.money subdomain no longer exists
    fmt = (
        "https://cs.money/1.0/market/sell-orders/730"
        "?hasTradeLock=false&hasTradeLock=true"
        "&limit=60&maxPrice={max_price}&minPrice={min_price}"
    )

    result = []
    value = 0.2
    step = 0.1

    while value < 500:
        new_value = round(value + step, 2)
        step = value
        url = fmt.format(min_price=value, max_price=new_value)
        result.append(CsmoneyTask(url=url))
        value = new_value
    
    # Also try a simple test URL
    test_url = "https://cs.money/1.0/market/sell-orders/730?limit=10"
    result.insert(0, CsmoneyTask(url=test_url))
    
    return result


async def main():
    redis = RedisConnector.create(
        host=EnvVar.get("REDIS_HOST"),
        port=EnvVar.get("REDIS_PORT"),
        db=EnvVar.get("REDIS_DB"),
        password=EnvVar.get("REDIS_PASSWORD"),
    )
    scheduler = RedisTaskScheduler(redis)
    await scheduler.clear()
    tasks = generate_tasks()
    print(f"Generated {len(tasks)} tasks.")
    print(f"Sample URL: {tasks[0].url}")
    for task in tasks:
        await scheduler.append_task(task)


if __name__ == "__main__":
    asyncio.run(main())