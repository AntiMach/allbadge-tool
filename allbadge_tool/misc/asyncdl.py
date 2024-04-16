import asyncio
from pathlib import Path
from typing import Callable
from httpx import AsyncClient


class AsyncDownloader:
    _client: AsyncClient
    _entries: list[tuple[str, Path]]
    _done_callback: Callable[[str], None]
    _progress_callback: Callable[[float], None]

    def __init__(self):
        self._entries = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        async with AsyncClient(verify=False, follow_redirects=True) as self._client:
            self._total_bytes = 0
            self._downloaded_bytes = 0
            await self._start()

    # Initializer methods

    def add_entry(self, url: str | None = None, out_file: Path | None = None):
        if url and out_file:
            self._entries.append((url, out_file))

    def set_progress_callback(self, callback):
        self._progress_callback = callback

    def set_done_callback(self, callback):
        self._done_callback = callback

    # Helper methods

    @property
    def _ratio_dowloaded(self):
        return min(self._downloaded_bytes / self._total_bytes if self._total_bytes else 0.0, 1.0)

    async def _start(self):
        await asyncio.gather(*(self._try_download_entry(*entry) for entry in self._entries))

    async def _try_download_entry(self, url: str, outfile: Path):
        try:
            await self._download_entry(url, outfile)
            self._done_callback(outfile, None)
        except Exception as e:
            self._done_callback(outfile, e)

    async def _download_entry(self, url: str, out_file: Path):
        async with self._client.stream("GET", url) as res:
            content_length = None

            if content_length := res.headers.get("Content-Length"):
                content_length = int(content_length)
                self._total_bytes += content_length

            out_file.parent.mkdir(parents=True, exist_ok=True)

            with out_file.open("wb") as fp:
                async for chunk in res.aiter_bytes():
                    fp.write(chunk)
                    self._downloaded_bytes += len(chunk)

                    if not content_length:
                        self._total_bytes += len(chunk)

                    self._progress_callback(self._ratio_dowloaded)
