import re

from django.core.exceptions import MiddlewareNotUsed
from django.http import HttpRequest, HttpResponse

from ..events import Request
from .client import client

IP_REGEX = re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")


def get_ip(request: HttpRequest):
    ip_address = request.META.get("HTTP_X_FORWARDED_FOR", "").strip()
    if ip_address:
        ip_address = ip_address.split(",")[0].strip()
    if not ip_address:
        ip_address = request.META.get("REMOTE_ADDR", "127.0.0.1").strip()
    if not IP_REGEX.match(ip_address):
        ip_address = None
    return ip_address


def request_headers(request: HttpRequest):
    headers = {}
    if not client.include_headers:
        return headers
    if client.include_headers is True:
        include = set(name.lower() for name in request.headers)
    else:
        include = set(name.lower() for name in client.include_headers)
    if client.exclude_headers is None:
        exclude = client.sensitive_headers
    else:
        exclude = set(name.lower() for name in client.exclude_headers)
    for name in sorted(include - exclude):
        value = request.headers.get(name)
        if value is not None:
            headers[name] = value
    return headers


class VaranusMiddleware:
    def __init__(self, get_response):
        if not client.configured:
            # TODO: warning
            print("VaranusClient is not configured -- disabling middleware.")
            raise MiddlewareNotUsed()
        client.ping()
        self.get_response = get_response

    def process_exception(self, request, exception):
        # Any value in using request.varanus instead of current context here?
        client.raw_exception(exception)

    def __call__(self, request: HttpRequest):
        with client.context(request.path) as varanus:
            setattr(request, client.request_attr, varanus)
            response = self.get_response(request)
            # TODO: any need for request tags separate from context tags?
            varanus.request = Request(
                host=request.get_host(),
                path=request.path,
                method=request.method or "",
                status=response.status_code,
                headers=request_headers(request),
                size=(
                    len(response.content)
                    if isinstance(response, HttpResponse)
                    else None
                ),
                ip=get_ip(request),
                user=(
                    request.user.get_username()
                    if hasattr(request, "user")
                    and request.user
                    and request.user.is_authenticated
                    else None
                ),
            )
        return response
