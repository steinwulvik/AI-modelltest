# Valg av språkmodell for hendelsesklassifisering – Morild Bank

7. november 2026 · Stein Wulvik

## Oppsummering

Claude Haiku 5.5 og GPT-6 Luna klassifiserte 97–100 % av 39 IT-hendelser riktig, på rundt ett sekund per svar og for under en cent totalt. Mistral 7B, kjørt på egen PC med Ollama, traff 87 % og holdt alle data på egen maskin, men undervurderte de to mest alvorlige hendelsene. For en bank er valget derfor en avveining mellom treffsikkerhet og hvor dataene behandles, ikke mellom leverandører: det samme testoppsettet ble brukt på alle fire modellene.

## Hvorfor teste

Målet var å finne ut, med egne tall, hvilken språkmodell som passer til en konkret bankoppgave, i stedet for å stole på leverandørenes egne påstander.

- **Riktig valg for oppgaven:** modellene er ulikt sterke på ulike oppgaver. Bare en test på bankens egne typer saker viser hvor treffsikre de er der det betyr noe.
- **Hele bildet, ikke bare treffprosent:** en bank må veie treffsikkerhet mot hastighet, kostnad og hvor dataene behandles. Testen måler alle fire.
- **Ikke låst til én leverandør:** ved å kjøre samme test på modeller fra fire leverandører vises det at løsningen kan bytte modell når pris, kvalitet eller krav endrer seg.
- **Grunnlag for kontroll:** en fast test med kjente svar kan kjøres på nytt hver gang en modell oppdateres eller byttes, slik at banken kan dokumentere at løsningen fortsatt virker som forventet.

## Slik ble det testet

- **Oppgave:** klassifisere IT-hendelser i den fiktive Morild Bank som lav, middels eller alvorlig, ut fra faste regler for hvor lenge hver tjeneste kan være nede.
- **Testhendelser:** 39 oppdiktede hendelser der det riktige svaret var bestemt på forhånd: 13 lave, 13 middels og 13 alvorlige.
- **Likt for alle:** samme instruksjon, samme hendelser og samme måling. Bare modellen byttes, og det krever bare én linje i en innstillingsfil (konfigurasjonsfil).
- **Verktøy:** et lite Python-program bygget med rammeverket DSPy 3.4.1, som stiller det samme spørsmålet (prompten) til hver modell og leser svarene på samme måte. Modellen på egen PC kjørte med gratisprogrammet Ollama.
- **Modeller:** den minste aktuelle modellen fra hver leverandør, valgt fra leverandørenes egne oversikter og sjekket mot det kontoen faktisk har tilgang til gjennom leverandørenes API (tilkoblingen programmer bruker).
- **Kjøringer:** tre kjøringer for å se hvor stabile resultatene er.

## Resultater

Tallene er fra siste kjøring. Kostnaden gjelder alle 39 hendelsene, slik leverandøren oppga den.

| Modell | Treff (siste) | Treff i 3 kjøringer | Sekunder per svar | Kostnad (dollar) | Hvor dataene behandles |
| --- | --- | --- | --- | --- | --- |
| Claude Haiku 5.5 (Anthropic) | 39/39 (100 %) | 38 · 38 · 39 | 1,0 | 0,0049 | Hos Anthropic |
| GPT-6 Luna (OpenAI) | 38/39 (97 %) | – · – · 38 | 1,3 | 0,0027 | Hos OpenAI |
| Gemini 3.5 Flash-Lite (Google) | 35/39 (90 %) | 33 · 33 · 35 | 3,4 | 0,0069 | Hos Google |
| Mistral 7B (på egen PC, via Ollama) | 34/39 (87 %) | 34 · 34 · 34 | 8,4 | 0 | På egen PC |

GPT ble bare målt i siste kjøring. Gemini svarte på 38 av 39 i hver kjøring. Gratisversjonen har en grense (kvote) for hvor mange spørsmål man kan sende per minutt, og den stoppet ett av dem. Forskjeller på 1–2 treff ligger innenfor variasjonen mellom kjøringer.

## Hva modellene bommet på

Retningen på feilene betyr mer enn antallet: å undervurdere en alvorlig hendelse er dyrere for en bank enn å overvurdere en middels.

| Modell | Feilmønster | Eksempel |
| --- | --- | --- |
| Claude, GPT | Overvurderer i ett tilfelle (middels → alvorlig) | Manuell kredittvurdering av alle lånesøknader i én dag. Det riktige svaret kan diskuteres, siden alle lånekunder er berørt. |
| Gemini | Undervurderer middels hendelser (middels → lav) | Lånesøknad nede i tre timer, varsler nede i seks timer |
| Mistral lokal | Undervurderer alvorlige hendelser (alvorlig → middels) | Kontoutskrifter med navn og kontonummer sendt til feil mottakere; innenlands betaling nede i tre timer, lenger enn banken tåler |

Mistral sin bom på datalekkasjen er den mest alvorlige feilen i testen: personopplysninger på avveie skal meldes til Datatilsynet.

## Anbefaling for en bank

Velg modell etter hvor sensitive dataene er, og bygg løsningen slik at modellen kan byttes.

1. **Hendelsesbeskrivelser uten personopplysninger:** bruk en av de store modellene som kjøres hos leverandøren over internett, som Claude eller GPT. Den treffer 97–100 %, svarer på et sekund og koster under en cent per 39 hendelser. Krev en avtale om hvordan leverandøren behandler dataene, og helst at de behandles i Europa.
2. **Sensitive data som ikke kan forlate banken:** bruk en lokal modell, men la et menneske kontrollere alt modellen ikke setter som alvorlig. Lokal Mistral bommet nettopp på de alvorlige.
3. **Unngå innlåsing:** ha de samme instruksjonene og de samme testhendelsene, og kjør testen på nytt når leverandørene lanserer nye modeller. I denne testen var det én linje i en innstillingsfil som skilte modellene.
4. **Mål det som koster mest:** følg andelen alvorlige hendelser som blir undervurdert, ikke bare total treffprosent.

## Forbehold og lærdommer

- **Få testhendelser:** bare 39 oppdiktede hendelser. Ett riktig svar utgjør 2,6 prosentpoeng, så forskjeller på ett eller to svar kan skyldes tilfeldigheter.
- **Ikke helt like innstillinger:** Modellene kan stilles inn til å svare så likt som mulig hver gang. Claude og GPT tillater ikke denne innstillingen og kjørte med vanlig innstilling, mens Gemini og Mistral kjørte med den. Likevel varierte Gemini mer enn Claude mellom kjøringene.
- **Leverandørene oppfører seg ulikt:** de godtar ulike innstillinger og har ulike grenser for hvor mye de kan brukes. Å bytte modell krever derfor alltid en ny testkjøring, ikke bare et nytt modellnavn.
- **Les svarene, ikke bare tallet:** første kjøring ga Mistral 0 av 39, fordi modellen satte et ekstra tegn foran svarordet. Etter at programmet ble rettet til å lese svaret riktig, var resultatet 34 av 39.
- **Kostnad:** tallene er hva leverandørene oppga for testkjøringen, ikke et anslag på hva daglig bruk vil koste.
