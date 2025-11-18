from ..search import ChoiceFacet, DateFilter, Search
from .base import SiteView


class Overview(SiteView):
    template_name = "site/overview.html"

    def get_context(self):
        return {
            "host": self.request.get_host(),
            "scheme": self.request.scheme,
        }


class Logs(SiteView):
    template_name = "site/logs.html"

    def get_context(self):
        return {
            "logs": self.site.logs.select_related("context"),
        }


class Errors(SiteView):
    template_name = "site/errors.html"

    def get_context(self):
        return {
            "errors": self.site.errors.select_related("context"),
        }


class Requests(SiteView):
    template_name = "site/requests.html"

    def get_context(self):
        return {
            "requests": self.site.requests.select_related("context"),
        }


class Queries(SiteView):
    template_name = "site/queries.html"

    class QuerySearch(Search):
        timeframe = DateFilter(field_name="timestamp")
        tags = ChoiceFacet()
        type = ChoiceFacet(field_name="command")
        db = ChoiceFacet()

    def get_context(self):
        qs = self.site.queries.select_related("context")
        s = self.QuerySearch(qs)
        form = s.get_form(self.request.GET or None)
        if form.is_valid():
            print(form.cleaned_data)
        return {
            "queries": qs,
            "filter_form": form,
        }


class Metrics(SiteView):
    template_name = "site/metrics.html"

    def get_context(self):
        return {
            "metrics": self.site.metrics.select_related("context"),
        }
