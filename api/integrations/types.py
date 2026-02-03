from typing import Optional
from pydantic import BaseModel
from enum import StrEnum

type ArtistId = int


class Relation(StrEnum):
    WIKIPEDIA = "WIKIPEDIA"
    INSPIRED = "INSPIRED"


class Artist(BaseModel):
    id: ArtistId  # A unique id to identify an artist
    name: str  # Display name - potentially not unique, don't use as identifier
    wikipedia_title: Optional[str] = None
    wikipedia_description: Optional[str] = None
    wikipedia_summary: Optional[str] = None


class Edge(BaseModel):
    source: Artist
    target: Artist
    # Relation type does not guarantee that any of the following are present
    # todo: should this be the case? What way would there be to capture the fact
    # that properties depends on the Relation type?
    wikipedia_description: Optional[str] = None
