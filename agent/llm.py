import requests
import json


def extract_info(text, config):
    # NEU: lange Shopseiten kürzen, sonst schneidet Ollama den Text ab
    text = text[:4000]

    # NEU: bereinigter Prompt, Regeln vor dem Text
    prompt = f"""Du bist ein Experte für die Extraktion von Produktdaten aus Texten von Online-Shops für Fahrzeugmodifikationen und Zubehör.
Extrahiere aus dem folgenden Text die Informationen zum Produkt und gib sie als JSON mit den Schlüsseln name, beschreibung und preis zurück.

Regeln:
- Verwende nur Informationen, die im Text stehen. Erfinde nichts.
- Wenn eine Information fehlt, trage null ein.
- Gib den Preis als Zahl mit Punkt und ohne Währung an, z. B. 289.90.

---
{text}
---"""

    # NEU: null erlaubt und alle Felder Pflicht
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": ["string", "null"]},
            "beschreibung": {"type": ["string", "null"]},
            "preis": {"type": ["number", "null"]}
        },
        "required": ["name", "beschreibung", "preis"]
    }

    r = requests.post(
        config["llm"]["url"] + "/api/generate",
        json={
            "model": config["llm"]["model"],
            "prompt": prompt,
            "stream": False,
            "think": False,
            "format": schema
        }
    )

    return json.loads(r.json()["response"])