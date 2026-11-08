"""Spør hver leverandør hvilke modeller nøkkelen din har tilgang til, og skriver navnene til
modeller-tilgjengelige.txt. Sjekker også at modellnavnene i modeller.json finnes.
Nøklene leses fra .env og skrives aldri ut."""
import json
import os
import pathlib

import requests

MAPPE = pathlib.Path(__file__).parent

fil = MAPPE / ".env"
if fil.exists():
    for linje in fil.read_text(encoding="utf-8").splitlines():
        if "=" in linje and not linje.strip().startswith("#"):
            navn, verdi = linje.split("=", 1)
            os.environ.setdefault(navn.strip(), verdi.strip().strip('"'))


def openai(k):
    r = requests.get("https://api.openai.com/v1/models", headers={"Authorization": f"Bearer {k}"}, timeout=30)
    r.raise_for_status()
    return [m["id"] for m in r.json()["data"]]


def anthropic(k):
    r = requests.get(
        "https://api.anthropic.com/v1/models?limit=1000",
        headers={"x-api-key": k, "anthropic-version": "2023-06-01"},
        timeout=30,
    )
    r.raise_for_status()
    return [m["id"] for m in r.json()["data"]]


def gemini(k):
    r = requests.get(
        "https://generativelanguage.googleapis.com/v1beta/models?pageSize=1000",
        headers={"x-goog-api-key": k},
        timeout=30,
    )
    r.raise_for_status()
    return [
        m["name"].removeprefix("models/")
        for m in r.json().get("models", [])
        if "generateContent" in m.get("supportedGenerationMethods", [])
    ]


def mistral(k):
    r = requests.get("https://api.mistral.ai/v1/models", headers={"Authorization": f"Bearer {k}"}, timeout=30)
    r.raise_for_status()
    return [m["id"] for m in r.json()["data"]]


LEVERANDORER = {
    "openai": ("OPENAI_API_KEY", openai),
    "anthropic": ("ANTHROPIC_API_KEY", anthropic),
    "gemini": ("GEMINI_API_KEY", gemini),
    "mistral": ("MISTRAL_API_KEY", mistral),
}

oppsett = json.loads((MAPPE / "modeller.json").read_text(encoding="utf-8"))["modeller"]
ut = []
for prefiks, (nokkel, hent) in LEVERANDORER.items():
    ut.append(f"=== {prefiks} ===")
    k = os.environ.get(nokkel)
    if not k:
        ut.append(f"Ingen {nokkel} i .env")
        continue
    try:
        navn = sorted(set(hent(k)))
    except requests.HTTPError as e:
        ut.append(f"FEIL: HTTP {e.response.status_code}: {e.response.text[:300]}")
        continue
    except Exception as e:
        ut.append(f"FEIL: {type(e).__name__}: {str(e)[:300]}")
        continue
    for m in oppsett:
        if m["modell"].startswith(prefiks + "/"):
            valgt = m["modell"].split("/", 1)[1]
            ut.append(f"Valgt i modeller.json: {valgt} -> {'FINNES' if valgt in navn else 'FINNES IKKE'}")
    ut.append(f"Tilgjengelige ({len(navn)}):")
    ut.extend("  " + n for n in navn)

(MAPPE / "modeller-tilgjengelige.txt").write_text("\n".join(ut) + "\n", encoding="utf-8")
print("Ferdig. Se modeller-tilgjengelige.txt")
