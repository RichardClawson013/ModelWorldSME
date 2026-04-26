"""
scripts/generate_compliance_tasks.py

Generates recurring SME compliance tasks for DE, US, and EU jurisdictions
and merges them into sme_worldmodel_v1.5.json.

Sources:
  DE — GewO, BGB, UStG, EStG, GewStG, SGB IV, HGB, DSGVO/BDSG, MiLoG
  US — IRS Title 26, eCFR Title 29 (DOL/FLSA/OSHA), Title 13 (SBA), ADA
  EU — GDPR (2016/679), NIS2 (2022/2555), Late Payment Directive (2011/7),
        CSRD (2022/2464)

Scope: recurring obligations for SMEs (5–250 FTE, turnover < €50M).
One-time startup steps excluded.
"""

import json
from pathlib import Path

TASKS = [
    # ── EUROPEAN UNION ────────────────────────────────────────────

    {
        "id": "T-COMP-0001",
        "name": "GDPR Annual Privacy Review",
        "name_en": "GDPR Annual Privacy Review",
        "domain": "D-LEG",
        "description": "Annual review and update of all data processing activities, privacy notices, data retention schedules, and vendor DPAs to ensure ongoing GDPR compliance.",
        "cause": {
            "trigger": "Annual calendar event — January or after any significant process change",
            "business_need": "Maintain GDPR compliance; avoid supervisory authority audits",
            "upstream_tasks": []
        },
        "effect": {
            "output": "Updated Article 30 register, reviewed privacy notices, confirmed DPAs",
            "downstream_tasks": ["T-COMP-0002", "T-COMP-0003"]
        },
        "state_inputs": ["data processing register", "vendor contracts"],
        "state_outputs": ["updated register", "signed DPAs"],
        "agent_profile": {
            "automatable": "ask_first",
            "guardrails": [
                "Never approve new data processing without human sign-off",
                "Never delete personal data without documented legal basis"
            ],
            "escalation_triggers": [
                "New data processing activity identified",
                "Vendor unable to sign DPA"
            ]
        },
        "failure": {
            "risk_level": "high",
            "failure_mode": "Outdated register; processing without legal basis",
            "business_damage": "Up to €10 million or 2% of global annual turnover (Art. 83(4) GDPR)"
        },
        "_compliance": {
            "jurisdiction": ["EU"],
            "frequency": "yearly",
            "scale_threshold": "all",
            "deadline": "No fixed date; ongoing obligation",
            "legal_source": {"name": "GDPR", "url": "https://eur-lex.europa.eu/eli/reg/2016/679", "article": "Art. 5, 13, 30"},
            "validation_method": "Internal audit checklist; DPA template signed for each vendor"
        }
    },
    {
        "id": "T-COMP-0002",
        "name": "GDPR Data Breach Notification",
        "name_en": "GDPR Data Breach Notification",
        "domain": "D-LEG",
        "description": "Notify the supervisory authority within 72 hours of becoming aware of a personal data breach. If high risk to individuals, also notify those individuals without undue delay.",
        "cause": {
            "trigger": "Discovery of a personal data breach (accidental or unlawful access, loss, disclosure)",
            "business_need": "Legal obligation; minimise regulatory and reputational damage",
            "upstream_tasks": []
        },
        "effect": {
            "output": "Breach notification to DPA; individual notifications if high risk",
            "downstream_tasks": []
        },
        "state_inputs": ["incident log", "breach assessment"],
        "state_outputs": ["DPA notification", "individual notifications"],
        "agent_profile": {
            "automatable": "human_only",
            "guardrails": [
                "Never delay notification beyond 72 hours from discovery",
                "Never file notification without DPO or legal review"
            ],
            "escalation_triggers": ["Any suspected personal data breach"]
        },
        "failure": {
            "risk_level": "critical",
            "failure_mode": "Late or missing notification to supervisory authority",
            "business_damage": "Up to €10 million or 2% of global annual turnover (Art. 83(4) GDPR)"
        },
        "_compliance": {
            "jurisdiction": ["EU"],
            "frequency": "event_driven",
            "scale_threshold": "all",
            "deadline": "72 hours from discovery",
            "legal_source": {"name": "GDPR", "url": "https://eur-lex.europa.eu/eli/reg/2016/679", "article": "Art. 33–34"},
            "validation_method": "Incident log timestamp vs. notification timestamp"
        }
    },
    {
        "id": "T-COMP-0003",
        "name": "GDPR Data Subject Request",
        "name_en": "GDPR Data Subject Request",
        "domain": "D-LEG",
        "description": "Respond to requests from individuals to access, correct, delete, or port their personal data. Response must be provided within one calendar month, extendable by two months for complex requests.",
        "cause": {
            "trigger": "Incoming request from a data subject (email, letter, web form)",
            "business_need": "Legal obligation under GDPR rights chapter",
            "upstream_tasks": []
        },
        "effect": {
            "output": "Written response with requested data or documented refusal with reason",
            "downstream_tasks": []
        },
        "state_inputs": ["subject identity verification", "data inventory"],
        "state_outputs": ["response letter or data export"],
        "agent_profile": {
            "automatable": "ask_first",
            "guardrails": [
                "Never release personal data of a third party in response to a subject request",
                "Always verify identity before processing"
            ],
            "escalation_triggers": ["Request involves sensitive data categories", "Request from a lawyer or DPA"]
        },
        "failure": {
            "risk_level": "high",
            "failure_mode": "Non-response or delayed response to subject access request",
            "business_damage": "Up to €20 million or 4% of global annual turnover (Art. 83(5) GDPR)"
        },
        "_compliance": {
            "jurisdiction": ["EU"],
            "frequency": "event_driven",
            "scale_threshold": "all",
            "deadline": "1 calendar month from receipt",
            "legal_source": {"name": "GDPR", "url": "https://eur-lex.europa.eu/eli/reg/2016/679", "article": "Art. 15–22"},
            "validation_method": "Logged receipt date vs. response date; response on file"
        }
    },
    {
        "id": "T-COMP-0004",
        "name": "NIS2 Cybersecurity Risk Assessment",
        "name_en": "NIS2 Cybersecurity Risk Assessment",
        "domain": "D-LEG",
        "description": "Annual cybersecurity risk assessment and management measures for medium and large SMEs in sectors covered by NIS2 (energy, transport, health, digital infrastructure, etc.). Management personally liable for non-compliance.",
        "cause": {
            "trigger": "Annual — or after a significant IT incident or infrastructure change",
            "business_need": "Legal obligation for medium entities (50-250 FTE or turnover €10M-€50M) in covered sectors",
            "upstream_tasks": []
        },
        "effect": {
            "output": "Risk register, security policy, incident response plan, supply chain security review",
            "downstream_tasks": []
        },
        "state_inputs": ["IT asset inventory", "previous risk register"],
        "state_outputs": ["updated risk register", "security measures documentation"],
        "agent_profile": {
            "automatable": "ask_first",
            "guardrails": ["Never approve new IT vendors without security assessment"],
            "escalation_triggers": ["Significant cybersecurity incident must be reported to national CSIRT within 24h"]
        },
        "failure": {
            "risk_level": "high",
            "failure_mode": "Missing risk management measures; unreported incidents",
            "business_damage": "Up to €7 million or 1.4% of global turnover for essential entities"
        },
        "_compliance": {
            "jurisdiction": ["EU"],
            "frequency": "yearly",
            "scale_threshold": "50 FTE",
            "deadline": "Ongoing; incident reports within 24h (early warning) and 72h (full report)",
            "legal_source": {"name": "NIS2 Directive", "url": "https://eur-lex.europa.eu/eli/dir/2022/2555", "article": "Art. 21, 23"},
            "validation_method": "Risk register reviewed by management; test of incident response procedure"
        }
    },
    {
        "id": "T-COMP-0005",
        "name": "EU Late Payment Compliance Check",
        "name_en": "EU Late Payment Compliance Check",
        "domain": "D-LEG",
        "description": "Ensure that payment terms in B2B contracts do not exceed 60 days (30 days for public authorities) and that statutory interest is automatically applied to overdue invoices. Review standard contract templates quarterly.",
        "cause": {
            "trigger": "Quarterly review of contract templates; or when drafting a new B2B contract",
            "business_need": "Protect cash flow; avoid unenforceable payment terms",
            "upstream_tasks": []
        },
        "effect": {
            "output": "Compliant contract templates; overdue invoice interest notices sent",
            "downstream_tasks": []
        },
        "state_inputs": ["contract templates", "overdue invoice list"],
        "state_outputs": ["updated templates", "interest claim letters"],
        "agent_profile": {
            "automatable": "notify",
            "guardrails": ["Never agree to payment terms exceeding 60 days without legal sign-off"],
            "escalation_triggers": ["Payment terms requested above 60 days"]
        },
        "failure": {
            "risk_level": "medium",
            "failure_mode": "Unenforceable contract terms; unclaimed statutory interest",
            "business_damage": "Loss of statutory interest (currently 8% above ECB rate); reputational risk"
        },
        "_compliance": {
            "jurisdiction": ["EU"],
            "frequency": "quarterly",
            "scale_threshold": "all",
            "deadline": "Ongoing — contract review quarterly",
            "legal_source": {"name": "Late Payment Directive", "url": "https://eur-lex.europa.eu/eli/dir/2011/7", "article": "Art. 3–4"},
            "validation_method": "Random audit of 10 contracts for payment term compliance"
        }
    },
    {
        "id": "T-COMP-0006",
        "name": "CSRD Sustainability Reporting",
        "name_en": "CSRD Sustainability Reporting",
        "domain": "D-LEG",
        "description": "Annual sustainability report according to European Sustainability Reporting Standards (ESRS). Mandatory from 2025 for large companies; SMEs listed on regulated markets required from 2026. Value chain SMEs face indirect pressure from large customers.",
        "cause": {
            "trigger": "Financial year end; or when major customer requests ESG data",
            "business_need": "Legal compliance for in-scope companies; commercial necessity for supply chain SMEs",
            "upstream_tasks": []
        },
        "effect": {
            "output": "Sustainability statement included in management report",
            "downstream_tasks": []
        },
        "state_inputs": ["energy consumption data", "emissions data", "social KPIs"],
        "state_outputs": ["ESRS-compliant sustainability statement"],
        "agent_profile": {
            "automatable": "ask_first",
            "guardrails": ["Never publish sustainability claims without supporting data"],
            "escalation_triggers": ["Customer requests third-party verified ESG report"]
        },
        "failure": {
            "risk_level": "medium",
            "failure_mode": "Missing or inaccurate sustainability report",
            "business_damage": "Exclusion from public contracts; loss of large customers; regulatory fines (national)"
        },
        "_compliance": {
            "jurisdiction": ["EU"],
            "frequency": "yearly",
            "scale_threshold": "250 FTE",
            "deadline": "Same deadline as annual financial report",
            "legal_source": {"name": "CSRD", "url": "https://eur-lex.europa.eu/eli/dir/2022/2464", "article": "Art. 19a"},
            "validation_method": "Third-party assurance (limited assurance from 2026, reasonable from 2028)"
        }
    },

    # ── GERMANY ───────────────────────────────────────────────────

    {
        "id": "T-COMP-0010",
        "name": "Umsatzsteuer-Voranmeldung",
        "name_en": "VAT Advance Return (Germany)",
        "domain": "D-LEG",
        "description": "Monatliche oder vierteljährliche Voranmeldung der Umsatzsteuer beim Finanzamt (ELSTER). Für Unternehmen mit Vorjahres-Zahllast > €7.500 monatlich; darunter vierteljährlich; unter €1.000 jährlich.",
        "cause": {
            "trigger": "10. des Folgemonats (monatlich) oder 10. des Folgequartals (vierteljährlich)",
            "business_need": "Steuerliche Pflicht; Vermeidung von Säumniszuschlägen",
            "upstream_tasks": []
        },
        "effect": {
            "output": "Elektronisch übermittelte USt-Voranmeldung; Zahlung der Zahllast",
            "downstream_tasks": ["T-COMP-0011"]
        },
        "state_inputs": ["Ausgangsrechnungen", "Eingangsrechnungen", "Vorsteuerbelege"],
        "state_outputs": ["eingereichte Voranmeldung", "Zahlungsbeleg"],
        "agent_profile": {
            "automatable": "ask_first",
            "guardrails": [
                "Nie ohne Prüfung durch Steuerberater einreichen",
                "Zahlung immer mit korrekter Steuernummer"
            ],
            "escalation_triggers": ["Zahllast über €10.000", "Erstattungsanspruch über €5.000"]
        },
        "failure": {
            "risk_level": "high",
            "failure_mode": "Verspätete Abgabe oder Zahlung",
            "business_damage": "Säumniszuschlag 1% pro Monat; Verspätungszuschlag bis 10% der Steuerschuld (§ 152 AO)"
        },
        "_compliance": {
            "jurisdiction": ["DE"],
            "frequency": "monthly",
            "scale_threshold": "all",
            "deadline": "10. des Folgemonats (mit Dauerfristverlängerung: 10. des übernächsten Monats)",
            "legal_source": {"name": "UStG", "url": "https://www.gesetze-im-internet.de/ustg_1980/", "article": "§ 18 Abs. 1–2 UStG"},
            "validation_method": "ELSTER-Übertragungsprotokoll; Kontoauszug Finanzamt"
        }
    },
    {
        "id": "T-COMP-0011",
        "name": "Jahresumsatzsteuererklärung",
        "name_en": "Annual VAT Return (Germany)",
        "domain": "D-LEG",
        "description": "Jährliche Umsatzsteuererklärung für das abgelaufene Kalenderjahr, elektronisch via ELSTER.",
        "cause": {
            "trigger": "31. Juli des Folgejahres (ohne Steuerberater); 28./29. Februar des übernächsten Jahres (mit Steuerberater)",
            "business_need": "Jährliche Veranlagungspflicht",
            "upstream_tasks": ["T-COMP-0010"]
        },
        "effect": {
            "output": "Eingereichte Jahreserklärung; Steuerbescheid",
            "downstream_tasks": []
        },
        "state_inputs": ["Voranmeldungen des Jahres", "Jahresbuchhaltung"],
        "state_outputs": ["Jahressteuererklärung", "Steuerbescheid"],
        "agent_profile": {
            "automatable": "human_only",
            "guardrails": ["Immer durch Steuerberater prüfen lassen"],
            "escalation_triggers": ["Abweichung von Voranmeldungen > 5%"]
        },
        "failure": {
            "risk_level": "high",
            "failure_mode": "Fristversäumnis; fehlerhafte Erklärung",
            "business_damage": "Verspätungszuschlag bis 10%; Schätzung durch das Finanzamt (§ 162 AO)"
        },
        "_compliance": {
            "jurisdiction": ["DE"],
            "frequency": "yearly",
            "scale_threshold": "all",
            "deadline": "31. Juli des Folgejahres (verlängerbar bis Februar des übernächsten Jahres mit Steuerberater)",
            "legal_source": {"name": "UStG", "url": "https://www.gesetze-im-internet.de/ustg_1980/", "article": "§ 18 Abs. 3 UStG"},
            "validation_method": "Steuerbescheid als Bestätigung"
        }
    },
    {
        "id": "T-COMP-0012",
        "name": "Gewerbesteuererklärung",
        "name_en": "Trade Tax Return (Germany)",
        "domain": "D-LEG",
        "description": "Jährliche Gewerbesteuererklärung bei der Gemeinde, abzugeben via ELSTER. Gewerbesteuer-Freibetrag €24.500 für Einzelunternehmer und Personengesellschaften.",
        "cause": {
            "trigger": "31. Juli des Folgejahres",
            "business_need": "Steuerliche Pflicht für Gewerbetreibende",
            "upstream_tasks": []
        },
        "effect": {
            "output": "Gewerbesteuererklärung; Bescheid der Gemeinde",
            "downstream_tasks": []
        },
        "state_inputs": ["Jahresabschluss", "steuerlicher Gewinn"],
        "state_outputs": ["Gewerbesteuerbescheid", "Vorauszahlungsplan"],
        "agent_profile": {
            "automatable": "human_only",
            "guardrails": ["Steuerberater muss unterzeichnen"],
            "escalation_triggers": ["Gewerbeertrag über €100.000"]
        },
        "failure": {
            "risk_level": "high",
            "failure_mode": "Fristversäumnis oder fehlerhafte Zerlegung",
            "business_damage": "Verspätungszuschlag; Zinsen auf Nachzahlung (1,8% p.a.)"
        },
        "_compliance": {
            "jurisdiction": ["DE"],
            "frequency": "yearly",
            "scale_threshold": "all",
            "deadline": "31. Juli des Folgejahres",
            "legal_source": {"name": "GewStG", "url": "https://www.gesetze-im-internet.de/gewstg/", "article": "§ 14a GewStG"},
            "validation_method": "Gewerbesteuerbescheid"
        }
    },
    {
        "id": "T-COMP-0013",
        "name": "Körperschaftsteuererklärung (GmbH)",
        "name_en": "Corporate Income Tax Return (Germany — GmbH)",
        "domain": "D-LEG",
        "description": "Jährliche Körperschaftsteuererklärung für GmbHs und UGs. Körperschaftsteuersatz 15% zzgl. Solidaritätszuschlag.",
        "cause": {
            "trigger": "31. Juli des Folgejahres (ohne Steuerberater)",
            "business_need": "Steuerliche Pflicht für Kapitalgesellschaften",
            "upstream_tasks": []
        },
        "effect": {
            "output": "Körperschaftsteuererklärung; Steuerbescheid",
            "downstream_tasks": []
        },
        "state_inputs": ["Jahresabschluss", "Handelsbilanz", "Steuerbilanz"],
        "state_outputs": ["Körperschaftsteuerbescheid"],
        "agent_profile": {
            "automatable": "human_only",
            "guardrails": ["Muss durch Steuerberater erstellt werden"],
            "escalation_triggers": ["Körperschaftsteuer-Vorauszahlung ändert sich um mehr als 20%"]
        },
        "failure": {
            "risk_level": "high",
            "failure_mode": "Fristversäumnis; fehlerhafte Gewinnermittlung",
            "business_damage": "Verspätungszuschlag bis 10%; strafrechtliche Konsequenzen bei Steuerhinterziehung"
        },
        "_compliance": {
            "jurisdiction": ["DE"],
            "frequency": "yearly",
            "scale_threshold": "all",
            "deadline": "31. Juli des Folgejahres",
            "legal_source": {"name": "KStG", "url": "https://www.gesetze-im-internet.de/kstg_1977/", "article": "§ 31 KStG"},
            "validation_method": "Steuerbescheid"
        }
    },
    {
        "id": "T-COMP-0014",
        "name": "Lohnsteuer-Anmeldung",
        "name_en": "Payroll Tax Return (Germany)",
        "domain": "D-LEG",
        "description": "Monatliche Anmeldung und Abführung der einbehaltenen Lohnsteuer, Solidaritätszuschlag und Kirchensteuer für alle Mitarbeiter via ELSTER.",
        "cause": {
            "trigger": "10. des Folgemonats nach Lohnzahlung",
            "business_need": "Pflicht des Arbeitgebers; Abführung der einbehaltenen Steuern",
            "upstream_tasks": []
        },
        "effect": {
            "output": "Elektronische Lohnsteuer-Anmeldung; Überweisung ans Finanzamt",
            "downstream_tasks": []
        },
        "state_inputs": ["Lohnabrechnungen des Monats", "Steuer-IDs der Mitarbeiter"],
        "state_outputs": ["Anmeldung", "Zahlungsbeleg"],
        "agent_profile": {
            "automatable": "notify",
            "guardrails": ["Niemals Lohnsteuer einbehalten aber nicht abführen"],
            "escalation_triggers": ["Mitarbeiter mit Sonderlohnsteuersatz", "Kurzarbeitergeld-Monate"]
        },
        "failure": {
            "risk_level": "critical",
            "failure_mode": "Nicht-Abführung der Lohnsteuer",
            "business_damage": "Strafbarkeit wegen Lohnsteuerhinterziehung (§ 266a StGB); Haftung des Geschäftsführers persönlich"
        },
        "_compliance": {
            "jurisdiction": ["DE"],
            "frequency": "monthly",
            "scale_threshold": "1 FTE",
            "deadline": "10. des Folgemonats",
            "legal_source": {"name": "EStG", "url": "https://www.gesetze-im-internet.de/estg/", "article": "§ 41a EStG"},
            "validation_method": "ELSTER-Protokoll; Kontoauszug"
        }
    },
    {
        "id": "T-COMP-0015",
        "name": "Sozialversicherungsbeiträge abführen",
        "name_en": "Social Security Contributions (Germany)",
        "domain": "D-LEG",
        "description": "Monatliche Abführung der Sozialversicherungsbeiträge (Kranken-, Pflege-, Renten-, Arbeitslosenversicherung) für alle sozialversicherungspflichtigen Mitarbeiter an die jeweilige Krankenkasse.",
        "cause": {
            "trigger": "Drittletzter Bankarbeitstag des laufenden Monats",
            "business_need": "Gesetzliche Arbeitgeberpflicht; Einzug durch Krankenkasse",
            "upstream_tasks": []
        },
        "effect": {
            "output": "SEPA-Überweisung an Krankenkasse; Beitragsnachweis",
            "downstream_tasks": []
        },
        "state_inputs": ["Bruttogehaltsliste", "Beitragssatzliste der Krankenkasse"],
        "state_outputs": ["Zahlungsbeleg", "Beitragsnachweis"],
        "agent_profile": {
            "automatable": "notify",
            "guardrails": ["Nie Fälligkeitsdatum verpassen — Säumniszuschlag sofort"],
            "escalation_triggers": ["Neue Mitarbeiter mid-month", "Beitragsschulden"]
        },
        "failure": {
            "risk_level": "critical",
            "failure_mode": "Verspätete oder fehlende Zahlung",
            "business_damage": "Säumniszuschlag 1% pro Monat; persönliche Haftung des Geschäftsführers (§ 266a StGB)"
        },
        "_compliance": {
            "jurisdiction": ["DE"],
            "frequency": "monthly",
            "scale_threshold": "1 FTE",
            "deadline": "Drittletzter Bankarbeitstag des Monats",
            "legal_source": {"name": "SGB IV", "url": "https://www.gesetze-im-internet.de/sgb_4/", "article": "§ 23 SGB IV"},
            "validation_method": "Kontoauszug; Beitragsnachweis der Krankenkasse"
        }
    },
    {
        "id": "T-COMP-0016",
        "name": "Jahresabschluss einreichen (GmbH)",
        "name_en": "Annual Accounts Filing (Germany — GmbH)",
        "domain": "D-LEG",
        "description": "GmbHs müssen ihren Jahresabschluss beim Bundesanzeiger elektronisch einreichen. Kleinstkapitalgesellschaften können eine verkürzte Bilanz einreichen.",
        "cause": {
            "trigger": "Spätestens 12 Monate nach dem Bilanzstichtag (für Kleinstgesellschaften 15 Monate)",
            "business_need": "Handelsrechtliche Offenlegungspflicht",
            "upstream_tasks": []
        },
        "effect": {
            "output": "Im Bundesanzeiger veröffentlichter Jahresabschluss",
            "downstream_tasks": []
        },
        "state_inputs": ["Jahresabschluss", "Gesellschafterversammlungsprotokoll"],
        "state_outputs": ["Bundesanzeiger-Veröffentlichung"],
        "agent_profile": {
            "automatable": "human_only",
            "guardrails": ["Gesellschafterversammlung muss Abschluss festgestellt haben"],
            "escalation_triggers": ["Frist 6 Monate vor Ablauf erreicht"]
        },
        "failure": {
            "risk_level": "high",
            "failure_mode": "Nicht- oder verspätete Offenlegung",
            "business_damage": "Ordnungsgeld €2.500 bis €25.000 pro Verstoß (§ 335 HGB)"
        },
        "_compliance": {
            "jurisdiction": ["DE"],
            "frequency": "yearly",
            "scale_threshold": "all",
            "deadline": "12 Monate nach Geschäftsjahresende",
            "legal_source": {"name": "HGB", "url": "https://www.gesetze-im-internet.de/hgb/", "article": "§ 325 HGB"},
            "validation_method": "Bundesanzeiger-Abruf"
        }
    },
    {
        "id": "T-COMP-0017",
        "name": "Mindestlohn-Dokumentation",
        "name_en": "Minimum Wage Documentation (Germany)",
        "domain": "D-LEG",
        "description": "Aufzeichnung von Beginn, Ende und Dauer der täglichen Arbeitszeit für Minijobber, kurzfristig Beschäftigte und bestimmte Branchen (MiLoG). Aufbewahrung 2 Jahre.",
        "cause": {
            "trigger": "Täglich; bei jeder Schicht geringfügig Beschäftigter",
            "business_need": "Nachweis der Mindestlohn-Einhaltung; Schutz bei Zollprüfungen",
            "upstream_tasks": []
        },
        "effect": {
            "output": "Unterzeichnete Arbeitszeitaufzeichnungen; Lohnbelege",
            "downstream_tasks": []
        },
        "state_inputs": ["Schichtpläne", "Stempeluhrdaten"],
        "state_outputs": ["Arbeitszeitaufzeichnung"],
        "agent_profile": {
            "automatable": "notify",
            "guardrails": ["Aufzeichnungen müssen spätestens 7 Tage nach Schicht vorliegen"],
            "escalation_triggers": ["Zollkontrolle angekündigt"]
        },
        "failure": {
            "risk_level": "high",
            "failure_mode": "Fehlende oder lückenhafte Aufzeichnungen",
            "business_damage": "Bußgeld bis €500.000 (§ 21 MiLoG); Ausschluss von öffentlichen Aufträgen"
        },
        "_compliance": {
            "jurisdiction": ["DE"],
            "frequency": "monthly",
            "scale_threshold": "1 FTE",
            "deadline": "Täglich; Aufbewahrung 2 Jahre",
            "legal_source": {"name": "MiLoG", "url": "https://www.gesetze-im-internet.de/milog/", "article": "§ 17 MiLoG"},
            "validation_method": "Stichprobenprüfung; Zollkontrolle-Checkliste"
        }
    },
    {
        "id": "T-COMP-0018",
        "name": "Unfallversicherung melden (BG)",
        "name_en": "Accident Insurance Report (Germany — Berufsgenossenschaft)",
        "domain": "D-LEG",
        "description": "Jährliche Lohnnachweis-Meldung an die zuständige Berufsgenossenschaft bis 16. Februar. Bei Arbeitsunfällen mit mehr als 3 Ausfalltagen: Unfallanzeige innerhalb von 3 Tagen.",
        "cause": {
            "trigger": "Jährlich: 16. Februar; bei Unfall: binnen 3 Tagen",
            "business_need": "Pflichtversicherung; Beitragsberechnung; Unfallmeldepflicht",
            "upstream_tasks": []
        },
        "effect": {
            "output": "Lohnnachweismeldung; Beitragsbescheid; ggf. Unfallanzeige",
            "downstream_tasks": []
        },
        "state_inputs": ["Lohnnachweis des Vorjahres", "Unfallprotokoll"],
        "state_outputs": ["BG-Meldung"],
        "agent_profile": {
            "automatable": "notify",
            "guardrails": ["Unfallanzeige niemals verzögern"],
            "escalation_triggers": ["Arbeitsunfall mit Arztbesuch"]
        },
        "failure": {
            "risk_level": "high",
            "failure_mode": "Fehlende Lohnnachweis-Meldung oder Unfallanzeige",
            "business_damage": "Ordnungswidrigkeiten; persönliche Haftung bei Vorsatz"
        },
        "_compliance": {
            "jurisdiction": ["DE"],
            "frequency": "yearly",
            "scale_threshold": "1 FTE",
            "deadline": "16. Februar (Lohnnachweis); 3 Tage (Unfallanzeige)",
            "legal_source": {"name": "SGB VII", "url": "https://www.gesetze-im-internet.de/sgb_7/", "article": "§ 165, § 193 SGB VII"},
            "validation_method": "BG-Quittung; Unfallanzeige-Kopie"
        }
    },
    {
        "id": "T-COMP-0019",
        "name": "Transparenzregister-Meldung",
        "name_en": "Transparency Register Filing (Germany)",
        "domain": "D-LEG",
        "description": "Meldung der wirtschaftlich Berechtigten (Gesellschafter mit mehr als 25% Anteilen oder gleichwertigem Einfluss) an das Transparenzregister. Bei Änderungen: binnen 4 Wochen.",
        "cause": {
            "trigger": "Gesellschafterveränderung; Erstgründung; jährliche Prüfung auf Aktualität",
            "business_need": "Pflicht nach GwG; Geldwäscheprävention",
            "upstream_tasks": []
        },
        "effect": {
            "output": "Aktuelle Eintragung im Transparenzregister",
            "downstream_tasks": []
        },
        "state_inputs": ["Gesellschafterliste", "Handelsregisterauszug"],
        "state_outputs": ["Transparenzregister-Eintrag"],
        "agent_profile": {
            "automatable": "ask_first",
            "guardrails": ["Nur Geschäftsführer oder Notar darf Änderungen melden"],
            "escalation_triggers": ["Gesellschafterveränderung über 25%"]
        },
        "failure": {
            "risk_level": "high",
            "failure_mode": "Fehlende oder veraltete Eintragung",
            "business_damage": "Bußgeld bis €150.000 (§ 56 GwG)"
        },
        "_compliance": {
            "jurisdiction": ["DE"],
            "frequency": "event_driven",
            "scale_threshold": "all",
            "deadline": "4 Wochen nach Änderung",
            "legal_source": {"name": "GwG", "url": "https://www.gesetze-im-internet.de/gwg_2017/", "article": "§ 20 GwG"},
            "validation_method": "Auszug aus dem Transparenzregister"
        }
    },

    # ── UNITED STATES ─────────────────────────────────────────────

    {
        "id": "T-COMP-0030",
        "name": "Federal Quarterly Payroll Tax (Form 941)",
        "name_en": "Federal Quarterly Payroll Tax (Form 941)",
        "domain": "D-LEG",
        "description": "Quarterly filing of Form 941 to report wages paid, federal income tax withheld, and Social Security/Medicare taxes. Deposit schedule (monthly or semi-weekly) determined by lookback period.",
        "cause": {
            "trigger": "End of each calendar quarter (March 31, June 30, September 30, December 31)",
            "business_need": "IRS employer obligation; withholding and FICA tax remittance",
            "upstream_tasks": []
        },
        "effect": {
            "output": "Filed Form 941; tax deposits made per deposit schedule",
            "downstream_tasks": []
        },
        "state_inputs": ["payroll records", "federal tax deposit history"],
        "state_outputs": ["filed Form 941", "deposit confirmation"],
        "agent_profile": {
            "automatable": "ask_first",
            "guardrails": [
                "Never miss a deposit date — penalties start at 2% and escalate to 15%",
                "Always use EFTPS for electronic deposits"
            ],
            "escalation_triggers": ["Tax liability changes significantly vs prior quarter", "Penalty notice received"]
        },
        "failure": {
            "risk_level": "critical",
            "failure_mode": "Late filing or deposit; underreporting",
            "business_damage": "Failure-to-deposit penalty 2–15% of unpaid tax; Trust Fund Recovery Penalty (100% of unpaid taxes) personally assessed on responsible persons"
        },
        "_compliance": {
            "jurisdiction": ["US"],
            "frequency": "quarterly",
            "scale_threshold": "1 FTE",
            "deadline": "Last day of month following quarter end (April 30, July 31, October 31, January 31)",
            "legal_source": {"name": "IRC / IRS", "url": "https://www.irs.gov/forms-pubs/about-form-941", "article": "IRC § 3111, § 3402"},
            "validation_method": "IRS acknowledgment; EFTPS payment confirmation"
        }
    },
    {
        "id": "T-COMP-0031",
        "name": "Federal Unemployment Tax (Form 940)",
        "name_en": "Federal Unemployment Tax Annual Return (FUTA)",
        "domain": "D-LEG",
        "description": "Annual filing of Form 940 to report and pay Federal Unemployment Tax (FUTA) at 6% on first $7,000 of each employee's wages (effective rate 0.6% with state credit). Deposits required if liability exceeds $500 per quarter.",
        "cause": {
            "trigger": "January 31 each year; quarterly deposits if liability > $500",
            "business_need": "IRS employer obligation; funds federal unemployment insurance",
            "upstream_tasks": []
        },
        "effect": {
            "output": "Filed Form 940; FUTA deposits paid",
            "downstream_tasks": []
        },
        "state_inputs": ["annual payroll by employee", "FUTA credit worksheet"],
        "state_outputs": ["filed Form 940"],
        "agent_profile": {
            "automatable": "notify",
            "guardrails": ["Track FUTA liability each quarter to catch $500 threshold"],
            "escalation_triggers": ["State receives a FUTA credit reduction"]
        },
        "failure": {
            "risk_level": "medium",
            "failure_mode": "Late or missing Form 940 filing",
            "business_damage": "5% per month failure-to-file penalty (max 25%); 0.5% per month failure-to-pay"
        },
        "_compliance": {
            "jurisdiction": ["US"],
            "frequency": "yearly",
            "scale_threshold": "1 FTE",
            "deadline": "January 31",
            "legal_source": {"name": "IRS", "url": "https://www.irs.gov/forms-pubs/about-form-940", "article": "IRC § 3301–3311"},
            "validation_method": "IRS acknowledgment; prior-year comparison"
        }
    },
    {
        "id": "T-COMP-0032",
        "name": "W-2 and W-3 Filing",
        "name_en": "W-2 / W-3 Annual Wage Reporting",
        "domain": "D-LEG",
        "description": "Issue W-2 forms to all employees and file W-3 (transmittal) with SSA by January 31. Report wages, tips, and withholdings for prior tax year. Also file electronically with IRS if 10 or more forms.",
        "cause": {
            "trigger": "January 31 — applies to prior tax year wages",
            "business_need": "Employee tax filing dependency; SSA earnings record",
            "upstream_tasks": []
        },
        "effect": {
            "output": "W-2 copies to employees; W-2/W-3 filed with SSA",
            "downstream_tasks": []
        },
        "state_inputs": ["annual payroll records", "employee tax withholding data"],
        "state_outputs": ["W-2 copies", "SSA electronic filing confirmation"],
        "agent_profile": {
            "automatable": "notify",
            "guardrails": ["Never miss January 31 — penalties same-day escalate"],
            "escalation_triggers": ["Corrected W-2c needed for prior year"]
        },
        "failure": {
            "risk_level": "high",
            "failure_mode": "Late or missing W-2 issuance or filing",
            "business_damage": "$60 per form if filed within 30 days late; up to $630 per form for intentional disregard"
        },
        "_compliance": {
            "jurisdiction": ["US"],
            "frequency": "yearly",
            "scale_threshold": "1 FTE",
            "deadline": "January 31",
            "legal_source": {"name": "IRS", "url": "https://www.irs.gov/forms-pubs/about-form-w-2", "article": "IRC § 6051"},
            "validation_method": "SSA acknowledgment number; employee delivery confirmation"
        }
    },
    {
        "id": "T-COMP-0033",
        "name": "1099-NEC Filing",
        "name_en": "1099-NEC / 1099-MISC Filing",
        "domain": "D-LEG",
        "description": "Issue 1099-NEC to independent contractors paid $600 or more during the tax year. File Copy A with IRS by January 31. Also applies to 1099-MISC for rents, prizes, and other income.",
        "cause": {
            "trigger": "January 31 — prior tax year payments to non-employees",
            "business_need": "IRS reporting requirement; contractor tax compliance",
            "upstream_tasks": []
        },
        "effect": {
            "output": "1099-NEC delivered to contractors; filed with IRS",
            "downstream_tasks": []
        },
        "state_inputs": ["contractor payment records", "W-9 forms on file"],
        "state_outputs": ["1099-NEC copies", "IRS filing confirmation"],
        "agent_profile": {
            "automatable": "notify",
            "guardrails": ["Always collect W-9 before first payment to avoid backup withholding"],
            "escalation_triggers": ["Contractor refuses to provide W-9"]
        },
        "failure": {
            "risk_level": "medium",
            "failure_mode": "Missing or late 1099 filing",
            "business_damage": "$60–$630 per form; backup withholding obligation of 24% if no TIN on file"
        },
        "_compliance": {
            "jurisdiction": ["US"],
            "frequency": "yearly",
            "scale_threshold": "all",
            "deadline": "January 31",
            "legal_source": {"name": "IRS", "url": "https://www.irs.gov/forms-pubs/about-form-1099-nec", "article": "IRC § 6041A"},
            "validation_method": "IRS FIRE system acknowledgment"
        }
    },
    {
        "id": "T-COMP-0034",
        "name": "Form I-9 Employment Eligibility",
        "name_en": "Form I-9 Employment Eligibility Verification",
        "domain": "D-LEG",
        "description": "Complete and retain Form I-9 for every new hire to verify identity and employment authorization. Must be completed within 3 business days of start date. Retain for 3 years from hire date or 1 year after termination (whichever is later).",
        "cause": {
            "trigger": "Every new employee hire",
            "business_need": "Federal law — Immigration Reform and Control Act (IRCA)",
            "upstream_tasks": []
        },
        "effect": {
            "output": "Completed, signed Form I-9 on file",
            "downstream_tasks": []
        },
        "state_inputs": ["new hire start date", "identity documents provided by employee"],
        "state_outputs": ["completed I-9 form"],
        "agent_profile": {
            "automatable": "human_only",
            "guardrails": [
                "Never accept expired documents",
                "Never ask for more or different documents than required"
            ],
            "escalation_triggers": ["Employee unable to provide valid documents within 3 days"]
        },
        "failure": {
            "risk_level": "high",
            "failure_mode": "Missing or improperly completed I-9; retention failure",
            "business_damage": "$281–$2,789 per paperwork violation; $698–$27,894 per knowingly hired unauthorized worker"
        },
        "_compliance": {
            "jurisdiction": ["US"],
            "frequency": "event_driven",
            "scale_threshold": "1 FTE",
            "deadline": "3 business days from start date",
            "legal_source": {"name": "IRCA / USCIS", "url": "https://www.uscis.gov/i-9", "article": "8 USC § 1324a"},
            "validation_method": "Annual I-9 audit against current employee list"
        }
    },
    {
        "id": "T-COMP-0035",
        "name": "OSHA 300 Log Posting",
        "name_en": "OSHA 300 Log Annual Posting and Submission",
        "domain": "D-LEG",
        "description": "Maintain OSHA Form 300 (injury and illness log) throughout the year. Post Form 300A summary in the workplace February 1 through April 30. Electronically submit data to OSHA if 20–249 employees in high-hazard industries, or 250+ employees in any industry.",
        "cause": {
            "trigger": "February 1 (posting); March 2 (electronic submission for covered employers)",
            "business_need": "OSHA recordkeeping and reporting requirement",
            "upstream_tasks": []
        },
        "effect": {
            "output": "Form 300A posted; electronic submission to OSHA Injury Tracking Application (ITA)",
            "downstream_tasks": []
        },
        "state_inputs": ["workplace injury and illness records"],
        "state_outputs": ["posted Form 300A", "ITA submission confirmation"],
        "agent_profile": {
            "automatable": "notify",
            "guardrails": ["Record work-related injuries within 7 days of occurrence"],
            "escalation_triggers": ["Fatality or hospitalization of 3+ employees — report to OSHA within 8 hours"]
        },
        "failure": {
            "risk_level": "high",
            "failure_mode": "Failure to post, record, or submit",
            "business_damage": "Up to $16,131 per serious violation; up to $161,323 per willful or repeated violation"
        },
        "_compliance": {
            "jurisdiction": ["US"],
            "frequency": "yearly",
            "scale_threshold": "11 FTE",
            "deadline": "February 1 (posting); March 2 (electronic submission)",
            "legal_source": {"name": "OSHA", "url": "https://www.osha.gov/recordkeeping", "article": "29 CFR 1904"},
            "validation_method": "Posted form in workplace; ITA submission receipt"
        }
    },
    {
        "id": "T-COMP-0036",
        "name": "Federal Business Income Tax Quarterly Estimate",
        "name_en": "Federal Quarterly Estimated Income Tax (US)",
        "domain": "D-LEG",
        "description": "Quarterly estimated tax payments for self-employed individuals (Schedule C), S-Corp shareholders, and partnership members. Required if expected tax liability exceeds $1,000 for the year.",
        "cause": {
            "trigger": "April 15, June 15, September 15, January 15 of following year",
            "business_need": "Pay-as-you-go tax obligation; avoid underpayment penalty",
            "upstream_tasks": []
        },
        "effect": {
            "output": "Form 1040-ES payment submitted; payment confirmation",
            "downstream_tasks": []
        },
        "state_inputs": ["projected annual income", "prior year tax liability"],
        "state_outputs": ["quarterly payment confirmation"],
        "agent_profile": {
            "automatable": "ask_first",
            "guardrails": ["Safe harbor: pay 100% of prior year tax or 90% of current year tax"],
            "escalation_triggers": ["Income varies significantly from prior year projection"]
        },
        "failure": {
            "risk_level": "medium",
            "failure_mode": "Underpayment of estimated taxes",
            "business_damage": "Underpayment penalty (current rate ~8% annualized on shortfall)"
        },
        "_compliance": {
            "jurisdiction": ["US"],
            "frequency": "quarterly",
            "scale_threshold": "all",
            "deadline": "April 15, June 15, September 15, January 15",
            "legal_source": {"name": "IRS", "url": "https://www.irs.gov/businesses/small-businesses-self-employed/estimated-taxes", "article": "IRC § 6654"},
            "validation_method": "IRS EFTPS payment history"
        }
    },
    {
        "id": "T-COMP-0037",
        "name": "State Sales Tax Return",
        "name_en": "State Sales Tax Return (US)",
        "domain": "D-LEG",
        "description": "Monthly or quarterly filing of state sales tax returns for taxable goods and services sold. Filing frequency determined by sales volume. Economic nexus thresholds (post-Wayfair) require filing in states where $100,000 in sales or 200 transactions occur annually.",
        "cause": {
            "trigger": "Monthly or quarterly based on sales volume; nexus established in a new state",
            "business_need": "State tax obligation; economic nexus compliance post-Wayfair",
            "upstream_tasks": []
        },
        "effect": {
            "output": "Filed state sales tax return; remittance paid",
            "downstream_tasks": []
        },
        "state_inputs": ["sales by state", "exemption certificates on file"],
        "state_outputs": ["filed return", "payment confirmation per state"],
        "agent_profile": {
            "automatable": "notify",
            "guardrails": ["Monitor nexus thresholds monthly for all states"],
            "escalation_triggers": ["New state threshold reached", "State audit notice received"]
        },
        "failure": {
            "risk_level": "high",
            "failure_mode": "Failure to collect or remit sales tax",
            "business_damage": "Back taxes plus interest and penalties; personal liability in some states"
        },
        "_compliance": {
            "jurisdiction": ["US"],
            "frequency": "monthly",
            "scale_threshold": "all",
            "deadline": "Varies by state; typically 20th of following month",
            "legal_source": {"name": "South Dakota v. Wayfair / State Revenue Codes", "url": "https://www.streamlinedsalestax.org/", "article": "Economic nexus laws (all 45 sales tax states)"},
            "validation_method": "State portal filing confirmation; nexus tracker report"
        }
    },
    {
        "id": "T-COMP-0038",
        "name": "Workers Compensation Insurance Renewal",
        "name_en": "Workers' Compensation Insurance Annual Renewal",
        "domain": "D-LEG",
        "description": "Annual renewal of workers' compensation insurance for all employees. Required in 48 of 50 US states. Payroll audit by insurer determines final premium. Maintain certificates of insurance for all work sites.",
        "cause": {
            "trigger": "Annual policy expiration date; new hire triggers certificate update",
            "business_need": "State legal requirement; employee injury coverage",
            "upstream_tasks": []
        },
        "effect": {
            "output": "Renewed policy certificate; payroll audit submitted",
            "downstream_tasks": []
        },
        "state_inputs": ["payroll records", "prior year claims history", "employee count by job class"],
        "state_outputs": ["renewed policy", "certificate of insurance"],
        "agent_profile": {
            "automatable": "notify",
            "guardrails": ["Never allow a lapse in coverage — work must stop if uninsured"],
            "escalation_triggers": ["Claim filed", "Premium increase >20%"]
        },
        "failure": {
            "risk_level": "critical",
            "failure_mode": "Lapse in coverage",
            "business_damage": "Stop-work orders; personal liability for injured employee medical costs; fines up to $10,000+ per state"
        },
        "_compliance": {
            "jurisdiction": ["US"],
            "frequency": "yearly",
            "scale_threshold": "1 FTE",
            "deadline": "Policy renewal date (typically annual)",
            "legal_source": {"name": "State Workers' Compensation Acts", "url": "https://www.dol.gov/agencies/owcp", "article": "Varies by state"},
            "validation_method": "Certificate of insurance on file; payroll audit complete"
        }
    },
    {
        "id": "T-COMP-0039",
        "name": "FLSA Wage Record Maintenance",
        "name_en": "FLSA Payroll Record Maintenance",
        "domain": "D-LEG",
        "description": "Maintain payroll records for all employees for at least 3 years: hours worked, wages paid, overtime, deductions. Retain all records that explain wage computations for 2 years. Non-exempt employees must be paid overtime (1.5×) for hours over 40 per week.",
        "cause": {
            "trigger": "Ongoing — each pay period; triggered by DOL investigation",
            "business_need": "FLSA compliance; wage and hour dispute defense",
            "upstream_tasks": []
        },
        "effect": {
            "output": "Maintained payroll records (paper or digital)",
            "downstream_tasks": []
        },
        "state_inputs": ["timesheets", "pay stubs", "exemption classifications"],
        "state_outputs": ["archived payroll records"],
        "agent_profile": {
            "automatable": "notify",
            "guardrails": [
                "Never round time in a way that consistently benefits the employer",
                "Review exempt classifications annually"
            ],
            "escalation_triggers": ["Employee files wage complaint", "DOL audit initiated"]
        },
        "failure": {
            "risk_level": "high",
            "failure_mode": "Missing records; misclassification; unpaid overtime",
            "business_damage": "Back wages + equal amount in liquidated damages + attorney fees; up to $10,000 per child labor violation"
        },
        "_compliance": {
            "jurisdiction": ["US"],
            "frequency": "monthly",
            "scale_threshold": "1 FTE",
            "deadline": "Ongoing; records retained 3 years",
            "legal_source": {"name": "FLSA / DOL", "url": "https://www.dol.gov/agencies/whd/flsa", "article": "29 CFR Part 516"},
            "validation_method": "Annual records audit against current employee list"
        }
    },
    {
        "id": "T-COMP-0040",
        "name": "EEO-1 Component 1 Report",
        "name_en": "EEO-1 Component 1 Annual Workforce Data Report",
        "domain": "D-LEG",
        "description": "Annual filing of workforce data by race/ethnicity, sex, and job category for employers with 100+ employees, or federal contractors with 50+ employees and $50,000+ in contracts. Filed with EEOC via online portal.",
        "cause": {
            "trigger": "Annual; filing window typically opens January and closes in March/April",
            "business_need": "EEOC data collection for enforcement and research",
            "upstream_tasks": []
        },
        "effect": {
            "output": "Filed EEO-1 data via EEOC portal",
            "downstream_tasks": []
        },
        "state_inputs": ["employee demographic data", "job classification codes"],
        "state_outputs": ["EEOC portal submission confirmation"],
        "agent_profile": {
            "automatable": "ask_first",
            "guardrails": ["Data must be collected voluntarily — cannot require employees to self-identify"],
            "escalation_triggers": ["First year of crossing 100-employee threshold"]
        },
        "failure": {
            "risk_level": "medium",
            "failure_mode": "Missing or late filing",
            "business_damage": "Court order to compel filing; reputational risk; scrutiny in discrimination investigations"
        },
        "_compliance": {
            "jurisdiction": ["US"],
            "frequency": "yearly",
            "scale_threshold": "100 FTE",
            "deadline": "Typically March–April (varies annually)",
            "legal_source": {"name": "EEOC / Title VII", "url": "https://www.eeoc.gov/employers/eeo-1-data-collection", "article": "42 USC § 2000e-8(c)"},
            "validation_method": "EEOC portal submission receipt"
        }
    },
    {
        "id": "T-COMP-0041",
        "name": "ADA Website Accessibility Audit",
        "name_en": "ADA / Section 508 Website Accessibility Compliance",
        "domain": "D-LEG",
        "description": "Annual audit of business website and digital tools for WCAG 2.1 Level AA compliance. Courts have held that public-facing websites are places of public accommodation under ADA Title III. High-risk areas: missing alt text, inaccessible forms, no keyboard navigation.",
        "cause": {
            "trigger": "Annual review; or after major website update",
            "business_need": "ADA Title III compliance; avoid demand letters and litigation",
            "upstream_tasks": []
        },
        "effect": {
            "output": "Accessibility audit report; remediation plan",
            "downstream_tasks": []
        },
        "state_inputs": ["website URL list", "prior audit report"],
        "state_outputs": ["WCAG compliance report"],
        "agent_profile": {
            "automatable": "ask_first",
            "guardrails": ["Prioritise form and checkout page accessibility first"],
            "escalation_triggers": ["ADA demand letter received"]
        },
        "failure": {
            "risk_level": "medium",
            "failure_mode": "Inaccessible website; non-compliant digital tools",
            "business_damage": "ADA Title III lawsuit settlements typically $25,000–$100,000; serial plaintiff litigation"
        },
        "_compliance": {
            "jurisdiction": ["US"],
            "frequency": "yearly",
            "scale_threshold": "all",
            "deadline": "No fixed date; annual best practice",
            "legal_source": {"name": "ADA Title III", "url": "https://www.ada.gov/resources/web-guidance/", "article": "42 USC § 12181"},
            "validation_method": "Automated scan (axe, WAVE) + manual keyboard navigation test"
        }
    },
]


def main():
    worldmodel_path = Path(__file__).parent.parent / "worldmodel" / "sme_worldmodel_v1.5.json"
    output_path = worldmodel_path  # overwrite in place

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

    # Update metadata
    model.setdefault("_meta", {})["compliance_tasks_added"] = added
    model["_meta"]["total_tasks"] = len(model["tasks"])

    print(f"\nWriting {output_path} ...")
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(model, f, indent=2, ensure_ascii=False)

    print(f"\nDone. Added {added} compliance tasks ({skipped} skipped). Total: {len(model['tasks'])} tasks.")


if __name__ == "__main__":
    main()
