# 402ward — markedsundersøgelse: hvem overvåger x402-endpoints? (november 2026)

*Research-notat, ingen kode. Udarbejdet 2026-11-09.*

## TL;DR

- **Markedet er allerede fyldt** med gratis og billige værktøjer, både til ren oppetid og til at tjekke, om 402-svaret er korrekt. Mindst ti aktører dækker det i dag (se tabellen), og flere er gratis.
- **Den reelle målgruppe er lille.** Coinbase CDP Bazaar har **33.083 x402-ressourcer på 3.246 hosts** (målt 2026-11-09). Kun **246 hosts har ≥10 unikke betalere på 30 dage**. **837 hosts har højst én betaler**, sandsynligvis kun ejeren selv.
- **Betalingsviljen er dokumenteret lav.** En udbyder (Fizzl13/x402-doctor) opsagde en ekstern "route-watch" til **5 USDC/md.** og byggede den samme kontrol gratis i GitHub Actions.
- **Anbefaling: drop 402ward som generel monitor.** Der er kun plads til en *anderledes* vinkel: **betalte end-to-end canary-kald** (faktisk afregning plus validering af det leverede svar) og et pre-flight-tjek på køber-siden. Det skal i så fald prøves med en tidsramme på 4 uger og hårde stop-kriterier (se nederst). Ellers drop.

## 1. Hvor mange x402-endpoints findes der, og hvem ejer dem?

### Primærdata: Coinbase CDP Bazaar discovery-API

Jeg hentede hele kataloget fra `https://api.cdp.coinbase.com/platform/v2/x402/discovery/resources` (offentligt og uden nøgle) den 2026-11-09.

| Mål | Værdi |
|---|---|
| Ressourcer (API `total`) | 33.083 (32.872 unikke URL'er) |
| Unikke hosts | 3.246 |
| Unikke registrerbare domæner | ~1.401 |
| Unikke `payTo`-adresser | 2.535 |
| Andel af listninger hos top-10 `payTo` | **46 %** |
| Største enkeltejer | én `payTo` (halowerk.com) står for 6.326 listninger (19 %) |
| Hostet på `workers.dev`, `onrender.com`, `vercel.app` og `fly.dev` | ~5.900 listninger (hobby- og serverless-hosting) |
| Netværk (accepts-linjer) | Base 37.040 · Solana 12.665 · Polygon 7.683 · Arbitrum 6.009 · XRPL 4.830 · … |
| Schemes | `exact` ~97 %, derefter `upto`, `batch-settlement` og ~15 eksotiske |
| x402-version | v2: 32.875 · v1: 210 |
| Kald pr. ressource, 30 dage | median **2**, p90 9, p99 116 |
| Unikke betalere pr. ressource | 1 betaler: 20.127 (61 %) |
| Hosts med ≥10 / ≥100 betalere (max over ressourcer) | 246 / ~60 |
| Top-100 ressourcers andel af alle kald | **72 %** (af 783k kald i alt) |
| Største hosts målt på kald | agent.pocket.network, blockrun.ai, api.zerion.io, api-xpay.com, stableenrich.dev |

Næsten alle ressourcer har `lastUpdated` i okt.–nov. 2026, og alle har mindst ét kald. Det passer med, at CDP-facilitatoren indekserer et endpoint, når det første gang afregner med Bazaar-udvidelsen slået til. Det betyder også, at kataloget **ikke rydder ud** i døde endpoints af sig selv.

**Begrænsning:** Sessionens netværkspolitik blokerede direkte kald til tredjeparts-hosts. Jeg har derfor *ikke selv* testet, om endpoints svarer korrekt. Tallene for korrekthed nedenfor kommer fra andre.

### Andre tællinger (sekundære kilder)

- **402index**: angiver "tens of thousands of endpoints across hundreds of verified providers". Ifølge en tredjepartsanalyse beskar de indekset mellem 2026-10-26 og 11-02 fra **196.373 til 43.907** endpoints, og efter oprydningen var **2,7 % offline**. Tallet dækker også L402 og MPP.
- **x402jp "x402 Endpoint"**: 17.089 endpoints fra 6 kataloger (2026-09-17).
- **edvyno (x402scan#1318)**: målte 2026-10-28 **727 hosts**. **430** svarede med en live 402, og karaktererne fordelte sig A 116 / B 36 / C 52 / D 160 / **F 360**. De hyppigste fejl var `no_well_known` 208, `no_paid_routes` 129, `no_catalog` 97, `wrong_status` 71 og `unparseable_402` 34.
- **afx (dev.to)**: 20.338 endpoints testet. 87,3 % svarede korrekt med 402, én udbyder ejede 52 % af kataloget, og 161 blev markeret som "agent honeypots".

**Konklusion:** Afhængigt af katalog og hvordan der dedupliceres, findes der omkring 20–45 tusind x402-endpoints. De ejes dog af kun ~1.400 domæner og ~2.500 wallets. Fordelingen er ekstremt skæv: en håndfuld masse-listere (som auto-genererer hundredvis af "data-API"-ruter) og et par dusin udbydere med rigtig trafik. **Kundeemnerne for en monitor er de ~250 hosts med reelle betalere**, ikke de 33.000 endpoints.

## 2. Hvem overvåger i dag?

### 402index (402index.io)

- **Hvad det er:** et protokol-agnostisk katalog over betalte API'er (L402, x402 og MPP), MIT-licenseret, med kode på GitHub (`ryanthegentry/402index`, forket bl.a. til `frynetworks/402index`). Lavet af Ryan Gentry og bidragydere. Kontakt: hello@402index.io.
- **Hvad de måler:** et sundhedstjek af alle listninger med fast interval, som standard **hvert 60. minut** (`HEALTH_CHECK_INTERVAL_MS`). De registrerer status og antal fejl i træk (f.eks. "Consecutive Failures 302"). Selvregistrering *validerer 402-challengen* og finder ud af, om endpointet taler L402 og/eller x402. Verificering sker i to trin: **domæne** (DNS/.well-known-challenge) og **betaling** (for x402: "spec-compliant 402 headers with valid payment requirements"). Jeg fandt ingen latensmåling.
- **Offentlige data:** åbent søge-API (`/api/v1/services?protocol=&health=&verified=`), `/api/v1/health`, RSS, Nostr (NIP-99), en MCP-server (`@402index/mcp-server`) og HMAC-signerede webhooks. Licensen for selve dataene er ikke angivet.
- **Forretningsmodel:** jeg fandt ingen betalte niveauer, ingen fremhævede listninger og intet betalt alarmprodukt. Det ligner et community- eller open source-projekt. **Vigtigt for 402ward:** de giver allerede helt gratis det, en simpel monitor ville sælge, nemlig sundhedstjek hver time, et korrekthedstjek af challengen og webhooks.

### Afsenderen af "free week of outside route-watch"

- Den eneste offentlige spor er **Fizzl13/x402-doctor PR #524** (merged 2026-11-04): "This covers what an outside 'route-watch' service offered us for **5 USDC a month**, at no cost." Udbyderen byggede i stedet sin egen kontrol hvert 10. minut i GitHub Actions. Den tjekker, at `/health` giver 200, og at den betalte rute giver 402 med en `PAYMENT-REQUIRED`-header, der dekoder til en challenge med Base (`eip155:8453`). Ved fejl prøver den igen efter 60 sekunder og opretter ved dobbeltfejl et GitHub-issue.
- **Afsenderens identitet er ikke offentlig.** "Free week" og navnet "route-watch" findes ikke i noget indekseret materiale. (`jackcrombie/route-watch` og `route.watch` har intet med det at gøre: det er hhv. et værktøj til netværksstier og GPS-flådestyring.)
- Mønstret går igen i økosystemet: uopfordrede tilbud via GitHub-issues og mails til udbydere, som man finder via Bazaar. For eksempel tilbød edvyno x402scan et gratis ugentligt sundhedsfeed som indgang til en **rapport til $99**. Pointen er, at **selv en billig og proaktivt solgt monitor blev opsagt, så snart den var vist frem**, fordi den kan bygges på en eftermiddag.

### x402 Bazaar og Agentic Market (Coinbase)

- **Bazaar** er CDP's discovery-lag. Endpoints bliver indekseret automatisk, når de afregner via CDP-facilitatoren med Bazaar-udvidelsen slået til. Det eneste kvalitetssignal er `quality.{l30DaysTotalCalls, l30DaysUniquePayers, lastCalledAt}`. Der er **ingen felter for oppetid eller sundhed**. Dokumentationen kalder det selv "more like Yahoo search".
- **Agentic.Market** (lanceret 2026-04-20) er Coinbases kuraterede frontend ovenpå Bazaar. Den har en **gratis x402 Endpoint Validator** (`agentic.market/validate`, API `POST /platform/v2/x402/validate`, ingen nøgle). Den tjekker blandt andet challengen og metadata (beskrivelser over 500 tegn afvises, tekst der ligner prompt-injection filtreres fra). Det er et engangstjek, ikke løbende overvågning.
- Kendte huller (x402-foundation/x402#2557): listninger, der "hænger" mellem Bazaar og Agentic Market, kun rod-stien bliver indekseret (1 af 4+ betalte endpoints), forældede poster og navne, der ligner varemærker. Det er reelle smertepunkter for udbydere, men de løses opstrøms hos Coinbase og ikke af en monitor.

### Andre aktører

| Aktør | Vinkel | Pris |
|---|---|---|
| **x402-list.com/status** | Oppetid og svartid for ~850 services | gratis |
| **zauth Provider Hub** | SDK-middleware: oppetid, succesrate, svartid, omsætning, mail-alarmer | freemium (pris ikke fundet) |
| **x402-trust (x402.fuchss.app, MCP)** | Trust score, historik pr. endpoint, *watch* i 30 dage med alarm ved ændring af **payTo**, pris, asset eller netværk, spec-regression, delisting og liveness | betaling pr. kald via x402 |
| **x402station.io /watch** | Watch-abonnementer via MCP og API | betaling pr. kald |
| **a-un Endpoint Monitor** (Base Bazaar) | Tjek ca. hver 4. time, ~42 tjek pr. betaling, webhook ved ændret dom | engangsbetaling via x402 |
| **"watch-pack"** (dev.to) | 250 ændringstjek mod ét endpoint over 90 dage | $1 |
| **x402 Doctor Scan** (stelardigital) | Offentlig leaderboard med 9 tjek og karakter | gratis |
| **Forgemesh /scan** | Karakter A–F: "Can agents actually pay you?" | gratis |
| **edvyno** | Karakter og fejl-id pr. host for hele Bazaar | gratis feed / $99 rapport |
| **x402scan (Merit Systems), x402 Atlas** | Explorer og analytics (transaktioner, top-servere) | gratis |
| **agent402.tools seller-trust**, "observed trust"-sider | Trust-evidens om sælger | betaling pr. kald |
| **nohumans.directory** | Katalog med løbende gen-test | 5 gratis listninger pr. domæne |
| **Udbyderne selv** | Cron eller GitHub Actions på 20 linjer (Fizzl13) | $0 |

## 3. Er der plads til 402ward? Korrekthed vs. ren oppetid

**Ren oppetid: nej.** Det er en commodity. Ping og "svarer ruten 402?" findes gratis hos 402index (hver time), x402-list, zauth og Better Stack/UptimeRobot med en statuskode-regel. Prisen er presset ned til omkring $1 for 250 tjek. Det bedste bevis er, at den eneste kendte betalte kunde (5 USDC/md.) skiftede til at gøre det selv.

**Korrekthed af 402-svaret (statisk): også stort set dækket.** At parse `PAYMENT-REQUIRED`, validere v1/v2-skemaet, tjekke `accepts`, netværk, asset og `.well-known/x402` findes allerede gratis som engangstjek (CDP validator, Forgemesh, x402 Doctor, edvyno). Løbende drift i payTo og pris findes som betalt watch (x402-trust, x402station). En ny aktør vil skulle konkurrere med Coinbases egen validator.

**Hvad dækkes *ikke* (eller dårligt)?**
1. **End-to-end betalte canary-kald.** Faktisk at betale ~$0,001–0,01, verificere afregningen on-chain, og at det betalte svar (a) leveres, (b) matcher det annoncerede output-skema i Bazaar og (c) ikke er "paid-but-denied". Ifølge arXiv 2605.30998 er det en reel angrebs- og fejlklasse. Ingen af de fundne værktøjer siger tydeligt, at de betaler for at teste. Det koster penge pr. tjek, og derfor er der en voldgrav.
2. **Tjek på tværs af facilitatorer og netværk.** Virker betalingen faktisk via CDP, PayAI og andre, og på hvert annonceret netværk (Base, Solana, Polygon …)? Kataloget viser, at mange endpoints annoncerer 5–10 netværk, men sandsynligvis kun er testet på ét.
3. **Pre-flight på køber-siden.** Agenter og wallets vil gerne spørge "skal jeg betale dette endpoint?" før de betaler. Her konkurrerer man med x402-trust og agent402, men det er den side, hvor pengene bevæger sig.

**Markedsstørrelse, selv for den skarpe vinkel:** ~250 hosts med reelle betalere, hvoraf mange er hobbyprojekter. Med en realistisk pris på $5–20/md. og 10 % konvertering bliver det **< $500/md.** Det kan ikke bære et produkt, men det kan validere en niche, hvis køber-siden (agent-platforme og wallets) betaler pr. kald.

## 4. Anbefaling: **Byg anderledes, ellers drop**

**Drop** 402ward som "x402-validator/monitor" i den form, navnet antyder. Både oppetid og statisk 402-korrekthed findes gratis, også fra Coinbase selv, og den eneste dokumenterede kunde valgte at bygge det selv.

**Byg kun anderledes**, hvis der er appetit på et lille, tidsbegrænset eksperiment:
- **Produkt:** "402ward canary". Rigtige mikrobetalinger mod udvalgte endpoints, der verificerer afregning, leveret svar og skema og afprøver hvert annonceret netværk og hver facilitator. Resultatet sælges **pr. kald via x402 til købere og agent-platforme** (pre-flight-dom med evidens). Ikke som et abonnement til udbydere.
- **Datagrundlag:** CDP discovery-API'et (gratis, offentligt). Prioritér de ~250 hosts med ≥10 betalere.
- **Tidsramme:** 4 uger. **Stop-kriterier:** (a) under 5 eksterne betalende kald om dagen efter 4 uger, eller (b) x402-trust, x402station, 402index eller Coinbase lancerer betalte canary-kald, eller (c) canary-omkostningen pr. dom overstiger den pris, markedet vil betale (~$0,01).

**Hvis tiden ikke er til et eksperiment, er "drop" det rigtige svar.**

## Metode og forbehold

- Primærdata: et fuldt træk fra CDP Bazaar `/platform/v2/x402/discovery/resources` (33.085 poster, 2026-11-09). Rådata er ikke committet. Trækket kan genskabes med offset-paginering (`limit=1000`).
- Sessionens netværk blokerede 402index.io, agentic.market, docs.x402.org, dev.to og de fleste tredjeparts-hosts. Oplysningerne om dem kommer fra søgeuddrag og GitHub (README, PR'er og issues). Tal fra leverandørernes egne sider er ikke uafhængigt verificeret.
- Ingen live test af endpoints. Tallene for korrekthed (87,3 %, 430/727 osv.) er tredjepartsmålinger med hver sin metode.

## Kilder

- CDP Bazaar discovery-API: https://api.cdp.coinbase.com/platform/v2/x402/discovery/resources
- 402index: https://402index.io/ · https://402index.io/api-docs · https://github.com/ryanthegentry/402index · https://github.com/frynetworks/402index
- "What AI agents actually paid for on x402: October 2026": https://dev.to/feldsparaiagent/what-ai-agents-actually-paid-for-on-x402-october-2026-44cf
- Fizzl13/x402-doctor PR #524 (route-watch, 5 USDC/md.): https://github.com/Fizzl13/x402-doctor/pull/524
- x402 Bazaar-dokumentation: https://docs.x402.org/extensions/bazaar
- Agentic.Market: https://www.coinbase.com/en-gb/developer-platform/discover/launches/agentic-market · https://agentic.market/validate
- Bazaar/Agentic Market-huller: https://github.com/x402-foundation/x402/issues/2557
- AWS AgentCore + Bazaar: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/payments-connect-bazaar.html
- edvyno-sundhedsfeed: https://github.com/Merit-Systems/x402scan/issues/1318
- x402scan: https://www.x402scan.com/ · x402 Atlas: https://x402atlas.com/
- x402-list status: https://x402-list.com/status
- zauth Provider Hub: https://zauth.inc/provider-hub
- x402-trust MCP: https://glama.ai/mcp/servers/JonasFuchss/x402-trust-mcp
- x402station watch: https://www.x402station.io/watch
- a-un Endpoint Monitor: https://opensea.io/tools/x402-bazaar/base/8468483623937967931
- x402 Doctor Scan: https://stelardigital.com/x402-doctor/scan · Forgemesh: https://forgemesh.io/scan
- x402jp: https://endpoint.x402jp.com/ · nohumans.directory: https://api.nohumans.directory/
- "We probed 20,338 x402 endpoints": https://dev.to/afx/we-probed-20338-x402-endpoints-161-are-agent-honeypots-4c3n
- Angreb på x402 (paid-but-denied): https://arxiv.org/pdf/2605.30998
- agent402 seller-trust: https://agent402.tools/tools/seller-trust
