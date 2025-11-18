import uuid

import msgspec
from django.http import HttpRequest, HttpResponseBase, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from varanus import events

from ..models import Context, Node, Site, SiteKey


class APIView(View):
    key: SiteKey
    site: Site
    environment: str

    @csrf_exempt
    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponseBase:
        try:
            self.key = SiteKey.objects.select_related("site").get(
                access_key=request.META.get("HTTP_X_VARANUS_KEY", ""), active=True
            )
            self.environment = request.META.get("HTTP_X_VARANUS_ENVIRONMENT", "")
            self.site = self.key.site
            with self.site.activated():
                result = super().dispatch(request, *args, **kwargs)
                if isinstance(result, HttpResponseBase):
                    return result
                return JsonResponse(result)
        except SiteKey.DoesNotExist:
            return JsonResponse({"error": "Invalid site key."}, status=401)
        except Exception as e:
            raise e
            return JsonResponse({"error": str(e)}, status=400)


class NodePingView(APIView):
    def post(self, request, *args, **kwargs):
        info = msgspec.json.decode(request.body, type=events.NodeInfo)
        node, created, node_update = Node.update(info, self.site, self.environment)
        return node_update.to_dict() if node_update else {}


class IngestView(APIView):
    def post(self, request, *args, **kwargs):
        event = msgspec.json.decode(request.body, type=events.Context)
        context = Context.from_event(
            event,
            event_id=uuid.uuid4(),
            site=self.site,
            environment=self.environment,
        )
        return {"event_id": context.event_id}
