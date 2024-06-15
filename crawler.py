import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
import storage
import time

USER_AGENT = 'TestWebCrawler/1.0'

def create_robot_parser(url):
    """ Create a robot parser for the given URL """
    parsed_url = urlparse(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}/"
    robots_txt_url = urljoin(base_url, 'robots.txt')
    parser = RobotFileParser()
    parser.set_url(robots_txt_url)
    parser.read()
    return parser

def can_fetch(url, parser):
    """ Check if the url can be fetched according to robots.txt """
    return parser.can_fetch(USER_AGENT, url)

def get_links(url, parser, base_url):
    """ Fetches all unique links from a given URL respecting robots.txt. """
    if not can_fetch(url, parser):
        print(f"Fetching disallowed by robots.txt: {url}")
        return set()
    headers = {'User-Agent': USER_AGENT}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    links = set()
    for link in soup.find_all('a', href=True):
        full_url = urljoin(base_url, link['href'])
        if full_url.startswith(base_url) and full_url != url:
            links.add(full_url)
    return links

def get_content(url, parser):
    """ Fetches content of a given URL if allowed by robots.txt. """
    if not can_fetch(url, parser):
        print(f"Fetching disallowed by robots.txt: {url}")
        return ""
    headers = {'User-Agent': USER_AGENT}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    text = ' '.join(p.text for p in soup.find_all('p'))
    return text

def crawl_website(start_url, max_links=50, delay=1.0):
    """ Crawls a website starting from `start_url` until it collects `max_links` unique links and stores their contents, respecting robots.txt and rate limiting. """
    parser = create_robot_parser(start_url)
    conn = storage.create_connection('website.db')
    storage.create_table(conn)

    visited = set()
    to_visit = {start_url}
    base_url = f"{urlparse(start_url).scheme}://{urlparse(start_url).netloc}"

    while to_visit and len(visited) < max_links:
        current_url = to_visit.pop()
        if current_url not in visited:
            visited.add(current_url)
            print(f"Visiting: {current_url}")
            content = get_content(current_url, parser)
            if content:
                storage.save_page(conn, current_url, content)
            links = get_links(current_url, parser, base_url)
            to_visit.update(links - visited)
            if len(visited) >= max_links:
                break
            time.sleep(delay)
    conn.close()

if __name__ == "__main__":
    start_page = "https://en.wikipedia.org/wiki/Main_Page"
    crawl_website(start_page)