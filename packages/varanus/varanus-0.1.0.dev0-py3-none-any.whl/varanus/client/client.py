import platform
from importlib.metadata import distributions
from typing import Union
from urllib.parse import urlsplit

from varanus.events import Context, NodeInfo

from ..utils import import_string
from .context import VaranusContext, current_context
from .loggers import QueryLogger
from .transport.base import BaseTransport


def install_query_logger(logger):
    def handler(sender, **kwargs):
        if logger not in kwargs["connection"].execute_wrappers:
            kwargs["connection"].execute_wrappers.append(logger)

    return handler


class VaranusClient:
    environment: str | None
    transport: BaseTransport

    request_attr: str
    logger_name: str
    tags: dict

    include_headers: Union[list, bool, None]
    exclude_headers: list | None
    sensitive_headers = set(
        [
            "authorization",
            "cookie",
            "proxy-authorization",
        ]
    )

    scheme_transports = {
        "test": "varanus.client.transport.test.TestTransport",
        "http": "varanus.client.transport.http.HttpTransport",
        "https": "varanus.client.transport.http.HttpTransport",
        "db": "varanus.client.transport.database.ModelTransport",
    }

    send_all: bool
    configured = False

    def setup(
        self,
        dsn,
        request_attr="varanus",
        environment=None,
        transport_class=None,
        logger_name="varanus.request",
        tags=None,
        include_headers=None,
        exclude_headers=None,
        log_queries: bool | int = False,
        log_query_params=False,
        query_metrics=False,
        send_all=False,
        install=None,
    ):
        url = urlsplit(dsn)
        self.environment = environment
        if transport_class is None:
            transport_class = self.scheme_transports.get(url.scheme)
            if transport_class is None:
                raise ValueError(f"No transport class found for `{url.scheme}`")
        if isinstance(transport_class, str):
            transport_class = import_string(transport_class)
        self.transport = transport_class(url, self.environment)
        self.request_attr = request_attr
        self.logger_name = logger_name
        self.tags = tags or {}
        self.include_headers = include_headers
        self.exclude_headers = exclude_headers
        if log_queries or query_metrics:
            try:
                # The logger is installed as early as possible, and for all connections.
                from django.db.backends.signals import connection_created

                # Create a single QueryLogger to be used by all connections.
                self.query_logger = QueryLogger(
                    log_queries,
                    log_query_params,
                    query_metrics,
                )
                # Install it in each new connection (if it's not already installed).
                connection_created.connect(
                    install_query_logger(self.query_logger),
                    weak=False,
                )
            except ImportError:
                pass
        self.send_all = send_all
        self.configured = True
        if install:
            if not isinstance(install, list):
                raise TypeError(
                    "The varanus middleware can only be automatically installed into a list."
                )
            if "django.contrib.auth.middleware.AuthenticationMiddleware" in install:
                idx = install.index(
                    "django.contrib.auth.middleware.AuthenticationMiddleware"
                )
                install.insert(idx + 1, "varanus.client.middleware.VaranusMiddleware")
            elif "django.middleware.common.CommonMiddleware" in install:
                idx = install.index("django.middleware.common.CommonMiddleware")
                install.insert(idx + 1, "varanus.client.middleware.VaranusMiddleware")
            else:
                install.append("varanus.client.middleware.VaranusMiddleware")
        return self

    def send(self, *events: Context):
        for e in events:
            self.transport.send(e)

    def ping(self):
        self.transport.ping(
            NodeInfo(
                name=platform.node(),
                platform=platform.platform(),
                python_version=platform.python_version(),
                packages={d.name: d.version for d in distributions()},
            )
        )

    def log(self, level, message, *args, **kwargs):
        if ctx := current_context.get():
            kwargs.setdefault("stacklevel", 2)
            ctx.log(level, message, *args, **kwargs)

    def raw_exception(self, exception, tags: dict | None = None):
        if ctx := current_context.get():
            ctx.raw_exception(exception, tags=tags)

    def metric(self, name, value: float = 0.0, tags: dict | None = None):
        if ctx := current_context.get():
            ctx.metric(name, value, tags=tags)

    def context(self, name: str, tags: dict | None = None):
        if ctx := current_context.get():
            return ctx.context(name, tags)
        else:
            return VaranusContext(self, name, tags or self.tags)


client = VaranusClient()
