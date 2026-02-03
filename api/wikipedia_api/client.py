from typing import Optional, AsyncGenerator
import itertools
import httpx
from httpx import Response
import asyncio
from urllib import parse
from pydantic import BaseModel, Field


class Page(BaseModel):
    pageid: int
    title: str
    transcludedin: "Optional[list[Page]]" = None
    description: Optional[str] = None


class WikipediaResponseQuery(BaseModel):
    pages: dict[str, Page]


class WikipediaResponse(BaseModel):
    continue_field: Optional[dict[str, str]] = Field(alias="continue", default=None)
    query: WikipediaResponseQuery


class Client:
    async def api_request(
        self,
        url: str = "https://en.wikipedia.org/w/api.php",
        params: dict[str, str | int] = {},
        backoff: int = 1,
        retries: int = 3,
    ) -> Response:
        headers: dict[str, str] = {
            "User-Agent": "Atlas-2 https://github.com/jnathan02222/atlas-2",
        }

        # Sometimes the request just fails randomly
        # todo: could probably use a more specific Exception type to handle retries
        for i in range(retries):
            try:
                async with httpx.AsyncClient() as client:
                    request: Response = await client.get(
                        url=url, params=params, headers=headers, timeout=30.0
                    )
                break
            except Exception as e:
                if i == retries - 1:
                    raise e

        # On too many requests implement exponential backoff
        # todo: is there a way to do this with httpx?
        if request.status_code == 429 and backoff < 32:
            await asyncio.sleep(backoff)
            return await self.api_request(url, params, backoff * 2)
        elif not request.status_code == 200:
            raise Exception(f"{request.status_code} error: {request.text}")

        return request

    async def paginated_api_request(
        self, params: dict[str, str | int], continue_accessor: str
    ) -> AsyncGenerator[WikipediaResponse]:
        data = WikipediaResponse(**(await self.api_request(params=params)).json())
        yield data
        while data.continue_field:
            params[continue_accessor] = data.continue_field[continue_accessor]
            data = WikipediaResponse(**(await self.api_request(params=params)).json())
            yield data

    async def transcludedin(self, title: str) -> AsyncGenerator[Page]:
        async def process_data(data: WikipediaResponse) -> AsyncGenerator[Page]:
            for p in data.query.pages.values():
                page = p
                break

            if page and page.transcludedin:
                batches: list[tuple[Page]] = list(
                    itertools.batched(page.transcludedin, 50)
                )
                for batch in batches:
                    async for page in self.description(
                        [str(page.pageid) for page in batch]
                    ):
                        yield page

        params: dict[str, str | int] = {
            "action": "query",
            "titles": title,
            "prop": "transcludedin",
            "format": "json",
            "tilimit": 500,
            "tinamespace": 0,  # Main pages
        }

        async for data in self.paginated_api_request(params, "ticontinue"):
            async for page in process_data(data):
                yield page

    async def description(self, pageids: list[str]) -> AsyncGenerator[Page]:
        params: dict[str, str | int] = {
            "action": "query",
            "pageids": "|".join(pageids),
            "prop": "description",
            "format": "json",
        }
        data = WikipediaResponse(**(await self.api_request(params=params)).json())
        for page in data.query.pages.values():
            yield page

    async def wikihtml(self, title: str) -> str:
        return (
            await self.api_request(
                url=f"https://en.wikipedia.org/wiki/{title_to_url(title)}",
            )
        ).text


def strip_braces(title: str) -> str:
    # Useful to normalize titles like "Beatles (Band)"
    # We know the Beatles is a band
    braces_index = title.find(" (")
    if braces_index == -1:
        return title
    return title[:braces_index]


def title_to_url(title: str) -> str:
    # Seems to be how Wikipedia does it, but we should probably find a specification
    # For some reason brackets get replaced
    return parse.quote(title.replace(" ", "_")).replace("%28", "(").replace("%29", ")")


def url_to_title(url: str) -> str:
    # Reverse of above
    return parse.unquote(url).replace("/wiki/", "").replace("_", " ")
