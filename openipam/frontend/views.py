from django.shortcuts import render

# Create your views here.


def index(request, *args, **kwargs):
    """Frontend SPA view"""
    return render(request, "frontend/index.html", {})
