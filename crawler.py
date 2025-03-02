import bs4
import os
import asyncio
import aiohttp
from pathlib import Path
from urllib.parse import urlparse
from config import MAX_DEPTH, START_URLS, OUTPUT_PATH

MY_URL = "https://skillbox.ru/"
BASE_DOMAIN = urlparse(MY_URL).netloc

OUT_PATH = Path(__name__).parent / os.path.dirname(OUTPUT_PATH)
OUT_PATH.mkdir(exist_ok=True, parents=True)
OUT_PATH = OUT_PATH.absolute()


async def get_content(url, client):
    """Делаем запрос оп ссылке и ищем другие ссылки на странице"""
    try:
        async with client.get(url) as response:
            print(f"{url}, status code: {response.status}")
            result = await response.read()
            soup = bs4.BeautifulSoup(result, "html.parser")
            res = await asyncio.to_thread(find_links, soup)
            return res

    except (aiohttp.ClientConnectionError, aiohttp.ClientError) as exp:
        print(exp)
        return []


def write_links(links):
    with open(OUTPUT_PATH, "w") as f:
        for link in links:
            f.write(link + '\n')


def is_external_link(url):
    """Проверяем является ли текущая ссылка внешней"""
    parsed_url = urlparse(url)
    if not parsed_url.netloc:
        return False
    return parsed_url.netloc != BASE_DOMAIN


def find_links(soup: bs4.BeautifulSoup):
    """Ищем все ссылки на странице"""
    result = []
    for link in soup.find_all("a"):
        res = link.get('href')
        if res is not None and is_external_link(res):
            result.append(res)
    return result


async def get_content_recursion(url, client, depth=MAX_DEPTH, visited=None):
    """Рекурсивно проходимся по всем страницам"""
    if visited is None:
        visited = set()
    if depth == 0 or url in visited:
        return
    else:
        visited.add(url)
        links = await get_content(url, client)
        if len(links) != 0:
            await asyncio.to_thread(write_links, links)

            rec_tasks = [get_content_recursion(url_i, client, depth - 1, visited) for url_i in links]
            return await asyncio.gather(*rec_tasks)
        else:
            return


async def main(url):
    """Начало обхода для ссылки"""
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(30)) as client:
        await get_content_recursion(url, client)


async def start_crawl():
    """Дожидаемся корутин для всех ссылок"""
    tasks = [main(url) for url in START_URLS]
    await asyncio.gather(*tasks)
