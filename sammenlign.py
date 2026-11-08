"""
Sammenligner språkmodeller på samme oppgave: klassifisere IT-hendelser i den fiktive Morild Bank
som lav, middels eller alvorlig. Alle modeller får samme instruksjon, samme testsett og samme måling.

Bruk:
    python sammenlign.py                  # alle aktive modeller i modeller.json
    python sammenlign.py --modeller GPT Claude
    python sammenlign.py --begrunnelse    # modellen resonnerer før den svarer (ChainOfThought)
    python sammenlign.py --test           # prøvekjøring uten API-nøkler (falsk modell)

Resultatene skrives til mappen resultater/: sammendrag.md og detaljer.csv.
Alle data er syntetiske.
"""

import argparse
import re
import csv
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import dspy

MAPPE = Path(__file__).resolve().parent
KLASSER = ["lav", "middels", "alvorlig"]


class Alvorlighet(dspy.Signature):
    """Du er beredskapsleder i Morild Bank. Klassifiser IT-hendelsen etter disse reglene:

    alvorlig: En kritisk tjeneste eller en hel kundekanal (mobilbank, nettbank) er nede for mange kunder,
    nedetiden er lengre enn tjenestens gjenopprettingsmål, eller kundedata kan være lekket eller feil.
    middels: Kundene merker feil, forsinkelse eller redusert funksjon, men ingen kritisk tjeneste er nede,
    og nedetiden er innenfor gjenopprettingsmålet.
    lav: Ingen eller svært liten påvirkning for kundene, for eksempel interne systemer, testmiljø,
    planlagt og varslet vedlikehold eller korte forsinkelser.

    Kritiske tjenester og gjenopprettingsmål: Kontooversikt og saldo 4 timer, Innenlands betaling 2 timer,
    Kortbetaling 1 time, Innlogging og identifisering 1 time.
    Andre tjenester: Lånesøknad 24 timer, Kundehenvendelser 8 timer, Varsler og meldinger 12 timer,
    Transaksjonsovervåking (AML) 24 timer.
    """

    hendelse: str = dspy.InputField(desc="Beskrivelse av hendelsen")
    alvorlighet: str = dspy.OutputField(desc="Nøyaktig ett ord: lav, middels eller alvorlig")


def normaliser(svar: str) -> str:
    """Gjør om svaret til en av klassene, så små forskjeller i skrivemåte ikke teller som feil."""
    s = (svar or "").strip().lower()
    # Noen modeller (f.eks. lokal Mistral) tar med rester av formatet, som "]", eller legger til en
    # forklaring etter svaret. Vi godtar det første klasseordet som står alene i svaret.
    treff = re.search(r"\b(" + "|".join(KLASSER) + r")\b", s)
    return treff.group(1) if treff else s


def kort_feil(e: Exception) -> str:
    """Kort, lesbar feiltekst til resultatfilene i stedet for leverandørens fulle feilmelding."""
    tekst = " ".join(str(e).split()).lower()
    if "quota" in tekst or "rate limit" in tekst or "429" in tekst:
        return "Kvotegrense nådd"
    if "timeout" in tekst or "timed out" in tekst:
        return "Tidsavbrudd"
    return "Feil i kallet"


def riktig(eksempel, svar, trace=None) -> bool:
    return normaliser(svar.alvorlighet) == eksempel.alvorlighet


def last_env():
    """Leser API-nøkler fra filen .env hvis den finnes (linjer på formen NAVN=verdi)."""
    fil = MAPPE / ".env"
    if not fil.exists():
        return
    for linje in fil.read_text(encoding="utf-8").splitlines():
        linje = linje.strip()
        if linje and not linje.startswith("#") and "=" in linje:
            navn, verdi = linje.split("=", 1)
            os.environ.setdefault(navn.strip(), verdi.strip().strip('"'))


def last_testsett():
    data = json.loads((MAPPE / "testsett.json").read_text(encoding="utf-8"))
    return [dspy.Example(hendelse=x["hendelse"], alvorlighet=x["alvorlighet"]).with_inputs("hendelse") for x in data]


def nar_tjener(url: str) -> bool:
    """Sjekker raskt at en lokal modelltjener (for eksempel Ollama) svarer, så kjøringen ikke henger."""
    import socket
    from urllib.parse import urlparse

    u = urlparse(url)
    try:
        with socket.create_connection((u.hostname, u.port or 80), timeout=2):
            return True
    except OSError:
        return False


def lag_modell(m: dict):
    # num_retries: prøver på nytt med økende ventetid ved midlertidige feil, f.eks. kvote per minutt.
    kwargs = {"max_tokens": 1000, "cache": False, "num_retries": 5}
    # Temperatur 0 for alle, unntatt modeller som ikke tar imot temperatur ("temperatur": null i modeller.json).
    temperatur = m.get("temperatur", 0.0)
    if temperatur is not None:
        kwargs["temperature"] = temperatur
    if m.get("api_base"):
        kwargs["api_base"] = m["api_base"]
    return dspy.LM(m["modell"], **kwargs)


def falsk_modell(testsett):
    """Falsk modell for --test: svarer riktig på to av tre, så hele løpet kan prøves uten nøkler."""
    from dspy.utils import DummyLM

    svar = [
        {"reasoning": "Prøvesvar.", "alvorlighet": x.alvorlighet if i % 3 else "middels"} for i, x in enumerate(testsett)
    ]
    return DummyLM(svar)


def kjor(navn, lm, program, testsett):
    """Kjører hele testsettet mot én modell og måler treff, tid, tokens og kostnad."""
    detaljer = []
    start = time.perf_counter()
    with dspy.context(lm=lm):
        for x in testsett:
            t0 = time.perf_counter()
            try:
                svar = normaliser(program(hendelse=x.hendelse).alvorlighet)
                feil = ""
            except Exception as e:  # en feil i ett kall skal ikke stoppe hele kjøringen
                svar, feil = "", kort_feil(e)
            detaljer.append(
                {
                    "modell": navn,
                    "hendelse": x.hendelse,
                    "fasit": x.alvorlighet,
                    "svar": svar,
                    "riktig": svar == x.alvorlighet,
                    "sekunder": round(time.perf_counter() - t0, 2),
                    "feil": feil,
                }
            )
    total = time.perf_counter() - start

    historikk = getattr(lm, "history", []) or []
    inn = sum((h.get("usage") or {}).get("prompt_tokens", 0) or 0 for h in historikk)
    ut = sum((h.get("usage") or {}).get("completion_tokens", 0) or 0 for h in historikk)
    kostnader = [h.get("cost") for h in historikk if h.get("cost") is not None]

    n = len(detaljer)
    treff = sum(d["riktig"] for d in detaljer)
    return detaljer, {
        "modell": navn,
        "treff": f"{treff}/{n}",
        "treffprosent": round(100 * treff / n, 1) if n else 0,
        "sek_per_kall": round(total / n, 2) if n else 0,
        "tokens_inn": inn,
        "tokens_ut": ut,
        "kostnad_usd": round(sum(kostnader), 4) if kostnader else None,
        "feil_i_kall": sum(1 for d in detaljer if d["feil"]),
    }


def forvirring(detaljer):
    """Antall per (fasit, svar), så man ser hvilke klasser modellen blander."""
    tabell = {f: {s: 0 for s in KLASSER + ["annet"]} for f in KLASSER}
    for d in detaljer:
        tabell[d["fasit"]][d["svar"] if d["svar"] in KLASSER else "annet"] += 1
    return tabell


def skriv_resultater(sammendrag, alle_detaljer, begrunnelse):
    ut = MAPPE / "resultater"
    ut.mkdir(exist_ok=True)

    with open(ut / "detaljer.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(alle_detaljer[0].keys()), delimiter=";")
        w.writeheader()
        w.writerows(alle_detaljer)

    linjer = [
        "# Sammenligning av modeller – Morild Bank (syntetiske data)",
        "",
        f"Kjørt {datetime.now():%d.%m.%Y %H:%M}. Oppgave: klassifisere {len(alle_detaljer) // max(1, len(sammendrag))} hendelser "
        f"som lav, middels eller alvorlig. Variant: {'med begrunnelse (ChainOfThought)' if begrunnelse else 'direkte svar (Predict)'}. Temperatur 0.",
        "",
        "| Modell | Treff | Treff % | Sek. per kall | Tokens inn | Tokens ut | Kostnad (USD) | Feil i kall |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for s in sorted(sammendrag, key=lambda s: -s["treffprosent"]):
        kost = "–" if s["kostnad_usd"] is None else f"{s['kostnad_usd']:.4f}"
        linjer.append(
            f"| {s['modell']} | {s['treff']} | {s['treffprosent']} | {s['sek_per_kall']} | {s['tokens_inn']} | "
            f"{s['tokens_ut']} | {kost} | {s['feil_i_kall']} |"
        )

    linjer += ["", "## Hva modellene bommet på", ""]
    for s in sammendrag:
        bom = [d for d in alle_detaljer if d["modell"] == s["modell"] and not d["riktig"]]
        linjer.append(f"### {s['modell']} ({len(bom)} feil)")
        tab = forvirring([d for d in alle_detaljer if d["modell"] == s["modell"]])
        linjer.append("")
        linjer.append("| Fasit \\ svar | " + " | ".join(KLASSER + ["annet"]) + " |")
        linjer.append("|---|" + "---|" * (len(KLASSER) + 1))
        for fasit, rad in tab.items():
            linjer.append(f"| {fasit} | " + " | ".join(str(rad[k]) for k in KLASSER + ["annet"]) + " |")
        linjer.append("")
        for d in bom:
            linjer.append(f"- Fasit **{d['fasit']}**, svar **{d['svar'] or 'ingen svar (' + (d['feil'] or 'tomt').lower() + ')'}**: {d['hendelse']}")
        linjer.append("")

    (ut / "sammendrag.md").write_text("\n".join(linjer), encoding="utf-8")
    return ut


def main():
    p = argparse.ArgumentParser(description="Sammenlign språkmodeller på Morild Banks testsett.")
    p.add_argument("--modeller", nargs="*", help="Navn fra modeller.json (standard: alle aktive)")
    p.add_argument("--begrunnelse", action="store_true", help="La modellen resonnere før den svarer")
    p.add_argument("--test", action="store_true", help="Prøvekjøring med falsk modell, uten API-nøkler")
    a = p.parse_args()

    last_env()
    testsett = last_testsett()
    program = dspy.ChainOfThought(Alvorlighet) if a.begrunnelse else dspy.Predict(Alvorlighet)

    if a.test:
        valgte = [("Falsk modell (test)", falsk_modell(testsett))]
    else:
        oppsett = json.loads((MAPPE / "modeller.json").read_text(encoding="utf-8"))["modeller"]
        valgte = []
        for m in oppsett:
            if a.modeller and m["navn"] not in a.modeller:
                continue
            if not a.modeller and not m.get("aktiv", True):
                continue
            if "FYLL-INN" in m["modell"]:
                print(f"Hopper over {m['navn']}: fyll inn modellnavn i modeller.json.")
                continue
            if m.get("nokkel") and not os.environ.get(m["nokkel"]):
                print(f"Hopper over {m['navn']}: mangler {m['nokkel']} (se README).")
                continue
            if m.get("api_base") and not nar_tjener(m["api_base"]):
                print(f"Hopper over {m['navn']}: får ikke kontakt med {m['api_base']} (er Ollama startet?).")
                continue
            valgte.append((m["navn"], lag_modell(m)))
        if not valgte:
            sys.exit("Ingen modeller å kjøre. Fyll inn modeller.json og API-nøkler, eller prøv --test.")

    sammendrag, alle = [], []
    for navn, lm in valgte:
        print(f"Kjører {navn} på {len(testsett)} hendelser ...")
        detaljer, s = kjor(navn, lm, program, testsett)
        alle += detaljer
        sammendrag.append(s)
        print(f"  {s['treff']} riktige ({s['treffprosent']} %), {s['sek_per_kall']} sek per kall")

    ut = skriv_resultater(sammendrag, alle, a.begrunnelse)
    print(f"\nFerdig. Se {ut / 'sammendrag.md'} og {ut / 'detaljer.csv'}.")


if __name__ == "__main__":
    main()
