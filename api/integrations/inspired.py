from integrations.base import Base
from integrations.types import Artist, Edge, Relation
from bs4 import BeautifulSoup
import logging
from db import DB

logger = logging.getLogger(__name__)


# Does it really make sense to make this an integration?
# It's kinda hooking onto existing relationships
class Inspired(Base):
    async def get_edges(self, artist: Artist) -> list[Edge]:
        edges: list[Edge] = []
        db = DB()
        for edge in await db.get_edge_detailed(artist.id):
            # for edge in await db.get_edge_data(edge.source.id, edge.target.id):
            if edge.wikipedia_description:
                # Now ask LLM if the description directly implies inspiration
                # But then we won't be able to label the write way
                # Hmm, see class comment
                print(edge.source.name)
                print(edge.target.name)
                print(
                    BeautifulSoup(edge.wikipedia_description, "html.parser").get_text()
                )

        return edges

    def get_relationship_label(self) -> Relation:
        return Relation.INSPIRED

    def should_skip_adding_artists(self) -> bool:
        return True
