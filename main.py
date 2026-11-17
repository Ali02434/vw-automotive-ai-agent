from agent.settings import loadconfig

if __name__ == "__main__":
    config = loadconfig()
    print("Suchlauf gestartet \n")
    print(config.get("limit"))
    print(config.get("llm").get("model"))