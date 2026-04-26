"""
scripts/generate_compliance_tasks_v2.py

Extends the compliance database with NL, UK, plus additional DE/US/EU tasks.
Merges into sme_worldmodel_v1.5.json without duplicating existing T-COMP IDs.
"""

import json
from pathlib import Path

TASKS = [

    # ── NETHERLANDS (NL) ──────────────────────────────────────────

    {
        "id": "T-COMP-0050",
        "name": "BTW-aangifte",
        "name_en": "VAT Return (Netherlands)",
        "domain": "D-LEG",
        "description": "Periodieke aangifte omzetbelasting bij de Belastingdienst. Kwartaalaangifte voor kleine ondernemers (< €1.886 per jaar); maandaangifte voor grotere bedragen. Via Mijn Belastingdienst Zakelijk of boekhoudpakket.",
        "cause": {
            "trigger": "Einde kwartaal of maand; uiterste indiendatum is de laatste dag van de maand na het aangiftetijdvak",
            "business_need": "Wettelijke verplichting Wet OB 1968; voorkomen van naheffingsaanslagen",
            "upstream_tasks": []
        },
        "effect": {
            "output": "Ingediende BTW-aangifte; betaling of teruggaaf",
            "downstream_tasks": []
        },
        "state_inputs": ["verkoopfacturen", "inkoopfacturen", "btw-grootboek"],
        "state_outputs": ["ingediende aangifte", "betalingsbevestiging"],
        "agent_profile": {
            "automatable": "ask_first",
            "guardrails": [
                "Nooit indienen zonder controle van de boekhouder",
                "Altijd suppletie indienen bij ontdekte fouten — nooit stilzwijgend aanpassen"
            ],
            "escalation_triggers": [
                "Betaalverplichting boven €10.000",
                "Teruggaafverzoek boven €5.000"
            ]
        },
        "failure": {
            "risk_level": "high",
            "failure_mode": "Te late indiening of betaling",
            "business_damage": "Verzuimboete tot €5.514; belastingrente 8% per jaar (2024)"
        },
        "_compliance": {
            "jurisdiction": ["NL"],
            "frequency": "quarterly",
            "scale_threshold": "all",
            "deadline": "Laatste dag van de maand na het aangiftetijdvak",
            "legal_source": {"name": "Wet OB 1968 / AWR", "url": "https://wetten.overheid.nl/BWBR0002629", "article": "Art. 14 Wet OB 1968"},
            "validation_method": "Bevestigingsmail Belastingdienst; bankafschrift betaling"
        }
    },
    {
        "id": "T-COMP-0051",
        "name": "Suppletie-aangifte BTW",
        "name_en": "VAT Supplementary Return (Netherlands)",
        "domain": "D-LEG",
        "description": "Vrijwillige correctie van eerder onjuist ingediende BTW-aangifte via suppletieformulier. Verplicht bij ontdekte fouten > €1.000 per tijdvak. Vrijwillige inkeer vermindert boeterisico.",
        "cause": {
            "trigger": "Ontdekking van fout in eerder ingediende BTW-aangifte",
            "business_need": "Wettelijke meldingsplicht; voorkomen van fraude-kwalificatie",
            "upstream_tasks": ["T-COMP-0050"]
        },
        "effect": {
            "output": "Ingediend suppletieformulier; eventuele nabetaling",
            "downstream_tasks": []
        },
        "state_inputs": ["oorspronkelijke aangifte", "gecorrigeerde berekening"],
        "state_outputs": ["suppletieformulier", "betalingsbewijs"],
        "agent_profile": {
            "automatable": "human_only",
            "guardrails": ["Altijd melden bij boekhouder vóór indiening"],
            "escalation_triggers": ["Fout boven €1.000", "Fout meerdere tijdvakken"]
        },
        "failure": {
            "risk_level": "high",
            "failure_mode": "Niet melden van ontdekte fout",
            "business_damage": "Vergrijpboete tot 100% van het na te betalen bedrag; strafrechtelijk risico"
        },
        "_compliance": {
            "jurisdiction": ["NL"],
            "frequency": "event_driven",
            "scale_threshold": "all",
            "deadline": "Zo snel mogelijk na ontdekking; uiterlijk voor belastingcontrole",
            "legal_source": {"name": "AWR", "url": "https://wetten.overheid.nl/BWBR0002320", "article": "Art. 10a AWR"},
            "validation_method": "Ontvangstbevestiging Belastingdienst"
        }
    },
    {
        "id": "T-COMP-0052",
        "name": "Loonaangifte",
        "name_en": "Payroll Tax Return (Netherlands)",
        "domain": "D-LEG",
        "description": "Maandelijkse aangifte loonheffingen (loonbelasting, premie volksverzekeringen, premies werknemersverzekeringen en bijdrage Zvw) bij de Belastingdienst. Indiening en betaling vóór de laatste werkdag van de aangiftemaand.",
        "cause": {
            "trigger": "Einde van elke aangifteperiode (kalendermaand); na iedere loonbetaling",
            "business_need": "Wettelijke inhoudingsplicht werkgever; financiering sociale zekerheid",
            "upstream_tasks": []
        },
        "effect": {
            "output": "Ingediende loonaangifte; betaling loonheffingen aan Belastingdienst",
            "downstream_tasks": []
        },
        "state_inputs": ["salarisstroken", "BSN-nummers werknemers", "loonbelastingkaarten"],
        "state_outputs": ["loonaangifte", "betalingsbevestiging"],
        "agent_profile": {
            "automatable": "notify",
            "guardrails": [
                "Nooit loonheffing inhouden maar niet afdragen",
                "Correctieberichten indienen bij fouten — niet aanpassen in volgende aangifte"
            ],
            "escalation_triggers": [
                "Nieuwe werknemer (aantrekken BSN en loonbelastingverklaring)",
                "Werknemer ziek melden bij UWV"
            ]
        },
        "failure": {
            "risk_level": "critical",
            "failure_mode": "Niet of te laat afdragen loonheffingen",
            "business_damage": "Verzuimboete €68–€5.514; belastingrente; persoonlijke aansprakelijkheid bestuurder (meldingsplicht betalingsonmacht)"
        },
        "_compliance": {
            "jurisdiction": ["NL"],
            "frequency": "monthly",
            "scale_threshold": "1 FTE",
            "deadline": "Laatste werkdag van de aangiftemaand",
            "legal_source": {"name": "Wet LB 1964 / AWR", "url": "https://wetten.overheid.nl/BWBR0002471", "article": "Art. 27 Wet LB 1964"},
            "validation_method": "Bevestigingsmail Belastingdienst; bankafschrift"
        }
    },
    {
        "id": "T-COMP-0053",
        "name": "Vennootschapsbelasting aangifte",
        "name_en": "Corporate Income Tax Return (Netherlands)",
        "domain": "D-LEG",
        "description": "Jaarlijkse aangifte vennootschapsbelasting (VPB) voor BV's en NV's. Tarief 19% tot €200.000 winst; 25,8% daarboven. Aangifte via fiscaal dienstverlener of online. Termijn: 5 maanden na boekjaarafsluiting (standaard 1 juni).",
        "cause": {
            "trigger": "Afsluiting boekjaar; uiterlijk 1 juni van het volgende jaar (of later bij uitstelregeling belastingadviseur)",
            "business_need": "Wettelijke belastingaangifteplicht voor rechtspersonen",
            "upstream_tasks": []
        },
        "effect": {
            "output": "Ingediende VPB-aangifte; aanslag vennootschapsbelasting",
            "downstream_tasks": []
        },
        "state_inputs": ["jaarrekening", "fiscale winstberekening", "fiscale reserves"],
        "state_outputs": ["VPB-aangifte", "belastingaanslag"],
        "agent_profile": {
            "automatable": "human_only",
            "guardrails": ["Altijd door belastingadviseur laten indienen"],
            "escalation_triggers": ["Fiscale winst > €200.000 (hogere tariefschijf)", "Verliesjaar (verliesverrekening)"]
        },
        "failure": {
            "risk_level": "high",
            "failure_mode": "Te late aangifte; schatting door Belastingdienst",
            "business_damage": "Verzuimboete €68–€5.514; ambtshalve aanslag met hoge schatting"
        },
        "_compliance": {
            "jurisdiction": ["NL"],
            "frequency": "yearly",
            "scale_threshold": "all",
            "deadline": "1 juni (standaard); tot 1 mei volgend jaar met uitstel via belastingadviseur",
            "legal_source": {"name": "Wet Vpb 1969", "url": "https://wetten.overheid.nl/BWBR0002672", "article": "Art. 25 Wet Vpb"},
            "validation_method": "Ontvangstbevestiging Belastingdienst; aanslag"
        }
    },
    {
        "id": "T-COMP-0054",
        "name": "KvK jaarrekening deponeren",
        "name_en": "Annual Accounts Filing (Netherlands — KvK)",
        "domain": "D-LEG",
        "description": "BV's, NV's en bepaalde VOF's zijn verplicht de jaarrekening te deponeren bij het Handelsregister (KvK) binnen 8 maanden na het boekjaar (of 12 maanden met aandeelhoudersuitstel). Kleine BV's mogen een verkorte balans deponeren.",
        "cause": {
            "trigger": "Uiterlijk 8 maanden na boekjaarafsluiting (standaard 31 augustus)",
            "business_need": "Wettelijke openbaarmakingsplicht; bescherming crediteuren",
            "upstream_tasks": []
        },
        "effect": {
            "output": "Gedeponeerde jaarrekening bij KvK (openbaar raadpleegbaar)",
            "downstream_tasks": []
        },
        "state_inputs": ["vastgestelde jaarrekening", "AVA-notulen of aandeelhoudersbesluit"],
        "state_outputs": ["deponeringsbewijs KvK"],
        "agent_profile": {
            "automatable": "human_only",
            "guardrails": ["AVA moet jaarrekening hebben vastgesteld vóór deponering"],
            "escalation_triggers": ["Termijn 2 maanden voor deadline bereikt"]
        },
        "failure": {
            "risk_level": "high",
            "failure_mode": "Niet of te laat deponeren",
            "business_damage": "Bestuurdersaansprakelijkheid bij faillissement (art. 2:248 BW); boete tot €22.500"
        },
        "_compliance": {
            "jurisdiction": ["NL"],
            "frequency": "yearly",
            "scale_threshold": "all",
            "deadline": "8 maanden na boekjaarafsluiting (standaard 31 augustus)",
            "legal_source": {"name": "BW Boek 2", "url": "https://wetten.overheid.nl/BWBR0003045", "article": "Art. 2:394 BW"},
            "validation_method": "Deponeringsbewijs KvK; openbare raadpleging handelsregister"
        }
    },
    {
        "id": "T-COMP-0055",
        "name": "KvK mutaties doorgeven",
        "name_en": "Chamber of Commerce — Update Business Register",
        "domain": "D-LEG",
        "description": "Wijzigingen in het handelsregister (adres, bestuurders, aandeelhouders, activiteiten, rechtsvorm) moeten binnen 1 week worden doorgegeven aan de KvK. Kosten €17,80 per mutatie (2024).",
        "cause": {
            "trigger": "Wijziging in bedrijfsgegevens (adres, bestuurder, SBI-code, filiaal, etc.)",
            "business_need": "Actueel handelsregister; wettelijke verplichting Handelsregisterwet",
            "upstream_tasks": []
        },
        "effect": {
            "output": "Bijgewerkte inschrijving handelsregister",
            "downstream_tasks": []
        },
        "state_inputs": ["actuele bedrijfsgegevens", "notariële akte bij structuurwijziging"],
        "state_outputs": ["bijgewerkt KvK-uittreksel"],
        "agent_profile": {
            "automatable": "ask_first",
            "guardrails": ["Adreswijziging tijdig doorgeven — crediteuren en overheid vertrouwen op KvK-adres"],
            "escalation_triggers": ["Bestuurswisseling", "Aandeelhouderswijziging > 25%"]
        },
        "failure": {
            "risk_level": "medium",
            "failure_mode": "Verouderd handelsregister",
            "business_damage": "Boete tot €9.000 (Handelsregisterwet art. 29); civiele aansprakelijkheid bij schade door verouderde gegevens"
        },
        "_compliance": {
            "jurisdiction": ["NL"],
            "frequency": "event_driven",
            "scale_threshold": "all",
            "deadline": "Binnen 1 week na de wijziging",
            "legal_source": {"name": "Handelsregisterwet 2007", "url": "https://wetten.overheid.nl/BWBR0021777", "article": "Art. 19 Handelsregisterwet"},
            "validation_method": "Bijgewerkt KvK-uittreksel"
        }
    },
    {
        "id": "T-COMP-0056",
        "name": "AVG verwerkingsregister bijhouden",
        "name_en": "GDPR Processing Register (Netherlands — AVG)",
        "domain": "D-LEG",
        "description": "Bijhouden van een register van verwerkingsactiviteiten (art. 30 AVG/GDPR) met daarin alle persoonsgegevens die worden verwerkt, het doel, de rechtsgrond, de bewaartermijn en de ontvangers. Jaarlijkse review verplicht.",
        "cause": {
            "trigger": "Bij aanvang verwerking nieuwe persoonsgegevens; jaarlijkse review in januari",
            "business_need": "AVG-verplichting; aantonend kunnen voldoen aan verantwoordingsplicht (accountability)",
            "upstream_tasks": []
        },
        "effect": {
            "output": "Actueel verwerkingsregister; bijgewerkte verwerkersovereenkomsten",
            "downstream_tasks": []
        },
        "state_inputs": ["overzicht persoonsgegevensverwerkingen", "leverancierscontracten"],
        "state_outputs": ["bijgewerkt register", "getekende verwerkersovereenkomsten"],
        "agent_profile": {
            "automatable": "ask_first",
            "guardrails": [
                "Nooit nieuwe verwerking starten zonder rechtsgrond vastgelegd in register",
                "Verwerkersovereenkomst verplicht bij elke verwerker"
            ],
            "escalation_triggers": [
                "Nieuwe verwerking bijzondere persoonsgegevens (gezondheid, BSN)",
                "Derde-land doorgifte zonder adequaatheidsbesluit"
            ]
        },
        "failure": {
            "risk_level": "high",
            "failure_mode": "Geen of onvolledig register; geen verwerkersovereenkomsten",
            "business_damage": "Boete AP tot €10 miljoen of 2% van wereldwijde omzet (art. 83 lid 4 AVG)"
        },
        "_compliance": {
            "jurisdiction": ["NL"],
            "frequency": "yearly",
            "scale_threshold": "all",
            "deadline": "Doorlopend; jaarlijkse review vóór 1 februari",
            "legal_source": {"name": "AVG / GDPR", "url": "https://eur-lex.europa.eu/eli/reg/2016/679", "article": "Art. 30 AVG"},
            "validation_method": "Intern auditrapport; steekproef verwerkersovereenkomsten"
        }
    },
    {
        "id": "T-COMP-0057",
        "name": "AVG datalek melden bij AP",
        "name_en": "Data Breach Notification to Dutch DPA (Autoriteit Persoonsgegevens)",
        "domain": "D-LEG",
        "description": "Melding van een datalek bij de Autoriteit Persoonsgegevens (AP) binnen 72 uur na ontdekking. Bij hoog risico voor betrokkenen ook directe melding aan die personen. Gebruik het AP-meldloket.",
        "cause": {
            "trigger": "Ontdekking van een inbreuk op persoonsgegevens (verlies, ongeautoriseerde toegang, wijziging)",
            "business_need": "Wettelijke meldplicht art. 33 AVG; voorkomen van boete en reputatieschade",
            "upstream_tasks": []
        },
        "effect": {
            "output": "Datalekmelding bij AP; eventuele melding aan betrokkenen",
            "downstream_tasks": []
        },
        "state_inputs": ["incidentrapport", "beoordeling risico voor betrokkenen"],
        "state_outputs": ["AP-melding", "interne documentatie datalek"],
        "agent_profile": {
            "automatable": "human_only",
            "guardrails": [
                "Nooit langer dan 72 uur wachten met melding",
                "Nooit zelf beslissen over niet-melding zonder juridisch advies"
            ],
            "escalation_triggers": ["Ieder vermoed datalek — zelfs bij twijfel"]
        },
        "failure": {
            "risk_level": "critical",
            "failure_mode": "Niet of te laat melden van datalek",
            "business_damage": "Boete AP tot €20 miljoen of 4% van wereldwijde omzet; reputatieschade"
        },
        "_compliance": {
            "jurisdiction": ["NL"],
            "frequency": "event_driven",
            "scale_threshold": "all",
            "deadline": "72 uur na ontdekking",
            "legal_source": {"name": "AVG", "url": "https://autoriteitpersoonsgegevens.nl/nl/onderwerpen/beveiliging/meldplicht-datalekken", "article": "Art. 33–34 AVG"},
            "validation_method": "Referentienummer AP-melding; tijdstempel ontdekking vs. melding"
        }
    },
    {
        "id": "T-COMP-0058",
        "name": "RI&E opstellen en actualiseren",
        "name_en": "Risk Inventory and Evaluation (Netherlands — RI&E)",
        "domain": "D-LEG",
        "description": "Elke werkgever met personeel is verplicht een Risico-Inventarisatie en -Evaluatie (RI&E) op te stellen en een bijbehorend Plan van Aanpak. Actualisatie bij organisatiewijziging of jaarlijks. Bedrijven < 25 medewerkers mogen een branche-RI&E gebruiken.",
        "cause": {
            "trigger": "Bij aanvang werkgeverschap; jaarlijkse review; of na bedrijfsongeval",
            "business_need": "Wettelijke verplichting Arbeidsomstandighedenwet; voorkomen arbeidsongeval",
            "upstream_tasks": []
        },
        "effect": {
            "output": "Actuele RI&E; Plan van Aanpak met maatregelen en deadlines",
            "downstream_tasks": []
        },
        "state_inputs": ["werkplekoverzicht", "aanwezige machines en gevaarlijke stoffen", "ziekteverzuimcijfers"],
        "state_outputs": ["RI&E document", "Plan van Aanpak"],
        "agent_profile": {
            "automatable": "human_only",
            "guardrails": ["RI&E laten toetsen door gecertificeerde arbodeskundige (> 25 medewerkers)"],
            "escalation_triggers": ["Ernstig bedrijfsongeval → directe melding Inspectie SZW"]
        },
        "failure": {
            "risk_level": "high",
            "failure_mode": "Geen of verouderde RI&E",
            "business_damage": "Boete Inspectie SZW tot €50.000 per overtreding; aansprakelijkheid bij bedrijfsongeval"
        },
        "_compliance": {
            "jurisdiction": ["NL"],
            "frequency": "yearly",
            "scale_threshold": "1 FTE",
            "deadline": "Doorlopend; jaarlijkse review",
            "legal_source": {"name": "Arbeidsomstandighedenwet", "url": "https://wetten.overheid.nl/BWBR0010346", "article": "Art. 5 Arbowet"},
            "validation_method": "Actuele RI&E + Plan van Aanpak aanwezig; toetsingsrapport arbodeskundige"
        }
    },
    {
        "id": "T-COMP-0059",
        "name": "Pensioenpremies afdragen",
        "name_en": "Pension Premium Remittance (Netherlands)",
        "domain": "D-LEG",
        "description": "Maandelijkse afdracht van pensioenpremies (werkgevers- en werknemersdeel) aan het verplichtgestelde bedrijfspensioenfonds of de gekozen pensioenuitvoerder. Controleer of de sector onder een verplicht pensioenfonds valt (Pensioenwet art. 2).",
        "cause": {
            "trigger": "Maandelijks; na iedere loonbetaling",
            "business_need": "Wettelijke verplichting Pensioenwet; arbeidsrechtelijke verplichting",
            "upstream_tasks": ["T-COMP-0052"]
        },
        "effect": {
            "output": "Pensioenpremies afgedragen; pensioenopgave naar uitvoerder",
            "downstream_tasks": []
        },
        "state_inputs": ["brutoloonlijst", "premiepercentages pensioenfonds"],
        "state_outputs": ["betalingsbevestiging pensioenfonds"],
        "agent_profile": {
            "automatable": "notify",
            "guardrails": ["Nooit pensioenpremies gebruiken als werkkapitaal — directe aansprakelijkheid"],
            "escalation_triggers": ["Nieuwe werknemer in verplichtgestelde sector", "Sectorwijziging"]
        },
        "failure": {
            "risk_level": "high",
            "failure_mode": "Niet of onvolledig afdragen pensioenpremies",
            "business_damage": "Persoonlijke aansprakelijkheid bestuurder; rente en incassokosten pensioenfonds; DNB-handhaving"
        },
        "_compliance": {
            "jurisdiction": ["NL"],
            "frequency": "monthly",
            "scale_threshold": "1 FTE",
            "deadline": "Conform betalingsregels pensioenfonds (doorgaans binnen 30 dagen na maand)",
            "legal_source": {"name": "Pensioenwet", "url": "https://wetten.overheid.nl/BWBR0020809", "article": "Art. 2, 23, 29 Pensioenwet"},
            "validation_method": "Afschriften pensioenfonds; jaarlijkse pensioenopgave werknemers"
        }
    },
    {
        "id": "T-COMP-0060",
        "name": "WKA-verklaring inlening personeel",
        "name_en": "Chain Liability Compliance (Netherlands — WKA)",
        "domain": "D-LEG",
        "description": "Bij inlening van personeel via uitzendbureaus of onderaannemers: controleer of het bureau gecertificeerd is (NEN 4400-1 of SNA-keurmerk) en bewaar facturen en betalingsbewijzen. Gebruik een G-rekening of depot om aansprakelijkheid te beperken.",
        "cause": {
            "trigger": "Bij elke inhuur van derden-personeel of uitbesteding van werk",
            "business_need": "Ketenaansprakelijkheid voor loonheffingen en BTW; Wet Aanpak Schijnconstructies",
            "upstream_tasks": []
        },
        "effect": {
            "output": "Gecertificeerde bureaus; G-rekening stortingen; gedocumenteerde factuurhistorie",
            "downstream_tasks": []
        },
        "state_inputs": ["inhuurfacturen", "NEN/SNA-certificaat uitzendbureau"],
        "state_outputs": ["G-rekening-stortingen", "depot-bewijzen"],
        "agent_profile": {
            "automatable": "ask_first",
            "guardrails": [
                "Nooit inhuren bij niet-gecertificeerd bureau zonder G-rekening",
                "Altijd SNA-register checken vóór ondertekening contract"
            ],
            "escalation_triggers": ["Uitzendbureau verliest certificering", "Factuur zonder BTW-nummer"]
        },
        "failure": {
            "risk_level": "high",
            "failure_mode": "Inlening bij niet-gecertificeerd bureau zonder bescherming",
            "business_damage": "Hoofdelijke aansprakelijkheid voor loonheffingen en BTW van het uitzendbureau"
        },
        "_compliance": {
            "jurisdiction": ["NL"],
            "frequency": "event_driven",
            "scale_threshold": "all",
            "deadline": "Bij elke inhuur controleren",
            "legal_source": {"name": "WKA / Invorderingswet 1990", "url": "https://wetten.overheid.nl/BWBR0004770", "article": "Art. 34–35 Invorderingswet"},
            "validation_method": "SNA-register controle; G-rekening-afschriften"
        }
    },

    # ── UNITED KINGDOM (UK) ───────────────────────────────────────

    {
        "id": "T-COMP-0070",
        "name": "VAT Return (UK — HMRC)",
        "name_en": "UK VAT Return (Making Tax Digital)",
        "domain": "D-LEG",
        "description": "Quarterly VAT return filed via MTD-compatible software. Mandatory for VAT-registered businesses (threshold £90,000 turnover). Standard rate 20%, reduced 5%, zero-rated for specific goods. Payment due 1 month and 7 days after period end.",
        "cause": {
            "trigger": "End of each VAT quarter (typically Jan/Apr/Jul/Oct or Feb/May/Aug/Nov)",
            "business_need": "Legal obligation under VATA 1994; MTD compliance from April 2022",
            "upstream_tasks": []
        },
        "effect": {
            "output": "Filed VAT return via MTD software; payment made to HMRC",
            "downstream_tasks": []
        },
        "state_inputs": ["sales invoices", "purchase invoices", "VAT account"],
        "state_outputs": ["MTD submission confirmation", "payment reference"],
        "agent_profile": {
            "automatable": "ask_first",
            "guardrails": [
                "Must use MTD-compatible software — no manual spreadsheet submission",
                "Never claim input VAT on non-business expenses"
            ],
            "escalation_triggers": ["VAT liability above £10,000", "Refund claim above £5,000"]
        },
        "failure": {
            "risk_level": "high",
            "failure_mode": "Late or incorrect VAT return; non-MTD filing",
            "business_damage": "Default surcharge 2–15% of tax due; penalty points system from Jan 2023 (up to £10,000)"
        },
        "_compliance": {
            "jurisdiction": ["UK"],
            "frequency": "quarterly",
            "scale_threshold": "all",
            "deadline": "1 calendar month + 7 days after VAT period end",
            "legal_source": {"name": "VATA 1994 / MTD", "url": "https://www.gov.uk/vat-returns", "article": "VATA 1994 s.25; SI 2018/261"},
            "validation_method": "HMRC online portal submission reference"
        }
    },
    {
        "id": "T-COMP-0071",
        "name": "PAYE / RTI Full Payment Submission",
        "name_en": "PAYE Real Time Information (RTI) — Full Payment Submission",
        "domain": "D-LEG",
        "description": "Submit a Full Payment Submission (FPS) to HMRC via payroll software on or before each payday. Report PAYE, National Insurance, and student loan deductions in real time. Also submit an Employer Payment Summary (EPS) if no payments were made.",
        "cause": {
            "trigger": "On or before every payday",
            "business_need": "RTI obligation since April 2013; underpins Universal Credit calculation",
            "upstream_tasks": []
        },
        "effect": {
            "output": "FPS accepted by HMRC; payroll tax paid via BACS",
            "downstream_tasks": []
        },
        "state_inputs": ["payroll run data", "employee NI numbers", "tax codes"],
        "state_outputs": ["FPS acceptance message", "payment to HMRC"],
        "agent_profile": {
            "automatable": "notify",
            "guardrails": [
                "Never miss an FPS — late submissions trigger automatic penalties",
                "Submit EPS by 19th if no FPS was sent in a month"
            ],
            "escalation_triggers": ["New starter (Starter Checklist required)", "Leavers (P45 required)"]
        },
        "failure": {
            "risk_level": "high",
            "failure_mode": "Late or missing FPS",
            "business_damage": "Late filing penalty £100–£400 per month depending on employee count; interest on late payment"
        },
        "_compliance": {
            "jurisdiction": ["UK"],
            "frequency": "monthly",
            "scale_threshold": "1 FTE",
            "deadline": "On or before each payday; PAYE payment by 19th (22nd electronic)",
            "legal_source": {"name": "ITEPA 2003 / Income Tax Regulations", "url": "https://www.gov.uk/running-payroll/fps-after-payday", "article": "SI 2012/822"},
            "validation_method": "HMRC Basic PAYE Tools / payroll software confirmation"
        }
    },
    {
        "id": "T-COMP-0072",
        "name": "Corporation Tax Return (CT600)",
        "name_en": "UK Corporation Tax Return (CT600)",
        "domain": "D-LEG",
        "description": "Annual Corporation Tax return (CT600) filed online with HMRC within 12 months of the company's accounting period end. Tax payment due 9 months and 1 day after period end. Rate: 19% (profits < £50,000), 25% (profits > £250,000), marginal relief between.",
        "cause": {
            "trigger": "12 months after company accounting period end (typically 12 months after year end)",
            "business_need": "Legal obligation; HMRC self-assessment for companies",
            "upstream_tasks": []
        },
        "effect": {
            "output": "Filed CT600; Corporation Tax paid",
            "downstream_tasks": []
        },
        "state_inputs": ["statutory accounts", "tax computations", "capital allowances schedule"],
        "state_outputs": ["CT600 filing reference", "tax payment confirmation"],
        "agent_profile": {
            "automatable": "human_only",
            "guardrails": ["Must be filed with iXBRL-tagged accounts"],
            "escalation_triggers": ["Profit > £250,000 (full 25% rate)", "R&D tax credits claimed"]
        },
        "failure": {
            "risk_level": "high",
            "failure_mode": "Late filing or payment",
            "business_damage": "£100 immediate penalty; £200 if 3+ months late; 10% of unpaid tax after 6/12 months; interest on late payment"
        },
        "_compliance": {
            "jurisdiction": ["UK"],
            "frequency": "yearly",
            "scale_threshold": "all",
            "deadline": "12 months after accounting period end (filing); 9 months + 1 day (payment)",
            "legal_source": {"name": "CTA 2009 / Finance Act 2021", "url": "https://www.gov.uk/company-tax-returns", "article": "CTA 2009 s.2; FA 2021 s.6"},
            "validation_method": "HMRC online filing reference"
        }
    },
    {
        "id": "T-COMP-0073",
        "name": "Companies House Confirmation Statement",
        "name_en": "Companies House Annual Confirmation Statement",
        "domain": "D-LEG",
        "description": "Annual confirmation statement (formerly annual return) filed with Companies House to confirm company details: registered office, directors, shareholders, SIC code, and share capital. Due within 14 days of the 12-month anniversary of incorporation (or last statement).",
        "cause": {
            "trigger": "Annual — 12 months after incorporation date or last statement date",
            "business_need": "Companies Act 2006 obligation; public register accuracy",
            "upstream_tasks": []
        },
        "effect": {
            "output": "Filed confirmation statement (£13 online / £40 paper)",
            "downstream_tasks": []
        },
        "state_inputs": ["current company details", "shareholder register", "PSC register"],
        "state_outputs": ["Companies House filing confirmation"],
        "agent_profile": {
            "automatable": "notify",
            "guardrails": ["PSC register must be up to date before filing"],
            "escalation_triggers": ["Director or shareholder changes not yet reflected"]
        },
        "failure": {
            "risk_level": "high",
            "failure_mode": "Late or missing confirmation statement",
            "business_damage": "Company struck off register; directors personally liable for company debts post-strike-off"
        },
        "_compliance": {
            "jurisdiction": ["UK"],
            "frequency": "yearly",
            "scale_threshold": "all",
            "deadline": "14 days after the confirmation date (12-month review date)",
            "legal_source": {"name": "Companies Act 2006", "url": "https://www.gov.uk/confirmation-statement", "article": "CA 2006 s.853A"},
            "validation_method": "Companies House transaction ID"
        }
    },
    {
        "id": "T-COMP-0074",
        "name": "UK GDPR Data Breach — ICO Notification",
        "name_en": "UK GDPR Data Breach Notification (ICO)",
        "domain": "D-LEG",
        "description": "Report personal data breaches to the Information Commissioner's Office (ICO) within 72 hours of discovery if the breach is likely to result in a risk to individuals. If high risk: also notify affected individuals without undue delay.",
        "cause": {
            "trigger": "Discovery of a personal data breach",
            "business_need": "UK GDPR obligation post-Brexit; ICO enforcement",
            "upstream_tasks": []
        },
        "effect": {
            "output": "ICO breach report (online portal); individual notifications if high risk",
            "downstream_tasks": []
        },
        "state_inputs": ["incident log", "breach risk assessment"],
        "state_outputs": ["ICO report reference", "individual notification records"],
        "agent_profile": {
            "automatable": "human_only",
            "guardrails": ["72-hour clock starts from awareness — not confirmed discovery"],
            "escalation_triggers": ["Any suspected personal data breach"]
        },
        "failure": {
            "risk_level": "critical",
            "failure_mode": "Late or missing breach report to ICO",
            "business_damage": "ICO fine up to £17.5 million or 4% of global annual turnover (whichever higher)"
        },
        "_compliance": {
            "jurisdiction": ["UK"],
            "frequency": "event_driven",
            "scale_threshold": "all",
            "deadline": "72 hours from discovery",
            "legal_source": {"name": "UK GDPR / DPA 2018", "url": "https://ico.org.uk/for-organisations/report-a-breach/", "article": "UK GDPR Art. 33; DPA 2018 s.67"},
            "validation_method": "ICO reference number; timestamp log"
        }
    },
    {
        "id": "T-COMP-0075",
        "name": "Auto-Enrolment Pension Contributions",
        "name_en": "Workplace Pension Auto-Enrolment (UK)",
        "domain": "D-LEG",
        "description": "Automatically enrol eligible workers (aged 22–state pension age, earning >£10,000/year) into a qualifying workplace pension. Minimum contribution: 8% of qualifying earnings (employer 3%, employee 5%). Re-enrol every 3 years.",
        "cause": {
            "trigger": "New eligible employee; every 3 years (re-enrolment date); worker opts out then meets threshold again",
            "business_need": "Pensions Act 2008 obligation; The Pensions Regulator enforcement",
            "upstream_tasks": []
        },
        "effect": {
            "output": "Employee enrolled in pension scheme; contributions paid monthly",
            "downstream_tasks": []
        },
        "state_inputs": ["employee earnings data", "age verification", "pension scheme details"],
        "state_outputs": ["enrolment confirmation", "contribution payment records"],
        "agent_profile": {
            "automatable": "notify",
            "guardrails": [
                "Cannot incentivise workers to opt out",
                "Must re-enrol opt-outs every 3 years automatically"
            ],
            "escalation_triggers": ["Worker opts back in within 1 month (must be enrolled)", "TPR inspection notice"]
        },
        "failure": {
            "risk_level": "high",
            "failure_mode": "Failure to enrol; missed contributions",
            "business_damage": "Fixed penalty £400; escalating penalty £50–£10,000 per day depending on employer size"
        },
        "_compliance": {
            "jurisdiction": ["UK"],
            "frequency": "monthly",
            "scale_threshold": "1 FTE",
            "deadline": "Contributions paid by 22nd of month following deduction",
            "legal_source": {"name": "Pensions Act 2008", "url": "https://www.thepensionsregulator.gov.uk/en/employers", "article": "PA 2008 s.3"},
            "validation_method": "Pension provider contribution statements; re-enrolment declaration filed with TPR every 3 years"
        }
    },
    {
        "id": "T-COMP-0076",
        "name": "P60 Year End Certificates",
        "name_en": "P60 / P11D Year End Employee Tax Documents (UK)",
        "domain": "D-LEG",
        "description": "Issue P60 (total pay and tax summary) to all employees on payroll at 5 April by 31 May each year. File P11D (benefits in kind) with HMRC and issue copies to employees by 6 July. Pay Class 1A NI on benefits by 22 July.",
        "cause": {
            "trigger": "Tax year end (5 April); P60 due 31 May; P11D due 6 July",
            "business_need": "Employee tax filing requirement; HMRC reporting",
            "upstream_tasks": ["T-COMP-0071"]
        },
        "effect": {
            "output": "P60 issued to employees; P11D filed with HMRC; Class 1A NI paid",
            "downstream_tasks": []
        },
        "state_inputs": ["annual payroll summaries", "benefits in kind records"],
        "state_outputs": ["P60 copies", "P11D filing confirmation"],
        "agent_profile": {
            "automatable": "notify",
            "guardrails": ["P60 must be given to employees — not just made available online"],
            "escalation_triggers": ["Employee queries P60 figures before personal tax return deadline"]
        },
        "failure": {
            "risk_level": "medium",
            "failure_mode": "Late P60 or P11D",
            "business_damage": "£300 penalty per P11D not filed by deadline; £60 per day ongoing; Class 1A NI late payment interest"
        },
        "_compliance": {
            "jurisdiction": ["UK"],
            "frequency": "yearly",
            "scale_threshold": "1 FTE",
            "deadline": "P60: 31 May; P11D: 6 July; Class 1A NI: 22 July",
            "legal_source": {"name": "ITEPA 2003", "url": "https://www.gov.uk/employer-reporting-expenses-benefits", "article": "ITEPA 2003 s.67, s.87"},
            "validation_method": "HMRC portal acknowledgment; employee distribution log"
        }
    },
    {
        "id": "T-COMP-0077",
        "name": "Gender Pay Gap Report (UK)",
        "name_en": "Gender Pay Gap Reporting (UK — 250+ employees)",
        "domain": "D-LEG",
        "description": "Annual publication of gender pay gap data on the government portal and company website. Required for employers with 250+ employees. Report must include mean and median hourly pay gap, bonus gap, and proportion of men/women in each pay quartile.",
        "cause": {
            "trigger": "Snapshot date 5 April each year; report due 4 April following year",
            "business_need": "Equality Act 2010 (Gender Pay Gap Information) Regulations 2017",
            "upstream_tasks": []
        },
        "effect": {
            "output": "Published report on government portal and company website",
            "downstream_tasks": []
        },
        "state_inputs": ["payroll data by gender", "bonus payment records"],
        "state_outputs": ["published gender pay gap report"],
        "agent_profile": {
            "automatable": "ask_first",
            "guardrails": ["Report must be signed by a director or equivalent"],
            "escalation_triggers": ["First year crossing 250-employee threshold"]
        },
        "failure": {
            "risk_level": "medium",
            "failure_mode": "Late or missing publication",
            "business_damage": "Unlimited fine via civil enforcement; significant reputational and recruitment damage"
        },
        "_compliance": {
            "jurisdiction": ["UK"],
            "frequency": "yearly",
            "scale_threshold": "250 FTE",
            "deadline": "4 April (private sector); 30 March (public sector)",
            "legal_source": {"name": "Equality Act 2010 / SI 2017/172", "url": "https://www.gov.uk/report-gender-pay-gap-data", "article": "SI 2017/172 reg. 2"},
            "validation_method": "Government reporting portal submission reference"
        }
    },

    # ── EU — AANVULLING ───────────────────────────────────────────

    {
        "id": "T-COMP-0080",
        "name": "AML Customer Due Diligence",
        "name_en": "Anti-Money Laundering — Customer Due Diligence (EU)",
        "domain": "D-LEG",
        "description": "Ongoing customer due diligence (CDD) for businesses subject to AML obligations (accountants, lawyers, notaries, estate agents, tax advisors, crypto providers, dealers in high-value goods >€10,000 cash). Includes KYC, UBO verification, and transaction monitoring.",
        "cause": {
            "trigger": "New customer onboarding; transactions above €10,000 cash; suspicious activity",
            "business_need": "AMLD6 compliance; FATF recommendations; avoid regulatory sanction",
            "upstream_tasks": []
        },
        "effect": {
            "output": "CDD file per customer; UBO register check; suspicious activity reports (SAR) where needed",
            "downstream_tasks": []
        },
        "state_inputs": ["customer identification documents", "UBO registry extract", "transaction history"],
        "state_outputs": ["CDD file", "SAR to FIU if applicable"],
        "agent_profile": {
            "automatable": "ask_first",
            "guardrails": [
                "Never accept cash payments > €10,000 without reporting",
                "Never process transaction for unverified customer"
            ],
            "escalation_triggers": ["PEP (Politically Exposed Person) identified", "High-risk country transaction", "Suspicious transaction pattern"]
        },
        "failure": {
            "risk_level": "critical",
            "failure_mode": "Failure to conduct CDD; failure to file SAR",
            "business_damage": "AMLD6: criminal liability for management; fines up to €5 million or 10% of annual turnover"
        },
        "_compliance": {
            "jurisdiction": ["EU"],
            "frequency": "event_driven",
            "scale_threshold": "all",
            "deadline": "Before establishing business relationship; ongoing monitoring",
            "legal_source": {"name": "AMLD6 / 6th Anti-Money Laundering Directive", "url": "https://eur-lex.europa.eu/eli/dir/2018/1673", "article": "Art. 3–14 AMLD6"},
            "validation_method": "CDD file completeness audit; SAR register review"
        }
    },
    {
        "id": "T-COMP-0081",
        "name": "Whistleblower Channel (EU Directive)",
        "name_en": "Whistleblower Protection — Internal Reporting Channel (EU)",
        "domain": "D-LEG",
        "description": "Establish and maintain a secure internal whistleblower reporting channel for breaches of EU law. Mandatory for organisations with 50+ employees. Reports must be acknowledged within 7 days and follow-up provided within 3 months.",
        "cause": {
            "trigger": "Mandatory from 17 December 2023 (50+ employees); from 17 December 2021 (250+ employees)",
            "business_need": "EU Whistleblower Directive 2019/1937; national implementation laws",
            "upstream_tasks": []
        },
        "effect": {
            "output": "Functioning secure reporting channel; written procedures; designated responsible person",
            "downstream_tasks": []
        },
        "state_inputs": ["reporting channel (secure email, platform, or hotline)", "designated handler"],
        "state_outputs": ["acknowledgment to reporter within 7 days", "feedback within 3 months"],
        "agent_profile": {
            "automatable": "human_only",
            "guardrails": [
                "Reporter identity must be kept strictly confidential",
                "No retaliation against whistleblowers — criminal offence"
            ],
            "escalation_triggers": ["Report received involving senior management", "Report involves financial fraud"]
        },
        "failure": {
            "risk_level": "high",
            "failure_mode": "No reporting channel; retaliation against reporter",
            "business_damage": "National fines (varies: NL €900,000; DE €100,000); criminal liability for retaliation"
        },
        "_compliance": {
            "jurisdiction": ["EU"],
            "frequency": "event_driven",
            "scale_threshold": "50 FTE",
            "deadline": "Channel must be established; reports acknowledged within 7 days",
            "legal_source": {"name": "EU Whistleblower Directive", "url": "https://eur-lex.europa.eu/eli/dir/2019/1937", "article": "Art. 8–9, 21 Dir. 2019/1937"},
            "validation_method": "Channel accessible and tested; response log maintained"
        }
    },
    {
        "id": "T-COMP-0082",
        "name": "E-Commerce Consumer Rights Compliance",
        "name_en": "E-Commerce — Consumer Rights and Right of Withdrawal (EU)",
        "domain": "D-LEG",
        "description": "B2C online sellers must provide mandatory pre-contract information, a 14-day right of withdrawal, and conformity guarantees on goods (2 years). T&Cs must be clear and compliant with the Consumer Rights Directive. Dark patterns are prohibited under the Digital Services Act.",
        "cause": {
            "trigger": "Annual review of T&Cs; immediately when selling to consumers online",
            "business_need": "Consumer Rights Directive 2011/83/EU; Omnibus Directive 2019/2161",
            "upstream_tasks": []
        },
        "effect": {
            "output": "Compliant T&Cs; correct withdrawal form; 2-year guarantee language",
            "downstream_tasks": []
        },
        "state_inputs": ["website T&Cs", "checkout flow", "return policy"],
        "state_outputs": ["compliant T&Cs published", "withdrawal form available"],
        "agent_profile": {
            "automatable": "ask_first",
            "guardrails": [
                "Never use pre-ticked consent boxes or hidden costs",
                "Always show total price including VAT and delivery before checkout"
            ],
            "escalation_triggers": ["Customer disputes right of withdrawal", "Consumer authority inquiry"]
        },
        "failure": {
            "risk_level": "medium",
            "failure_mode": "Missing withdrawal form; hidden charges; non-compliant T&Cs",
            "business_damage": "Withdrawal period extended to 12 months; national fines up to 4% of annual turnover (Omnibus)"
        },
        "_compliance": {
            "jurisdiction": ["EU"],
            "frequency": "yearly",
            "scale_threshold": "all",
            "deadline": "Ongoing; annual review of T&Cs",
            "legal_source": {"name": "Consumer Rights Directive / Omnibus Directive", "url": "https://eur-lex.europa.eu/eli/dir/2011/83", "article": "Art. 6, 9, 14 Dir. 2011/83"},
            "validation_method": "Legal review of T&Cs; mystery shopper checkout test"
        }
    },

    # ── GERMANY — AANVULLING ──────────────────────────────────────

    {
        "id": "T-COMP-0090",
        "name": "Verpackungsgesetz-Registrierung (LUCID)",
        "name_en": "Packaging Act Registration (Germany — LUCID)",
        "domain": "D-LEG",
        "description": "Unternehmen, die mit Ware befüllte Verpackungen in Deutschland in Umlauf bringen, müssen sich im LUCID-Verpackungsregister anmelden und lizenzpflichtige Verpackungen bei einem dualen System lizenzieren. Gilt auch für ausländische Onlinehändler, die an deutsche Endkunden liefern.",
        "cause": {
            "trigger": "Vor Inverkehrbringen der ersten Verpackung; jährliche Mengenmeldung bis 15. Mai",
            "business_need": "Verpackungsgesetz (VerpackG); Produktverantwortung des Erstinverkehrbringers",
            "upstream_tasks": []
        },
        "effect": {
            "output": "LUCID-Registrierung; Lizenznummer; jährliche Mengenmeldung",
            "downstream_tasks": []
        },
        "state_inputs": ["Verpackungsmengen nach Material", "LUCID-Zugangsdaten"],
        "state_outputs": ["LUCID-Registrierungsbestätigung", "Mengenmeldung"],
        "agent_profile": {
            "automatable": "notify",
            "guardrails": ["Keine Verpackungen in Verkehr bringen vor LUCID-Registrierung"],
            "escalation_triggers": ["Neue Verpackungsmaterialien", "Überschreitung der Mengenschwellen"]
        },
        "failure": {
            "risk_level": "high",
            "failure_mode": "Fehlende LUCID-Registrierung; fehlende Mengenmeldung",
            "business_damage": "Bußgeld bis €200.000; Abmahnungen durch Mitbewerber; Vertriebsverbot"
        },
        "_compliance": {
            "jurisdiction": ["DE"],
            "frequency": "yearly",
            "scale_threshold": "all",
            "deadline": "Registrierung vor Inverkehrbringen; Mengenmeldung 15. Mai",
            "legal_source": {"name": "VerpackG", "url": "https://www.verpackungsgesetz.de/", "article": "§ 9 VerpackG"},
            "validation_method": "LUCID-Registrierungsnummer; Lizenzvertrag duales System"
        }
    },
    {
        "id": "T-COMP-0091",
        "name": "Datenschutzbeauftragter benennen",
        "name_en": "Data Protection Officer Appointment (Germany)",
        "domain": "D-LEG",
        "description": "Unternehmen mit mindestens 20 Personen, die regelmäßig mit der automatisierten Verarbeitung personenbezogener Daten beschäftigt sind, müssen einen Datenschutzbeauftragten (DSB) benennen. Der DSB kann intern oder extern sein und muss bei der Aufsichtsbehörde gemeldet werden.",
        "cause": {
            "trigger": "Wenn die Grenze von 20 automatisiert verarbeitenden Personen überschritten wird; oder bei Verarbeitung sensibler Daten",
            "business_need": "§ 38 BDSG (strengere nationale Regel als AVG); Nichtbenennung ist Ordnungswidrigkeit",
            "upstream_tasks": []
        },
        "effect": {
            "output": "Schriftliche Benennung DSB; Meldung an Landesaufsichtsbehörde",
            "downstream_tasks": []
        },
        "state_inputs": ["Anzahl verarbeitender Personen", "Art der verarbeiteten Daten"],
        "state_outputs": ["Benennungsschreiben", "Kontaktdaten DSB auf Website"],
        "agent_profile": {
            "automatable": "human_only",
            "guardrails": ["DSB muss fachlich geeignet und zuverlässig sein; kein Interessenkonflikt"],
            "escalation_triggers": ["DSB kündigt Mandat", "Aufsichtsbehörde fordert Nachweis"]
        },
        "failure": {
            "risk_level": "high",
            "failure_mode": "Fehlende Benennung trotz Pflicht",
            "business_damage": "Bußgeld bis €50.000 (§ 43 BDSG); Haftung des Unternehmens"
        },
        "_compliance": {
            "jurisdiction": ["DE"],
            "frequency": "event_driven",
            "scale_threshold": "20 FTE",
            "deadline": "Unverzüglich nach Überschreiten der Schwelle",
            "legal_source": {"name": "BDSG", "url": "https://www.gesetze-im-internet.de/bdsg_2018/", "article": "§ 38 BDSG"},
            "validation_method": "Benennungsschreiben; Eintrag auf Website; Meldung an LDA"
        }
    },
    {
        "id": "T-COMP-0092",
        "name": "AGB und Widerrufsbelehrung prüfen",
        "name_en": "Terms & Conditions and Right of Withdrawal (Germany — BGB)",
        "domain": "D-LEG",
        "description": "Jährliche rechtliche Prüfung der Allgemeinen Geschäftsbedingungen (AGB) und der Widerrufsbelehrung für B2C-Onlineshops und -dienstleister. Unwirksame AGB-Klauseln führen zur Anwendung des gesetzlichen Standards und ermöglichen Abmahnungen.",
        "cause": {
            "trigger": "Jährliche Prüfung; bei Gesetzesänderungen; nach Abmahnung",
            "business_need": "§§ 305–310 BGB; FernAbsG; abmahnsicher bleiben",
            "upstream_tasks": []
        },
        "effect": {
            "output": "Rechtssichere, aktuelle AGB; konforme Widerrufsbelehrung auf Website",
            "downstream_tasks": []
        },
        "state_inputs": ["aktuelle AGB", "Widerrufsformular", "Impressum"],
        "state_outputs": ["geprüfte AGB", "aktualisierte Website"],
        "agent_profile": {
            "automatable": "human_only",
            "guardrails": ["Nur vom Anwalt freigegebene AGB verwenden"],
            "escalation_triggers": ["Abmahnung eingegangen", "BGH-Urteil ändert AGB-Rechtslage"]
        },
        "failure": {
            "risk_level": "high",
            "failure_mode": "Unwirksame AGB-Klauseln; fehlerhafte Widerrufsbelehrung",
            "business_damage": "Abmahnkosten €1.000–€5.000; Unterlassungsverfügung; Verlängerung des Widerrufsrechts auf 12 Monate"
        },
        "_compliance": {
            "jurisdiction": ["DE"],
            "frequency": "yearly",
            "scale_threshold": "all",
            "deadline": "Jährlich; nach jeder relevanten Gesetzesänderung",
            "legal_source": {"name": "BGB / UWG", "url": "https://www.gesetze-im-internet.de/bgb/", "article": "§§ 305–310 BGB; § 312g BGB"},
            "validation_method": "Anwaltsbestätigung; kein offenes Abmahnverfahren"
        }
    },

    # ── US — AANVULLING ───────────────────────────────────────────

    {
        "id": "T-COMP-0100",
        "name": "BOI Report — FinCEN",
        "name_en": "Beneficial Ownership Information Report (FinCEN / CTA)",
        "domain": "D-LEG",
        "description": "File Beneficial Ownership Information (BOI) with FinCEN under the Corporate Transparency Act. Required for most US LLCs and corporations. Report all beneficial owners (25%+ ownership or substantial control). New companies: within 90 days of formation. Existing companies: by January 1, 2025.",
        "cause": {
            "trigger": "Company formation; changes in beneficial ownership; annually if no changes (voluntary update)",
            "business_need": "Corporate Transparency Act (CTA) effective January 1, 2024; FinCEN anti-money laundering",
            "upstream_tasks": []
        },
        "effect": {
            "output": "FinCEN BOI report filed; FinCEN ID assigned",
            "downstream_tasks": []
        },
        "state_inputs": ["beneficial owner identification (passport/DL)", "company formation documents"],
        "state_outputs": ["FinCEN filing confirmation", "FinCEN ID number"],
        "agent_profile": {
            "automatable": "human_only",
            "guardrails": [
                "Never file with incorrect information — civil and criminal penalties apply",
                "Update within 30 days of any ownership change"
            ],
            "escalation_triggers": ["Ownership change", "New company formed", "Owner becomes senior officer"]
        },
        "failure": {
            "risk_level": "critical",
            "failure_mode": "Failure to file or filing with false information",
            "business_damage": "Civil penalty $591/day (inflation-adjusted); criminal: up to $10,000 fine and 2 years imprisonment"
        },
        "_compliance": {
            "jurisdiction": ["US"],
            "frequency": "event_driven",
            "scale_threshold": "all",
            "deadline": "Existing companies: January 1, 2025; new companies: 90 days from formation; updates: 30 days from change",
            "legal_source": {"name": "Corporate Transparency Act / FinCEN", "url": "https://www.fincen.gov/boi", "article": "31 USC § 5336"},
            "validation_method": "FinCEN filing confirmation number"
        }
    },
    {
        "id": "T-COMP-0101",
        "name": "ACA Employer Mandate (Forms 1094-C / 1095-C)",
        "name_en": "Affordable Care Act Employer Reporting (1094-C / 1095-C)",
        "domain": "D-LEG",
        "description": "Applicable Large Employers (ALEs — 50+ full-time equivalent employees) must offer minimum essential health coverage and file Forms 1094-C and 1095-C with IRS. Distribute 1095-C to employees by January 31. File 1094-C with IRS by March 31 (electronic).",
        "cause": {
            "trigger": "Annual — prior coverage year; triggered at 50 FTE threshold",
            "business_need": "ACA employer mandate; avoid employer shared responsibility payments",
            "upstream_tasks": []
        },
        "effect": {
            "output": "1095-C to each employee; 1094-C filed with IRS",
            "downstream_tasks": []
        },
        "state_inputs": ["monthly employee headcount", "health plan enrollment data", "FTE calculations"],
        "state_outputs": ["1095-C copies", "IRS e-filing confirmation"],
        "agent_profile": {
            "automatable": "notify",
            "guardrails": ["Monitor FTE count monthly — crossing 50 triggers obligation next year"],
            "escalation_triggers": ["Employee declines offered coverage (track for ESRP calculation)", "Workforce size approaching 50 FTE"]
        },
        "failure": {
            "risk_level": "high",
            "failure_mode": "Missing or incorrect 1095-C; failure to offer minimum coverage",
            "business_damage": "$310 per missing/incorrect form; Employer Shared Responsibility Payment $2,970–$4,460 per employee annually"
        },
        "_compliance": {
            "jurisdiction": ["US"],
            "frequency": "yearly",
            "scale_threshold": "50 FTE",
            "deadline": "1095-C to employees: January 31; 1094-C to IRS: March 31 (electronic)",
            "legal_source": {"name": "ACA / IRS", "url": "https://www.irs.gov/affordable-care-act/employers", "article": "IRC § 6055, § 6056"},
            "validation_method": "IRS AIR system submission receipt"
        }
    },
    {
        "id": "T-COMP-0102",
        "name": "ERISA Form 5500 (Retirement Plan)",
        "name_en": "ERISA Annual Report — Form 5500",
        "domain": "D-LEG",
        "description": "Annual reporting for employer-sponsored retirement plans (401k, pension, profit-sharing) with 100+ participants. File Form 5500 with DOL/IRS via EFAST2 system. Plans with fewer than 100 participants may file simplified Form 5500-SF.",
        "cause": {
            "trigger": "7 months after plan year end (typically July 31 for calendar-year plans); extendable to October 15",
            "business_need": "ERISA Title I reporting; DOL and IRS joint enforcement",
            "upstream_tasks": []
        },
        "effect": {
            "output": "Filed Form 5500 via EFAST2",
            "downstream_tasks": []
        },
        "state_inputs": ["plan financial statements", "participant count", "plan administrator records"],
        "state_outputs": ["EFAST2 acknowledgment number"],
        "agent_profile": {
            "automatable": "human_only",
            "guardrails": ["Must be signed by plan administrator (not just payroll)"],
            "escalation_triggers": ["Plan assets exceed $1 million (full audit required)", "Participant count changes from <100 to 100+"]
        },
        "failure": {
            "risk_level": "high",
            "failure_mode": "Late or missing Form 5500",
            "business_damage": "$250/day up to $150,000 per plan (IRS); $10/day up to $1,000 per participant (DOL)"
        },
        "_compliance": {
            "jurisdiction": ["US"],
            "frequency": "yearly",
            "scale_threshold": "1 FTE",
            "deadline": "7 months after plan year end (July 31 for calendar year); extension to October 15",
            "legal_source": {"name": "ERISA / DOL / IRS", "url": "https://www.dol.gov/agencies/ebsa/employers-and-advisers/plan-administration-and-compliance/reporting-and-filing", "article": "ERISA § 101, § 104"},
            "validation_method": "EFAST2 acknowledgment number"
        }
    },
    {
        "id": "T-COMP-0103",
        "name": "FMLA Eligibility and Notice",
        "name_en": "FMLA — Employee Notice and Leave Administration (US)",
        "domain": "D-LEG",
        "description": "Provide FMLA rights notice to all employees. When an employee requests leave for a qualifying reason, issue eligibility notice within 5 business days and designation notice within 5 business days of receiving sufficient information. Track and document FMLA leave usage.",
        "cause": {
            "trigger": "Employee request for leave (medical, family, military); annual posting requirement",
            "business_need": "Family and Medical Leave Act; DOL Wage and Hour Division enforcement",
            "upstream_tasks": []
        },
        "effect": {
            "output": "Posted FMLA notice; eligibility and designation letters; tracked leave records",
            "downstream_tasks": []
        },
        "state_inputs": ["employee leave request", "12-month FMLA usage tracking", "medical certification"],
        "state_outputs": ["eligibility notice", "designation notice", "leave records"],
        "agent_profile": {
            "automatable": "ask_first",
            "guardrails": [
                "Cannot deny FMLA to eligible employee for qualifying reason",
                "Cannot retaliate against employee for taking FMLA"
            ],
            "escalation_triggers": ["Employee has exhausted 12 weeks", "Employee requests intermittent leave", "Employee requests leave within 12 months of hire"]
        },
        "failure": {
            "risk_level": "high",
            "failure_mode": "Failure to designate FMLA leave; interference with FMLA rights",
            "business_damage": "Back pay + benefits lost + interest; liquidated damages (equal amount); attorney fees; reinstatement"
        },
        "_compliance": {
            "jurisdiction": ["US"],
            "frequency": "event_driven",
            "scale_threshold": "50 FTE",
            "deadline": "Eligibility notice: 5 business days from request; annual poster: always displayed",
            "legal_source": {"name": "FMLA / DOL", "url": "https://www.dol.gov/agencies/whd/fmla", "article": "29 CFR Part 825"},
            "validation_method": "Leave tracking system; designation notices on file"
        }
    },
    {
        "id": "T-COMP-0104",
        "name": "COBRA Continuation Notice",
        "name_en": "COBRA Health Coverage Continuation Notice (US)",
        "domain": "D-LEG",
        "description": "When an employee (or dependent) loses group health coverage due to a qualifying event (termination, reduced hours, divorce, etc.), notify the plan administrator within 30 days and provide the COBRA election notice to qualified beneficiaries within 14 days. Applies to employers with 20+ employees.",
        "cause": {
            "trigger": "Qualifying event: termination (except gross misconduct), hours reduction, divorce, death, Medicare eligibility, dependent status loss",
            "business_need": "ERISA Title I / COBRA (26 USC § 4980B); DOL enforcement",
            "upstream_tasks": []
        },
        "effect": {
            "output": "COBRA election notice sent to qualified beneficiaries",
            "downstream_tasks": []
        },
        "state_inputs": ["employee termination date", "qualifying event type", "plan administrator contact"],
        "state_outputs": ["COBRA election notice with proof of delivery"],
        "agent_profile": {
            "automatable": "notify",
            "guardrails": ["Notice must be sent regardless of whether employee is expected to elect coverage"],
            "escalation_triggers": ["Employee or dependent files COBRA complaint", "DOL investigation"]
        },
        "failure": {
            "risk_level": "high",
            "failure_mode": "Late or missing COBRA notice",
            "business_damage": "$110/day excise tax per qualified beneficiary; DOL civil penalty up to $110/day"
        },
        "_compliance": {
            "jurisdiction": ["US"],
            "frequency": "event_driven",
            "scale_threshold": "20 FTE",
            "deadline": "Employer to plan administrator: 30 days; plan administrator to beneficiaries: 14 days after notification",
            "legal_source": {"name": "COBRA / ERISA", "url": "https://www.dol.gov/sites/dolgov/files/ebsa/about-ebsa/our-activities/resource-center/faqs/cobra-continuation-health-coverage-consumer.pdf", "article": "26 USC § 4980B; ERISA § 601–608"},
            "validation_method": "Certified mail receipt or signed acknowledgment from beneficiary"
        }
    },
]


def main():
    worldmodel_path = Path(__file__).parent.parent / "worldmodel" / "sme_worldmodel_v1.5.json"

    print(f"Loading {worldmodel_path} ...")
    with worldmodel_path.open(encoding="utf-8") as f:
        model = json.load(f)

    existing_ids = {t["id"] for t in model.get("tasks", [])}
    added = 0
    skipped = 0

    for task in TASKS:
        if task["id"] in existing_ids:
            print(f"  SKIP (already exists): {task['id']}")
            skipped += 1
        else:
            model["tasks"].append(task)
            existing_ids.add(task["id"])
            added += 1
            print(f"  ADD: {task['id']} — {task['name_en']}")

    model.setdefault("_meta", {})["compliance_tasks_total"] = sum(
        1 for t in model["tasks"] if t["id"].startswith("T-COMP-")
    )
    model["_meta"]["total_tasks"] = len(model["tasks"])

    print(f"\nWriting {worldmodel_path} ...")
    with worldmodel_path.open("w", encoding="utf-8") as f:
        json.dump(model, f, indent=2, ensure_ascii=False)

    print(f"\nDone. Added {added} tasks ({skipped} skipped). Total: {len(model['tasks'])} tasks.")
    comp_total = model["_meta"]["compliance_tasks_total"]
    print(f"Compliance tasks in model: {comp_total}")


if __name__ == "__main__":
    main()
