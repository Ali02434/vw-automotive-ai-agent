"""Find product pages in configured shops."""

import json
import re
from collections import deque
from urllib.parse import urljoin, urlsplit, urldefrag

import requests
from bs4 import BeautifulSoup


MODIFICATION = re.compile(
    r"fahrwerk|feder|auspuff|abgas|ansaug|bremse|spoiler|diffusor|"
    r"bodykit|downpipe|stabilisator|felge|chiptuning", re.I
)


def _is_product_page(soup):
    for script in soup.select('script[type="application/ld+json"]'):
        try:
            pending = [json.loads(script.string or "")]
        except ValueError:
            continue
        while pending:
            item = pending.pop()
            if isinstance(item, dict):
                types = item.get("@type", [])
                if isinstance(types, str):
                    types = [types]
                if isinstance(types, list) and any(
                    isinstance(t, str) and t.rsplit("/", 1)[-1] == "Product" for t in types
                ):
                    return True
                pending.extend(item.values())
            elif isinstance(item, list):
                pending.extend(item)

    price = soup.select_one('[itemprop="price"], [class*="price"], [id*="price"]')
    price = price or soup.find(string=re.compile(r"(?:€|\$|£)\s*\d|\d[\d.,]*\s*(?:€|\$|£|EUR|USD)"))
    cart = soup.select_one('form.cart, [name="add-to-cart"], .single_add_to_cart_button')
    if not cart:
        cart = any(re.search(r"in den warenkorb|add to cart|buy now|jetzt kaufen",
                             button.get_text(" ", strip=True) + " " + button.get("value", ""), re.I)
                   for button in soup.select('button, input[type="submit"]'))
    return bool(soup.find("h1") and price and cart)


def find_products(shop_url, limit=3, max_pages=20):
    """Return product URLs and visible text found by following internal links."""
    host = urlsplit(shop_url).netloc
    queue, seen, products = deque([shop_url]), set(), []

    while queue and len(seen) < max_pages and len(products) < limit:
        url = queue.popleft()
        if url in seen:
            continue
        seen.add(url)
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as exc:
            print(f"Abruf fehlgeschlagen: {url}: {exc}")
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.find("h1")
        if _is_product_page(soup):
            if title and MODIFICATION.search(title.get_text()):
                for tag in soup.select("script, style, nav, header, footer, noscript"):
                    tag.decompose()
                products.append({"url": url, "text": soup.get_text(" ", strip=True)})
            continue

        links = []
        for link in soup.select("a[href]"):
            target = urldefrag(urljoin(url, link["href"])).url
            parts = urlsplit(target)
            if parts.scheme in ("http", "https") and parts.netloc == host and target not in seen:
                links.append(target)
        links.sort(key=lambda link: ("vw" not in urlsplit(link).path,
                                     "/produkt/" not in urlsplit(link).path))
        queue.extendleft(reversed(links))

    return products
