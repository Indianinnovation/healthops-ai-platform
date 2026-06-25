"""Simple load test for the API."""
import asyncio
import httpx
import time

BASE_URL = "http://localhost:8000"
CONCURRENT = 20
TOTAL_REQUESTS = 100


async def make_request(client: httpx.AsyncClient):
    resp = await client.post("/anomaly", json={
        "claims_denial_rate": 0.12, "avg_processing_days": 14,
        "member_satisfaction": 4.2, "readmission_rate": 0.10,
    })
    return resp.status_code


async def main():
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30) as client:
        start = time.time()
        tasks = [make_request(client) for _ in range(TOTAL_REQUESTS)]
        results = await asyncio.gather(*tasks)
        elapsed = time.time() - start

    success = sum(1 for r in results if r == 200)
    print(f"Results: {success}/{TOTAL_REQUESTS} succeeded in {elapsed:.2f}s")
    print(f"RPS: {TOTAL_REQUESTS / elapsed:.1f}")


if __name__ == "__main__":
    asyncio.run(main())
