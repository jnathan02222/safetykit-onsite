from integrations.base import Base
from integrations.types import Artist, Edge, Relation
from typing import AsyncGenerator
from bs4 import BeautifulSoup
from wikipedia_api.client import Client, strip_braces, url_to_title
import logging

logger = logging.getLogger(__name__)


class Wikipedia(Base):
    # Wikipedia integration: scrape runs in ~4 hours on my Macbook M2
    def __init__(self) -> None:
        self.api_client: Client = Client()
        # todo: A useful addition would be to have deeper links (ie. the works of Radiohead and The Cardigans both appear in Romeo + Juliet)

    async def get_vertices(self) -> AsyncGenerator[Artist]:
        # Scrape all pages that use the 'Template:Infobox musical artist' template
        # This is a better alternative to using the category system, which isn't very well maintained
        self.wikipedia_artists: dict[str, Artist] = {}
        async for page in self.api_client.transcludedin(
            "Template:Infobox musical artist"
        ):
            artist = Artist(
                id=page.pageid,
                name=strip_braces(page.title),
                wikipedia_title=page.title,
                wikipedia_description=page.description,
            )

            self.wikipedia_artists[page.title] = artist

            yield artist

    async def get_edges(self, artist: Artist) -> list[Edge]:
        # Wrap because we don't want failures to stop the entire job - though early fails while scraping artists are fine
        # To be fair, this function is now relatively stable
        # todo: A better strategy would be to mark failures for future retries
        # this way we can skip artists that are already up to date
        try:
            if not artist.wikipedia_title:
                return []
            # It turns out parsing HTML is a lot easier than parsing Wikitext
            html: str = await self.api_client.wikihtml(artist.wikipedia_title)
            soup = BeautifulSoup(html, "html.parser")

            edges: list[Edge] = []

            already_linked: set[str] = set()

            # Check all links in the html for the page
            # If it links to an artist (using our somewhat finicky matching method)
            # then add an edge.
            for link in soup.find_all("a"):
                if link.parent and link.parent.name == "p":
                    # Skip anything that doesn't belond to paragraph, these are typically
                    # templates / tables, and are usually a weak relationship anyway
                    href = link.get("href")
                    if not isinstance(href, str):
                        continue
                    # Potentially finicky way to match links to other artists
                    link_title: str = url_to_title(href)
                    if (
                        self.exists_artist(link_title)
                        and link_title not in already_linked
                    ):
                        edges.append(
                            Edge(
                                source=artist,
                                target=self.get_artist(link_title),
                                wikipedia_description=str(
                                    link.parent
                                ),  # Don't prettify or it adds a lot of bad looking whitespace :()
                            )
                        )
                        # We skip all other links to the same artist, assuming the first is the most important
                        already_linked.add(link_title)

            return edges
        except Exception:
            logger.error(f"Processing links for {artist.name} failed")
            return []

    def get_relationship_label(self) -> Relation:
        return Relation.WIKIPEDIA

    def exists_artist(self, name: str) -> bool:
        return name in self.wikipedia_artists

    def get_artist(self, name: str) -> Artist:
        return self.wikipedia_artists[name]
