import asyncio
import logging
import json
from pathlib import Path
from time import time
import asyncio

from aiohttp import ClientSession, ClientConnectorError
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)


class PathError(Exception):
    pass


async def fetch_page(session: ClientSession, url: str) -> str:
    """load a page for next processing"""

    try:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.text()
            else:
                logging.error(f"Failed to fetch {url}: Status {response.status}")
                return ""
    except ClientConnectorError as err:
        logging.error(f"Connection error: {err}")
        return ""


async def parse_quotes(page: str) -> list:
    """parsing of the quotes on page"""
    soup = BeautifulSoup(page, 'lxml')
    quotes = []
    for quote in soup.find_all("div", class_="quote"):
        text = quote.find("span", class_="text").text.strip()
        author = quote.find("small", class_="author").text.strip()
        tags = [tag.text.strip() for tag in quote.find_all("a", class_="tag")]
        quotes.append({"quote": text, "author": author, "tags": tags})
        logging.info(f"parsed quote by {author}")
    return quotes


async def parse_author(session: ClientSession, author_url: str) -> dict:
    """redirecting for every each author page from quote
    and parsing author biography and details"""
    page = await fetch_page(session, author_url)
    if page:
        soup = BeautifulSoup(page, 'lxml')
        author_details = soup.find("div", class_="author-details")

        author_biography = {
            "fullname": author_details.find("h3", class_="author-title").text.strip(),
            "born_date": author_details.find("span", class_="author-born-date").text.strip(),
            "born_location": author_details.find("span", class_="author-born-location").text.strip(),
            "description": author_details.find("div", class_="author-description").text.strip()
        }
        logging.info(f"fetched biography of {author_biography["fullname"]}")
        return author_biography


async def scrape_quotes_and_authors():
    """gathering all data about authors and quotes
    skipping authors if already fetched
    taking to save in save_to_json func"""
    base_url = "https://quotes.toscrape.com"
    authors_urls = set()
    quotes = []
    authors = []

    async with ClientSession() as session:
        page_tasks = [fetch_page(session, f"{base_url}/page/{i}/") for i in range(1, 11)]
        pages = await asyncio.gather(*page_tasks)

        for page in pages:
            if page:
                quotes.extend(await parse_quotes(page))
                soup = BeautifulSoup(page, 'lxml')
                for quote in soup.find_all("div", class_="quote"):
                    authors_urls.add(base_url + quote.find("a")["href"])

        author_tasks = [parse_author(session, url) for url in authors_urls]
        authors_data = await asyncio.gather(*author_tasks)
        authors = [author for author in authors_data if author]

    save_to_json("data_to_database/quotes.json", quotes)
    save_to_json("data_to_database/authors.json", authors)
    logging.info("all data successfully scraped and saved to database")


def save_to_json(filename: str, data: list):
    """saving to json file in correct format for uploading to mongoDB"""
    try:
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
    except PathError:
        raise PathError(f"Could not create a file in path: {filename}")


async def main():
    await scrape_quotes_and_authors()
