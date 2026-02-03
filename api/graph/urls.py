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
from db import DB
from wikipedia_api.client import title_to_url
from bs4 import BeautifulSoup
from integrations.types import Artist, Edge, ArtistId, Relation

api = NinjaAPI()

db = DB()
db.init_index()


@api.get("/edges", response=list[Edge])
async def edges(
    request, artist: ArtistId, relations: list[Relation] = [Relation.WIKIPEDIA]
):
    response = await db.get_edges(artist, relations)
    return response


@api.get("/search", response=list[Artist])
async def search(request, name: str):
    response = await db.get_artists(name)
    return response


@api.get("/edge-description", response=list[Edge])
async def edge_description(request, source: ArtistId, target: ArtistId):
    response = []
    for edge in await db.get_edge_data(source, target):
        if edge.wikipedia_description and edge.target.wikipedia_title:
            # Remove all references, links and highlight the target
            soup = BeautifulSoup(edge.wikipedia_description, "html.parser")
            for sup in soup.find_all("sup"):
                sup.decompose()
            for a in soup.find_all("a"):
                if (
                    a.get("href")
                    == f"/wiki/{title_to_url(edge.target.wikipedia_title)}"
                ):
                    a.name = "mark"
                else:
                    a.unwrap()

            edge.wikipedia_description = str(soup)
        response.append(edge)
    return response


@api.get("/shortest-path", response=list[list[Artist]])
async def shortest_path(request, start_id: ArtistId, end_id: ArtistId):
    return await db.shortest_path(start_id, end_id)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
]
