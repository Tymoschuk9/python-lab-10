from __future__ import annotations

import asyncio
import httpx


async def fetch_one_product(
    client: httpx.AsyncClient,
    semaphore: asyncio.Semaphore,
    url: str,
    max_retries: int = 3,
) -> dict:
    """
    Асинхронне завантаження одного ресурсу через HTTPX
    з використанням Semaphore для обмеження конкурентності
    та логіки Retry з backoff у разі мережевих помилок.
    """
    async with semaphore:
        for attempt in range(1, max_retries + 1):
            try:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
            except (httpx.RequestError, httpx.HTTPStatusError):
                if attempt == max_retries:
                    raise
                await asyncio.sleep(0.1 * attempt)
    raise RuntimeError(f"Не вдалося виконати запит до {url} після {max_retries} спроб")


async def fetch_many_products(
    base_url: str,
    product_ids: list[int],
    timeout: float = 5.0,
    max_concurrent: int = 3,
) -> list[dict]:
    """
    Паралельне завантаження декількох продуктів:
    демонструє роботу asyncio.Task, asyncio.gather, Semaphore, HTTPX та Timeout.
    """
    semaphore = asyncio.Semaphore(max_concurrent)
    async with httpx.AsyncClient(timeout=timeout) as client:
        tasks = [
            asyncio.create_task(
                fetch_one_product(
                    client=client,
                    semaphore=semaphore,
                    url=f"{base_url.rstrip('/')}/products/{pid}",
                )
            )
            for pid in product_ids
        ]
        return list(await asyncio.gather(*tasks))
