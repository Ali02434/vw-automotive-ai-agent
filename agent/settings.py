import yaml
from pathlib import Path


def loadconfig():
    with open(Path(__file__).parent.parent/"config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config