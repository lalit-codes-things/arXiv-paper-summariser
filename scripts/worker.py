import asyncio

from app.workers.tasks import process_next_job


async def main() -> None:
    processed = await process_next_job()
    print({"processed": processed})


if __name__ == "__main__":
    asyncio.run(main())
