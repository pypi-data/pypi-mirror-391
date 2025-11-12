import asyncio
import aiohttp
import time
from statistics import mean

async def fetch(session, url, method="GET", data=None):
    start = time.perf_counter()
    try:
        async with session.request(method, url, data=data) as resp:
            await resp.text()
            duration = time.perf_counter() - start
            return {"status": resp.status, "time": duration}
    except Exception as e:
        return {"status": None, "time": None, "error": str(e)}

async def run_requests(url, n=10, method="GET", data=None):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url, method, data) for _ in range(n)]
        results = await asyncio.gather(*tasks)
        return results

def summarize(results):
    valid = [r for r in results if r["status"]]
    errors = [r for r in results if not r["status"]]

    if not valid:
        return "❌ All requests failed."

    avg_time = mean([r["time"] for r in valid])
    success_rate = (len(valid) / len(results)) * 100

    report = (
        f"Requests sent: {len(results)}\n"
        f"Successful: {len(valid)} ({success_rate:.2f}%)\n"
        f"Avg response time: {avg_time:.3f}s\n"
        f"Failed: {len(errors)}"
    )
    return report

def simulate(url, n=10, method="GET", data=None):
    results = asyncio.run(run_requests(url, n, method, data))
    return summarize(results)
