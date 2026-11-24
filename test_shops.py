from unittest.mock import Mock, patch

from bs4 import BeautifulSoup

from agent.shops import _is_product_page, find_products


def test_finds_three_internal_products():
    root = "https://shop.example/"
    pages = {
        root: '<h1>Shop</h1><span class="price">ab 200 €</span>'
              '<a href="/vw/golf-7/sportfahrwerk">1</a><a href="/products/federn-2">2</a>'
              '<a href="/weiter">Weiter</a><a href="https://outside.example/produkt/auspuff">Extern</a>',
        root + "weiter": '<a href="/produkt/auspuff-3">3</a>'
                         '<a href="/vw/golf-7/sportfahrwerk">Duplikat</a>',
        root + "vw/golf-7/sportfahrwerk": '<h1>VW Gewindefahrwerk</h1><nav>Menü</nav>'
              '<p>Preis 500 €</p><script type="application/ld+json">'
              '{"@graph":[{"mainEntity":{"@type":["Thing","Product"]}}]}</script>',
        root + "products/federn-2": '<h1>VW Tieferlegungsfedern</h1>'
              '<script>hidden</script><p>Preis 200 €</p>'
              '<button>In den Warenkorb</button>',
        root + "produkt/auspuff-3": '<h1>VW Sportauspuff</h1><p>Preis 700 €</p>'
              '<script type="application/ld+json">{"@type":"Product"}</script>',
    }

    def get(url, timeout):
        response = Mock(text=pages[url])
        response.raise_for_status.return_value = None
        return response

    with patch("agent.shops.requests.get", side_effect=get) as request:
        products = find_products(root)

    assert len(products) == 3
    assert len({p["url"] for p in products}) == 3
    assert all("Preis" in p["text"] for p in products)
    assert all("Menü" not in p["text"] and "hidden" not in p["text"] for p in products)
    assert all(call.args[0] in pages for call in request.call_args_list)


def test_malformed_json_and_category_are_not_products():
    malformed = BeautifulSoup('<h1>VW Fahrwerk</h1><script type="application/ld+json">{broken</script>',
                              "html.parser")
    category = BeautifulSoup('<h1>Fahrwerke</h1><div class="price">ab 200 €</div>'
                             '<a href="/products/fahrwerk">Ansehen</a>', "html.parser")
    malformed_with_fallback = BeautifulSoup(str(malformed) + '<p>249 €</p>'
                                            '<button>Add to cart</button>', "html.parser")
    assert not _is_product_page(malformed)
    assert not _is_product_page(category)
    assert _is_product_page(malformed_with_fallback)
