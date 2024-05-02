import requests
import random
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from urllib.parse import urlparse, urljoin
import csv
import time


def is_internal_url(url, base_domain):
    parsed_url = urlparse(url)
    return not parsed_url.netloc or parsed_url.netloc == base_domain

def get_user_agent():
    ua = UserAgent()
    return ua.random

def get_internal_links(url, base_domain):
    try:
        response = requests.get(url, headers={"User-Agent": get_user_agent()})
        time.sleep(random.randint(1, 5))
        soup = BeautifulSoup(response.content, "html.parser")
    except Exception as e:
        print(f"Error fetching URL {url}: {e}")
        return set()

    internal_links = set()

    for link in soup.find_all("a"):
        href = link.get("href")
        if href:
            full_url = urljoin(url, href)
            if is_internal_url(href, base_domain) and not full_url.startswith("mailto"):
                internal_links.add(full_url)

    return internal_links


def recursive_scrape(url, base_domain, visited=set()):
    if url not in visited and url is not None:
        print(url)
        visited.add(url)
        internal_links = get_internal_links(url, base_domain)
        for link in internal_links:
            visited.update(recursive_scrape(link, base_domain, visited))

    return visited


def main():
    start_url = "https://protein.monster"
    base_domain = urlparse(start_url).netloc

    visited_links = recursive_scrape(start_url, base_domain)

    with open("internal_links.csv", "w", newline="") as csvfile:
        csv_writer = csv.writer(csvfile)
        for link in sorted(visited_links):
            csv_writer.writerow([link])


if __name__ == "__main__":
    main()
