from agent.settings import loadconfig
from agent.shops import find_products
from agent.llm import extract_info


if __name__ == "__main__":
    config = loadconfig()
    for shop in config["shops"]:
        for product in find_products(shop, limit=min(3, config["limit"])):
            result = extract_info(product["text"], config)
            print(product["url"], result)
