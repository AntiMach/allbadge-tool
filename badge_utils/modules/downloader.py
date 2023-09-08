import asyncio
from pathlib import Path
from typing import Callable
from httpx import AsyncClient
from itertools import product


class AllbadgeDownloader:
    REGIONS: list[tuple[str, str]] = [
        ("JPN", "j0ITmVqVgfUxe0O9"),
        ("EUR", "J6la9Kj8iqTvAPOq"),
        ("USA", "OvbmGLZ9senvgV3K"),
    ]

    VERSIONS = [
        "v130",
        "v131",
    ]

    BASE_URL = "https://npdl.cdn.nintendowifi.net/p01/nsa/{}/data/allbadge_{}.dat?tm=2"
    FILE_TEMPLATE = "allbadge_{}_{}.dat"

    _report_message: Callable[[str], None]
    _report_progress: Callable[[int], None]
    queue: asyncio.Queue
    client: AsyncClient

    def set_message_callback(self, callback: Callable[[str], None]) -> None:
        self._report_message = callback

    def set_progress_callback(self, callback: Callable[[int], None]) -> None:
        self._report_progress = lambda: callback(self._done / self._total)

    def start(self, destination: str):
        self._dir = Path(destination)
        self._total = 0
        self._done = 0

        self._report_message("Starting downloads")

        asyncio.run(self._start())

        self._report_message("Finished downloads")

    async def _start(self):
        self.queue = asyncio.Queue()

        async with AsyncClient(follow_redirects=True, verify=False) as self.client:
            coros = [self.try_download(*region, version) for region, version in product(self.REGIONS, self.VERSIONS)]
            await asyncio.gather(*coros)

    async def try_download(self, region_name: str, region_code: str, version: str):
        url = self.BASE_URL.format(region_code, version)
        file = self._dir / self.FILE_TEMPLATE.format(region_name, version)

        try:
            return await self.download(url, file)
        except Exception:
            self._report_message(f"Failed to download {file.name}")

    async def download(self, url: str, file: Path):
        if not file.parent.exists():
            self._report_message(f"Destination for {file.name} does not exist.")
            return

        self._report_message(f"Started downloading {file.name}")

        async with self.client.stream("GET", url) as res:
            self._total += int(res.headers["Content-Length"])
            self._report_progress()

            with file.open("wb") as fp:
                async for chunk in res.aiter_bytes(1024 * 1024):
                    self._done += len(chunk)
                    self._report_progress()
                    fp.write(chunk)

        self._report_message(f"Finished downloading {file.name}")
