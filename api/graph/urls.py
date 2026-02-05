"""
URL configuration for graph project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI
from integrations.types import ExampleOut, PolicyViolationOut
from data.models import Example, PolicyViolation

api = NinjaAPI()


@api.get("/add", response=int)
async def add(request, a: int, b: int):
    return a + b


@api.get("/subtract", response=int)
async def subtract(request, a: int, b: int):
    return a - b


@api.get("/example", response=list[str])
def list_employees(request):
    return [q.text for q in Example.objects.all()]


@api.get("/policies", response=list[PolicyViolationOut])
def list_policies(request):
    """List all policy violation analysis results."""
    return [
        {
            "id": p.id,
            "url": p.url,
            "title": p.title,
            "is_adderall_sold": p.is_adderall_sold,
            "appears_licensed_pharmacy": p.appears_licensed_pharmacy,
            "uses_visa": p.uses_visa,
            "explanation": p.explanation,
            "screenshot_path": p.screenshot_path,
            "screenshots": p.screenshots,
            "analyzed_at": p.analyzed_at,
        }
        for p in PolicyViolation.objects.all()
    ]


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
]
