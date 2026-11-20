from agent.settings import loadconfig
from agent.llm import extract_info, example_text

if __name__ == "__main__":
    config = loadconfig()
    print("Suchlauf gestartet \n")
    print(config.get("limit"))
    print(config.get("llm").get("model"))

    ergebnis = extract_info(example_text, config)
    print(ergebnis)