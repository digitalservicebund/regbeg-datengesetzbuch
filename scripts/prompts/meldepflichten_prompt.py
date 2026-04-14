"""
meldepflichten_prompt.py

Configuration and prompts for extract_meldepflichten_llm.py.
Organized into a separate file for better readability and type safety.
"""

from enum import Enum
from typing import List, Never, assert_never
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Categories as Source of Truth (Enums)
# ---------------------------------------------------------------------------

class ArtDerPflicht(str, Enum):
    # Informationspflichten
    Meldepflicht = "Meldepflicht"
    Benachrichtigungspflicht = "Benachrichtigungspflicht"
    Auskunftspflicht = "Auskunftspflicht"
    Berichtspflicht = "Berichtspflicht"
    # Verfahrenspflichten
    Registrierungspflicht = "Registrierungspflicht"
    Mitwirkungspflicht = "Mitwirkungspflicht"
    # Daten- oder Zugangsbereitstellung
    Bereitstellungspflicht = "Bereitstellungspflicht"
    # Governancepflichten
    Dokumentationspflicht = "Dokumentationspflicht"
    Prüfpflicht = "Prüfpflicht"
    Benennungspflicht = "Benennungspflicht"
    # Transparenzpflichten
    Veröffentlichungspflicht = "Veröffentlichungspflicht"
    # Andere
    SonstigePflicht = "Sonstige Pflicht"

class Wer(str, Enum):
    Unternehmen = "Unternehmen / Wirtschaft"
    KRITIS = "Betreiber kritischer Infrastrukturen (KRITIS)"
    Verantwortlicher = "Verantwortlicher (Datenverarbeitung)"
    Auftragsverarbeiter = "Auftragsverarbeiter"
    AnbieterDigital = "Anbieter digitaler Dienste"
    Hersteller = "Hersteller / Produktverantwortlicher"
    Bundesbehoerde = "Bundesbehörde (Öffentliche Stelle des Bund)"
    Landesbehoerde = "Landesbehörde (Öffentliche Stelle des Landes/Kommune)"
    Forschung = "Forschungseinrichtung / Hochschule"
    ISB = "Informationssicherheitsbeauftragter (ISB)"
    DSB = "Datenschutzbeauftragter (DSB)"
    Marktueberwachung = "Marktüberwachungsbehörde"
    Zertifizierer = "Notifizierende Stelle / Zertifizierer"
    Bank = "Bank / Finanzinstitut"
    Telekom = "Telekommunikationsanbieter"
    Gesundheit = "Gesundheitseinrichtung / Arzt"
    Mitgliedstaat = "Mitgliedstaat (EU)"
    Buerger = "Natürliche Person (Bürger)"
    Betroffener = "Betroffene Person"
    Andere = "Andere"

class AnWen(str, Enum):
    BSI = "BSI (Bundesamt für Sicherheit in der Informationstechnik)"
    BNetzA = "Bundesnetzagentur (BNetzA)"
    BfDI = "BfDI (Bundesbeauftragter für Datenschutz)"
    Landesdatenschutz = "Landesdatenschutzbehörde"
    DatenschutzAllgemein = "Datenschutzaufsichtsbehörden (allgemein)"
    EU_Kommission = "Europäische Kommission"
    EDPB = "Europäischer Datenschutzausschuss (EDPB)"
    ENISA = "ENISA (EU-Agentur für Cybersicherheit)"
    Marktueberwachung = "Marktüberwachungsbehörde"
    Polizei = "Strafverfolgungsbehörde (Polizei/Staatsanwaltschaft)"
    BaFin = "Finanzaufsicht (BaFin)"
    AndereAufsicht = "Andere Aufsichtsbehörde"
    Bundestag = "Bundestag / Bundesrat"
    Verantwortlicher = "Verantwortlicher (Datenverarbeitung)"
    Nutzer = "Nutzer / Endanwender"
    Betroffener = "Betroffene Person"
    Oeffentlichkeit = "Öffentlichkeit (Publikation)"
    Zertifizierer = "Zertifizierungsstelle"
    Meldestelle = "Meldestelle (CSIRT / CIRT / CERT)"
    Forschungszentrum = "Forschungsdatenzentrum"
    Andere = "Andere"

class Sektor(str, Enum):
    Wirtschaft = "Unternehmen / Wirtschaft"
    Verwaltung = "Verwaltung"
    Privat = "Privatpersonen"
    Gesetzgebung = "Gesetzgebung"
    Forschung = "Forschung und Wissenschaft"
    Rechtsprechung = "Rechtsprechung"
    Uebergreifend = "Übergreifend"

class Schutzrichtung(str, Enum):
    Selbstbestimmung = "Schutz der informationellen Selbstbestimmung (Individuenzentriert)"
    Wettbewerb = "Schutz der wirtschaftlichen Fairness & Wettbewerbsfähigkeit (Marktzentriert)"
    Gemeinwohl = "Schutz des Gemeinwohls & der öffentlichen Sicherheit (Staatszentriert)"
    Systemintegritaet = "Schutz der Systemintegrität & Cybersicherheit (Technikzentriert)"

class AusloeserTyp(str, Enum):
    antragsgebunden = "antragsgebunden"
    ereignisgebunden = "ereignisgebunden"
    entscheidungsgebunden = "entscheidungsgebunden"
    statusgebunden = "statusgebunden"
    periodisch = "periodisch"
    vorab_ex_ante = "vorab / ex ante"
    fortlaufend = "fortlaufend"
    voraussetzungsgebunden = "voraussetzungsgebunden"

class FristTyp(str, Enum):
    sofort_unverzueglich = "sofort / unverzüglich"
    feste_zeitspanne = "feste Zeitspanne"
    sofort_mit_maximalfrist = "sofort mit Maximalfrist"
    vorab_ex_ante = "vorab / ex ante"
    fortlaufend_dauerhaft = "fortlaufend / dauerhaft"
    periodisch_wiederkehrend = "periodisch / wiederkehrend"
    auf_verlangen = "auf Verlangen / auf Antrag"
    keine_frist = "keine Frist genannt"

# ---------------------------------------------------------------------------
# Derive Option Lists for Prompt Context
# ---------------------------------------------------------------------------

def get_pflicht_display_name(p: ArtDerPflicht) -> str:
    """
    Returns the long display name for the prompt.
    Uses 'match' for type-safe exhaustiveness checking.
    """
    match p:
        case ArtDerPflicht.Meldepflicht:
            return "Meldepflicht (oder Anzeigepflicht)"
        case ArtDerPflicht.Benachrichtigungspflicht:
            return "Benachrichtigungs-/Unterrichtungspflicht (oder Informationspflicht)"
        case ArtDerPflicht.Auskunftspflicht:
            return "Auskunftspflicht (oder Auskunftsverlangen)"
        case ArtDerPflicht.Berichtspflicht:
            return "Berichtspflicht"
        # Verfahrenspflichten
        case ArtDerPflicht.Registrierungspflicht:
            return "Registrierungspflicht (oder Eintragspflicht)"
        case ArtDerPflicht.Mitwirkungspflicht:
            return "Mitwirkungspflicht (oder Verfahrenspflicht, auch Einwilligung)"
        # Daten- oder Zugangsbereitstellungspflichten
        case ArtDerPflicht.Bereitstellungspflicht:
            return "Bereitstellungspflicht (oder Herausgabepflicht)"
        # Governancepflichten
        case ArtDerPflicht.Dokumentationspflicht:
            return "Dokumentationspflichten (Dokumentation, Verzeichnis führen, Protokollierung, Nachweise)"
        case ArtDerPflicht.Prüfpflicht:
            return "Prüfpflicht (oder Überprüfungspflicht, Bewertungspflicht)"
        case ArtDerPflicht.Benennungspflicht:
            return "Benennungspflicht (oder Ernennungspflicht, Bestellungspflicht)"
        case ArtDerPflicht.Veröffentlichungspflicht:
            return "Veröffentlichungspflicht (oder Bekanntmachungspflicht)"
        case ArtDerPflicht.SonstigePflicht:
            return "Sonstige Pflicht (nur wenn keine der anderen Kategorien passt)"
        case _ as unreachable:
            # IDEs like VS Code/Pylance will flag this if a case is missing!
            assert_never(unreachable)
    return ""  # Should be unreachable


# Generate the prompt strings.
PFLICHT_LIST_STR = "\n".join(f"- {get_pflicht_display_name(p)}" for p in list(ArtDerPflicht))
WER_LIST_STR = "\n".join(f"- {v.value}" for v in list(Wer))
AN_WEN_LIST_STR = "\n".join(f"- {v.value}" for v in list(AnWen))
SEKTOR_LIST_STR = "\n".join(f"- {s.value}" for s in list(Sektor))
SCHUTZRICHTUNG_LIST_STR = "\n".join(f"- {sr.value}" for sr in list(Schutzrichtung))
AUSLOESER_TYP_LIST_STR = "\n".join(f"- {at.value}" for at in list(AusloeserTyp))
FRIST_TYP_LIST_STR = "\n".join(f"- {ft.value}" for ft in list(FristTyp))

SYSTEM_PROMPT = f"""Du bist ein juristischer Assistent, der Meldepflichten, Dokumentationspflichten und verwandte Informationspflichten aus deutschen und EU-Rechtstexten extrahiert.
Deine Aufgabe
Identifiziere alle relevanten Pflichten zur Informationsweitergabe oder Dokumentation im gegebenen Gesetzesabschnitt.
Erfasse dabei folgende Pflichten:
{PFLICHT_LIST_STR}

Für jede gefundene Pflicht extrahierst du:

Grunddaten:
- **referenz**: Die genaue Paragraphen- oder Artikelangabe (z. B. "§ 32 Absatz 1" oder "Art. 33 Abs. 2 lit. a"; ohne Gesetzesangabe)
- **art_der_pflicht**: Die Art der Pflicht (z. B. "Meldepflicht", "Auskunftspflicht", "Dokumentationspflicht")

Beteiligte:
- **wer**: Wer ist zur Meldung/Auskunft verpflichtet? Wähle einen passenden Wert aus dieser Liste:
{WER_LIST_STR}
- **an_wen**: An wen muss die Information fließen? Wähle einen passenden Wert aus dieser Liste:
{AN_WEN_LIST_STR}

Kontext:
- **sektor**: Welcher Sektor wird hier primär reguliert? Wähle einen passenden Wert aus dieser Liste:
{SEKTOR_LIST_STR}
- **schutzrichtung**: In welche Schutzrichtung fällt diese Pflicht primär? Wähle einen passenden Wert aus dieser Liste:
{SCHUTZRICHTUNG_LIST_STR}

Auslöser:
- **ausloeser**: Freitext – wodurch wird die Pflicht ausgelöst? (z. B. "Eingang eines Antrags", "Vorliegen einer Datenschutzverletzung")
- **ausloeser_typ**: Wähle genau eine Kategorie:
{AUSLOESER_TYP_LIST_STR}

Frist:
- **frist**: Freitext – welche Frist gilt für die Meldung/Auskunft? (z. B. "unverzüglich", "innerhalb von 72 Stunden", "auf Verlangen")
- **frist_typ**: Wähle genau eine Kategorie:
{FRIST_TYP_LIST_STR}

Inhalt:
- **zitat**: Das genaue Zitat aus dem Gesetzestext, das die Pflicht beschreibt.
- **was_gemeldet_wird**: Eine knappe Zusammenfassung (1–2 Sätze) auf Deutsch, was genau mitgeteilt, bereitgestellt oder dokumentiert werden muss.

Bewertung:
- **konfidenz**: Wie sicher bist du dir, dass dies eine relevante Pflicht ist? (0.0–1.0)

Wichtige Hinweise:
- Halte dich strikt an die vorgegebenen Listen.
- Wenn im Abschnitt keine relevante Pflicht vorkommt, gib eine leere Liste zurück.
* Extrahiere keine rein internen Organisationspflichten **ohne Dokumentations- oder Informationsbezug**.
* Dokumentationspflichten sind **immer relevant**, auch wenn keine Information an Dritte fließt.
* Extrahiere keine Pflichten, die ausschließlich nach individueller Anordnung einer Behörde im Einzelfall entstehen.
- Halte "was_gemeldet_wird" sachlich und präzise.
"""


# ---------------------------------------------------------------------------
# Pydantic models for Structured Output
# ---------------------------------------------------------------------------

class Meldepflicht(BaseModel):
    referenz: str = Field(
        description="Die genaue Norm-Fundstelle, z. B. '§ 32 Absatz 1' oder 'Art. 33 Abs. 2'."
    )
    art_der_pflicht: ArtDerPflicht = Field(
        description="Art der Pflicht aus der vorgegebenen Liste."
    )
    wer: Wer = Field(
        description="Wer ist zur Meldung/Auskunft verpflichtet (Werte aus der Liste)."
    )
    an_wen: AnWen = Field(
        description="An wen wird gemeldet (Werte aus der Liste)."
    )
    sektor: Sektor = Field(
        description="Der regulierte Sektor (Werte aus der Liste)."
    )
    schutzrichtung: Schutzrichtung = Field(
        description="Die primäre Schutzrichtung der Pflicht."
    )
    ausloeser: str = Field(
        description="Freitext – wodurch wird die Pflicht ausgelöst? (z. B. \"Eingang eines Antrags\", \"Vorliegen einer Datenschutzverletzung\")"
    )
    ausloeser_typ: AusloeserTyp = Field(
        description="Der Auslöser der Pflicht (Werte aus der Liste)."
    )
    frist: str = Field(
        description="Freitext – welche Frist gilt für die Meldung/Auskunft?"
    )
    frist_typ: FristTyp = Field(
        description="Die Frist für die Meldung (Werte aus der Liste)."
    )
    zitat: str = Field(
        description="Das genaue Zitat aus dem Gesetzestext."
    )
    was_gemeldet_wird: str = Field(
        description="Knappe Zusammenfassung (1–2 Sätze) auf Deutsch."
    )
    konfidenz: float = Field(
        description="Konfidenz der KI (0.0-1.0), dass dies eine relevante Pflicht ist.",
        ge=0.0,
        le=1.0,
    )


class ExtractionResponse(BaseModel):
    meldepflichten: List[Meldepflicht] = Field(
        description="Liste aller gefundenen Meldepflichten und verwandten Pflichten im Abschnitt."
    )
