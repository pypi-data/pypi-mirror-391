from urllib.parse import SplitResult

import httpx
import msgspec

from varanus import events

from .base import BaseTransport


class HttpTransport(BaseTransport):
    def __init__(self, url: SplitResult, environment: str):
        path = url.path.rstrip("/")
        self.ping_url = f"{url.scheme}://{url.netloc}{path}/api/ping/"
        self.event_url = f"{url.scheme}://{url.netloc}{path}/api/ingest/"
        self.client = httpx.Client(
            headers={
                "X-Varanus-Key": url.username or "",
                "X-Varanus-Environment": environment or "",
            }
        )

    def ping(self, info: events.NodeInfo):
        self.client.post(self.ping_url, content=msgspec.json.encode(info))

    def send(self, event: events.Context):
        self.client.post(self.event_url, content=msgspec.json.encode(event))
