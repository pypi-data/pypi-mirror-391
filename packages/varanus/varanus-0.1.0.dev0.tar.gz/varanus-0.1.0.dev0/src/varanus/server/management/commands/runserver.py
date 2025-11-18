import uvicorn
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        uvicorn.run(
            "varanus.server.asgi:application",
            port=9000,
            reload=settings.DEBUG,
        )
