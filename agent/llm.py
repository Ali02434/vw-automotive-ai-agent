#TODO für LLM-Extraktion
import requests
import json

#beispielseite solange wie issue 3 noch nicht umgesetzt ist.
example_text = "Sportauspuff Edelstahl für VW Golf 8 GTI. Klappenauspuff mit 2x 100 mm Endrohren, satter Sound, TÜV-geprüft mit ABE. Lieferzeit 3-5 Werktage. Preis: 649,90 € inkl. MwSt."




def extract_info(text_fahrzeug, config):
    prompt =  f"""
    Du bist ein Experte für die Extraktion von Fahrzeugmerkmalen von Produkttexten aus Online-Shops. Untersuche den folgenden Text und extrahiere die relevanten Informationen zu den Fahrzeugmerkmalen. Gib die Ergebnisse in einem JSON Format  zurück, das die folgenden Bereiche Name, Beschreibung, Preis deckt. Verwende die JSON Schlüssel name, beschreibung, preis Wenn du nichts passendes findest, trag null ein. Gib den Preis als Zahl mit Punkt  ohne Währung an.
    Verwende Nur die Informationen, die im Text enthalten sind. Gib keine zusätzlichen Informationen oder Annahmen an. Achte darauf, dass das JSON-Format korrekt ist und keine zusätzlichen Zeichen oder Kommentare enthält.
    ---
    Text: {text_fahrzeug} \n
    ---
    """

    schema = {"type": "object", "properties": {"name": {"type": "string"}, "beschreibung": {"type": "string"}, "preis": {"type": "number"}}}


    r = requests.post(
        config["llm"]["url"] + "/api/generate",json={
            "model": config["llm"]["model"],
            "prompt": prompt,
            "stream": False,
            "think": False,
            "format": schema
        })

    return json.loads(r.json()["response"])