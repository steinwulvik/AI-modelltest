# AI-modelltest – Morild Bank

Fire språkmodeller fikk samme oppgave: å klassifisere 39 IT-hendelser i den fiktive Morild Bank som **lav**, **middels** eller **alvorlig**. Alle fikk samme instruksjon og de samme hendelsene, og svarene ble målt på samme måte. Det eneste som ble byttet, var modellen. Alle dataene er syntetiske.

**Rapport:** [Valg av språkmodell for hendelsesklassifisering – Morild Bank](Rapport.md)

## Resultat (november 2026)

| Modell | Treff | Sek. per svar | Kostnad (39 svar) | Hvor dataene behandles |
|---|---|---|---|---|
| Claude Haiku 5.5 | 39/39 (100 %) | 1,0 | $0,005 | Hos Anthropic |
| GPT-6 Luna | 38/39 (97 %) | 1,3 | $0,003 | Hos OpenAI |
| Gemini 3.5 Flash-Lite | 35/39 (90 %) | 3,4 | $0,007 | Hos Google |
| Mistral 7B, lokalt via Ollama | 34/39 (87 %) | 8,4 | 0 | På egen PC |

De to beste skymodellene traff 97–100 %. Den lokale modellen holdt alle dataene på egen maskin, men undervurderte de to mest alvorlige hendelsene. Forskjeller på 1–2 treff kan skyldes tilfeldigheter, slik resultatene fra tre kjøringer viser.

## Innhold

| Fil | Hva den gjør |
|---|---|
| `testsett.json` | 39 hendelser med fasit, 13 i hver klasse. |
| `modeller.json` | Modellene som testes. Her settes modellnavn og innstillinger per modell. |
| `sammenlign.py` | Kjører testen og skriver resultatene. Reglene for klassifisering står øverst i fila. |
| `sjekk_modeller.py` | Viser hvilke modeller API-nøklene har tilgang til. |
| `resultater/` | `sammendrag.md` (tabell og feilanalyse) og `detaljer.csv` (ett svar per linje). |
| `env-eksempel.txt` | Mal for API-nøklene. |

## Kom i gang (Windows)

1. Installer Python 3.10 eller nyere fra python.org.
2. Dobbeltklikk på `oppsett.bat`. Den lager et virtuelt miljø, installerer DSPy 3.4.1 og prøvekjører med en falsk modell. Loggen havner i `oppsett-logg.txt`.
3. Kopier `env-eksempel.txt` til `.env`, og fyll inn API-nøklene du har. **`.env` skal aldri lastes opp.** Den er stengt ute i `.gitignore`.
4. For lokal modell: installer Ollama og kjør `ollama pull mistral`.
5. Dobbeltklikk på `kjor.bat`. Modeller som mangler nøkkel, blir hoppet over.

## Tekniske merknader

- Med DSPy 3.4.1 må Ollama-adressen være `http://localhost:11434/v1`.
- Claude Haiku 5.5 og GPT-6 Luna godtar ikke temperatur 0. De har `"temperatur": null` i `modeller.json` og kjører med leverandørens standardinnstilling.
- Svarene tolkes ved at det første av ordene lav, middels eller alvorlig hentes ut. Lokale modeller legger ofte til formatrester eller forklaringer.
