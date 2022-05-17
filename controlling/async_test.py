import asyncio

async def run_the_job_first():
    while True:
        await asyncio.sleep(10)
        print("Peter je machr")

async def run_the_job_second():
    while True:
        await asyncio.sleep(10)
        print("Vskutku")

async def main():
    task1 = asyncio.create_task(run_the_job_first())
    task2 = asyncio.create_task(run_the_job_second())

    await task1
    await task2

asyncio.run(main())