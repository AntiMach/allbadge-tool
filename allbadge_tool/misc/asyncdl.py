import asyncio
from pathlib import Path
from typing import Callable
from httpx import AsyncClient


class AsyncDownloader:
    entries: list[tuple[str, Path]]
    progress_callback: Callable[[float], None]
    client: AsyncClient

    def __init__(self):
        self.entries = []
        self.total_bytes = 0
        self.downloaded_bytes = 0

    def add_entry(self, url: str, outfile: Path):
        self.entries.append((url, outfile))

    def set_progress_callback(self, callback: Callable[[float], None]):
        self.progress_callback = callback

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        async with AsyncClient(verify=False, follow_redirects=True) as self.client:
            await self._start()

    @property
    def _ratio_dowloaded(self):
        return self.downloaded_bytes / self.total_bytes if self.total_bytes else 0.0

    async def _start(self):
        tasks = (self._single_entry(*entry) for entry in self.entries)
        await asyncio.gather(*tasks)

    async def _single_entry(self, url: str, outfile: Path):
        async with self.client.stream("GET", url) as res:
            content_length = int(res.headers.get("Content-Length", 0))
            self.total_bytes += content_length
            outfile.parent.mkdir(parents=True, exist_ok=True)

            with outfile.open("wb") as fp:
                async for chunk in res.aiter_bytes():
                    fp.write(chunk)
                    self.downloaded_bytes += len(chunk)
                    self.progress_callback(self._ratio_dowloaded)

            if not content_length:
                self.total_bytes += self.downloaded_bytes
