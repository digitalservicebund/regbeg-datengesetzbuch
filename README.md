# Regelungsbegleitung zum Datengesetzbuch

Dieses Repository beinhaltet eine Sammlung von Daten und Skripten, um nationales Recht und Unionsrecht (*Bestandsrecht*) zu analysieren. Der Fokus liegt dabei auf dem Identifizieren und Extrahieren von Pflichten.

## Kontext des Projektes

Das Projekt wurde im Zuge einer Regelungsbegleitung zum Thema Datengesetzbuch erarbeitet.

"Regelungsbegleitungen" ist ein Angebot des BMDS im Rahmen des Zentrum für Legistik. Interdisziplinäre Teams unterstützen Fachressorts, ihre Rechtsetzungsvorhaben adressatenorientiert, praxisnah und digital gut umsetzbar zu gestalten.

## Ziele

- *Pflichten* (z.B. Meldepflichten, Dokumentationspflichten) zu identifizieren
- Diese Pflichten als eine Tabelle zu extrahieren, um automatisierte oder manuelle Arbeit daran anzuschließen
- Nutzern die Möglichkeit geben, die Pflichten zu suchen, zu filtern und weitere Analysen durchzuführen
- Exploration von Möglichkeiten Bestandsrecht mit Sprachmodellen zu verarbeiten

## Statische Analyseergebnisse

Im Ordner [docs/data] sind diverse `.csv` Datenblätter mit den extrahierten Pflichten aus den entsprechenden Gesetzen.

Zusätzlich gibt es die Datei [docs/data/Pflichten.xlsx], die alle extrahierten Pflichten als Excel-Datei beinhaltet.

## Skripte benutzen

### Abhängigkeiten installieren

Dieses Projekt verwendet `uv`. Mit folgendem Befehl werden die Abhängigkeiten installiert:

    uv sync

### Verwendung

#### Alle heruntergeladenen Normen konvertieren

    uv run scripts/convert_normen.py

#### Pflichten analysieren

Um Pflichten aus den heruntergeladenen Normen zu extrahieren, wird das Skript `extract_meldepflichten_llm.py` wie folgt verwendet:

    uv run scripts/extract_meldepflichten_llm.py --norm DSGVO

## Haftungsausschluss

Vor der Verwendung der Ergebnisse dieses Repositories ist zu beachten, dass bei der Erzeugung dieser Ergebnisse Sprachmodelle (LLMs) eingesetzt werden.

> [!IMPORTANT]
> Das Skript `extract_meldepflichten_llm.py` und seine Basis `llm_extract_base.py` verarbeiten Normen und extrahieren Pflichten mithilfe eines Sprachmodells. Dies kann zu fehlerhaft extrahierten Pflichten führen, z.B. durch Halluzinationen oder andere Fehlerquellen. Dieses Projekt gewährleistet keine Vollständigkeit oder Korrektheit.

> [!IMPORTANT]
> Das Skript `similarity_pflichten.py` analysiert Paare von Pflichten auf Ähnlichkeit mithilfe eines allgemeinen [Sentence Transformers](https://huggingface.co/sentence-transformers/paraphrase-multilingual-mpnet-base-v2). Dies kann zu falsch-positiven und falsch-negativen Ergebnissen führen. Dieses Projekt gewährleistet keine Korrektheit der Ähnlichkeitsanalyse.

> [!IMPORTANT]
> Das Skript `qa_meldepflichten_llm.py` kann eine automatisierte Qualitätsbewertung der extrahierten Pflichten durchführen – sowohl mittels unscharfem Abgleich gegen eine manuelle Prüfdatei als auch durch eine LLM-basierte Bewertung. Die LLM-Scores sind Schätzwerte des Sprachmodells und spiegeln möglicherweise nicht die tatsächliche Korrektheit wider. Dieses Projekt gewährleistet keine Verlässlichkeit der Qualitätsbewertung.

## Mitwirken

Jede:r ist herzlich eingeladen, die Entwicklung dieses Projekts mitzugestalten. Du kannst einen Beitrag leisten, indem du Feedback gibst, Probleme beschreibst, Fragen beantwortest, die Dokumentation erweiterst, oder Pull-Requests eröffnest. Bitte befolge immer die Richtlinien und unseren [Verhaltenskodex](CODE_OF_CONDUCT.md).

Um Code beizutragen erstelle einfach einen Pull Request mit deinen Änderungen, dieser wird dann von einer Person aus dem Team überprüft. Durch das Eröffnen eines Pull-Requests erklärst du ausdrücklich, dass du das Recht hast, deinen Beitrag an den DigitalService und die Community unter der vom Projekt gewählten Lizenz zu lizenzieren.

[English version below](#contributing)

---

## Contributing

Everyone is welcome to contribute! You can contribute by giving feedback, adding issues, answering questions, providing documentation or opening pull requests. Please always follow the guidelines and our [Code of Conduct](CODE_OF_CONDUCT.md).

To contribute code, simply open a pull request with your changes and it will be reviewed by someone from the team. By submitting a pull request you declare that you have the right to license your contribution to the DigitalService and the community under the license picked by the project.
