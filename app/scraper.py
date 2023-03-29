import aiohttp
import asyncio
from config import KAKAO_API_OPTION, KAKAO_API_KEY
from pydantic import BaseModel, Field
from typing import Optional, Dict


class Book(BaseModel):
    isbn: str
    title: str
    authors: str
    contents: str
    thumbnail: str
    url: str
    rate: float
    review: Optional[Dict]


class BookScraper:
    def __init__(self):
        self.key = KAKAO_API_KEY
        self.url = KAKAO_API_OPTION["url"]
        self.sort = KAKAO_API_OPTION["sort"]
        self.page = KAKAO_API_OPTION["page"]
        self.size = KAKAO_API_OPTION["size"]

    async def fetch(self, session, url):
        headers = {"authorization": f"KakaoAK {self.key}"}
        async with session.get(url, headers=headers) as response:
            result = await response.json()
            return result["documents"]

    async def scraper(self, keyword):
        urls = [
            f"{self.url}?query={keyword}&size={self.size}&page={i + 1}&sort={self.sort}"
            for i in range(self.page)
        ]
        async with aiohttp.ClientSession() as session:
            all_data = await asyncio.gather(*[self.fetch(session, url) for url in urls])
        result = []
        for data in all_data:
            for i in data:
                book = Book(
                    isbn=i["isbn"].split()[0],
                    title=i["title"],
                    authors=",".join(i["authors"]),
                    contents=i["contents"],
                    thumbnail=i["thumbnail"],
                    url=i["url"],
                    rate=0,
                )
                result.append(book)
        return result


if __name__ == "__main__":
    book = BookScraper()
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    result = asyncio.run(book.scraper("파이썬"))
    for i in result:
        print(i)
