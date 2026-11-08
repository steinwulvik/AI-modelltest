# Sammenligning av modeller – Morild Bank (syntetiske data)

Kjørt 07.11.2026 18:59. Oppgave: klassifisere 39 hendelser som lav, middels eller alvorlig. Variant: direkte svar (Predict). Temperatur 0.

| Modell | Treff | Treff % | Sek. per kall | Tokens inn | Tokens ut | Kostnad (USD) | Feil i kall |
|---|---|---|---|---|---|---|---|
| Claude | 39/39 | 100.0 | 1.03 | 29429 | 3935 | 0.0049 | 0 |
| GPT | 38/39 | 97.4 | 1.25 | 17109 | 1941 | 0.0027 | 0 |
| Gemini | 35/39 | 89.7 | 3.39 | 18136 | 596 | 0.0069 | 1 |
| Mistral (lokal) | 34/39 | 87.2 | 8.43 | 22389 | 894 | 0.0000 | 0 |

## Hva modellene bommet på

### GPT (1 feil)

| Fasit \ svar | lav | middels | alvorlig | annet |
|---|---|---|---|---|
| lav | 13 | 0 | 0 | 0 |
| middels | 0 | 12 | 1 | 0 |
| alvorlig | 0 | 0 | 13 | 0 |

- Fasit **middels**, svar **alvorlig**: Kredittvurderingen gir manuell behandling for alle lånesøknader i dag, så kundene får svar etter to dager i stedet for med en gang.

### Claude (0 feil)

| Fasit \ svar | lav | middels | alvorlig | annet |
|---|---|---|---|---|
| lav | 13 | 0 | 0 | 0 |
| middels | 0 | 13 | 0 | 0 |
| alvorlig | 0 | 0 | 13 | 0 |


### Gemini (4 feil)

| Fasit \ svar | lav | middels | alvorlig | annet |
|---|---|---|---|---|
| lav | 13 | 0 | 0 | 0 |
| middels | 3 | 9 | 0 | 1 |
| alvorlig | 0 | 0 | 13 | 0 |

- Fasit **middels**, svar **lav**: Lånesøknad i nettbanken har vært nede i tre timer. Kundene kan fortsatt ringe kundesenteret for å søke.
- Fasit **middels**, svar **[gemini/gemini-3.5-flash-lite] You exceeded your current quota, please check your plan and billing details. For more information on this error, head to: https://aistudio.google.com/docs/rate-limits. T**: Kredittvurderingen gir manuell behandling for alle lånesøknader i dag, så kundene får svar etter to dager i stedet for med en gang.
- Fasit **middels**, svar **lav**: Saksflyt AS har redusert kapasitet, og ventetiden i kundesenteret er 25 minutter i stedet for 5.
- Fasit **middels**, svar **lav**: Varsler og meldinger er nede i seks timer. Kundene får ikke beskjed om innkommende betalinger, men alt annet virker.

### Mistral (lokal) (5 feil)

| Fasit \ svar | lav | middels | alvorlig | annet |
|---|---|---|---|---|
| lav | 12 | 1 | 0 | 0 |
| middels | 2 | 11 | 0 | 0 |
| alvorlig | 0 | 2 | 11 | 0 |

- Fasit **alvorlig**, svar **middels**: Integrasjonsplattformen (API) stoppet etter en oppgradering. Innenlands betaling har ikke virket på tre timer.
- Fasit **alvorlig**, svar **middels**: En feilkonfigurert eksport har sendt kontoutskrifter med navn og kontonummer til feil mottakere.
- Fasit **middels**, svar **lav**: Lånesøknad i nettbanken har vært nede i tre timer. Kundene kan fortsatt ringe kundesenteret for å søke.
- Fasit **middels**, svar **lav**: Varsler og meldinger i mobilbanken vises ikke for kunder på eldre telefoner. Betaling og kontooversikt virker.
- Fasit **lav**, svar **middels**: Logglagringen for integrasjonsplattformen er 85 prosent full og må utvides innen en måned.