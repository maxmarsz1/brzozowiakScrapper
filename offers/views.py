from django.shortcuts import render
from django.http import HttpResponse


def sample_view(request):
    html = "<html><body>view</body></html>"
    return HttpResponse(html)