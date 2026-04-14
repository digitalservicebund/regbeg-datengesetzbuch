# Regelungsbegleitung zum Datengesetzbuch
This repository hosts a collection of data and scripts to analyze *Bestandsrecht* (existing law) from national and union legislation, with a focus on identifying and extracting regulatory obligations.

## Goals

- *Obligations* (e.g. Meldepflichten, Dokumentationspflichten) are identified correctly
- These obligations are extracted as a table for further automatic or manual work
- Enable users to do full search, filtering and various analysis on the data
- We learn more about using LLMs to parse existing law (*Bestandsrecht*).

## Getting started

### Install dependencies

This project uses `uv`. Run

    uv sync

to install the dependencies.

## Usage

### Convert all downloaded norms

    uv run scripts/convert_normen.py

### Analyze obligations

To analyze obligations from the downloaded norms, use the script `extract_meldepflichten_llm.py` like so:

    uv run scripts/extract_meldepflichten_llm.py --norm DSGVO

## Contributing

[Deutsche sprache weiter unten](#mitwirken)

Everyone is welcome to contribute! You can contribute by giving feedback, adding issues, answering questions, providing documentation or opening pull requests. Please always follow the guidelines and our [Code of Conduct](CODE_OF_CONDUCT.md).

To contribute code, simply open a pull request with your changes and it will be reviewed by someone from the team. By submitting a pull request you declare that you have the right to license your contribution to the DigitalService and the community under the license picked by the project.

## Mitwirken

Jede:r ist herzlich eingeladen, die Entwicklung der _Project_ mitzugestalten. Du kannst einen Beitrag leisten, indem du Feedback gibst, Probleme beschreibst, Fragen beantwortest, die Dokumentation erweiterst, oder Pull-Requests eröffnest. Bitte befolge immer die Richtlinien und unseren [Verhaltenskodex](CODE_OF_CONDUCT.md).

Um Code beizutragen erstelle einfach einen Pull Requests mit deinen Änderungen, dieser wird dann von einer Person aus dem Team überprüft. Durch das Eröffnen eines Pull-Requests erklärst du ausdrücklich, dass du das Recht hast deine Beitrag an den DigitalService und die Community unter der vom Projekt gewählten Lizenz zu lizenzieren.
