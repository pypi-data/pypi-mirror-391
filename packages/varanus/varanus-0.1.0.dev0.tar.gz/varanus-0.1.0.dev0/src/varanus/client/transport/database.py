import uuid
from urllib.parse import SplitResult

from django.db import transaction

from varanus import events
from varanus.server import models

from .base import BaseTransport


class ModelTransport(BaseTransport):
    def __init__(self, url: SplitResult, environment: str):
        self.environment = environment

    def ping(self, info: events.NodeInfo):
        site = models.Site.objects.get()
        models.Node.update(info, site=site, environment=self.environment)

    @transaction.atomic
    def send(self, event: events.Context):
        site = models.Site.objects.get()
        models.Context.from_event(
            event,
            event_id=uuid.uuid4(),
            site=site,
            environment=self.environment,
        )
