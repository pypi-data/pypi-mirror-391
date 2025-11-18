from .models import Site


def sites(request):
    return {
        "sites": Site.objects.all(),
    }
