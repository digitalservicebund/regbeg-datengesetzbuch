# Übersicht der Normen-Sammlung (Datengesetzbuch Context)

Diese Sammlung enthält zentrale Gesetze und Entwürfe zur Datenregulierung auf EU- und nationaler Ebene, optimiert für die Verarbeitung durch LLMs.

## Struktur der Datenformate
- **Plaintext (_Plaintext.txt):** Die durch `convert_normen.py` optimierten Fassungen. Zeilenumbrüche innerhalb von Absätzen wurden entfernt ("flattened"), um das Greppen und die LLM-Verarbeitung zu vereinfachen. **Dies ist das empfohlene Format.**
- **XML:** Volltexte von `gesetze-im-internet.de`. Gut für hierarchische Analysen, aber oft mit Umbrüchen im Text.
- **Text (.txt):** Die ursprünglichen PDF-Exzerpte mit manuellem Layout.

---

## 1. Europäische Union (EU)
Diese Verordnungen gelten unmittelbar und bilden den horizontalen Rahmen.

| Norm | Original (Layout) | Optimiert (LLM) |
| :--- | :--- | :--- |
| **DSGVO** | [DSGVO_Volltext.txt](./DSGVO/DSGVO_Volltext.txt) | [Plaintext](./DSGVO/DSGVO_Volltext_Plaintext.txt) |
| **AI Act** | [AIAct_Volltext.txt](./AIAct/AIAct_Volltext.txt) | [Plaintext](./AIAct/AIAct_Volltext_Plaintext.txt) |
| **DORA** | [DORA_Volltext.txt](./DORA/DORA_Volltext.txt) | [Plaintext](./DORA/DORA_Volltext_Plaintext.txt) |
| **Data Act** | [DataAct_Volltext.txt](./DataAct/DataAct_Volltext.txt) | [Plaintext](./DataAct/DataAct_Volltext_Plaintext.txt) |
| **Data Governance Act** | [DGA_Volltext.txt](./DGA/DGA_Volltext.txt) | [Plaintext](./DGA/DGA_Volltext_Plaintext.txt) |
| **Digital Markets Act** | [DMA_Volltext.txt](./DMA/DMA_Volltext.txt) | [Plaintext](./DMA/DMA_Volltext_Plaintext.txt) |
| **Digital Services Act** | [DSA_Volltext.txt](./DSA/DSA_Volltext.txt) | [Plaintext](./DSA/DSA_Volltext_Plaintext.txt) |
| **Interoperable Europe Act** | [IEA_Volltext.txt](./IEA/IEA_Volltext.txt) | [Plaintext](./IEA/IEA_Volltext_Plaintext.txt) |

## 2. Nationale Gesetze (Deutschland) - Volltexte
Aktuelle konsolidierte Fassungen im strukturierten XML-Format.

| Abkürzung | Norm | Original (XML) | Optimiert (LLM) |
| :--- | :--- | :--- | :--- |
| **BDSG** | Bundesdatenschutzgesetz | [BDSG_Volltext.xml](./BDSG/BDSG_Volltext.xml) | [Plaintext](./BDSG/BDSG_Volltext_Plaintext.txt) |
| **TDDDG** | TDDDG | [TDDDG_Volltext.xml](./TDDDG/TDDDG_Volltext.xml) | [Plaintext](./TDDDG/TDDDG_Volltext_Plaintext.txt) |
| **BSIG** | BSI-Gesetz | [BSIG_Volltext.xml](./BSIG/BSIG_Volltext.xml) | [Plaintext](./BSIG/BSIG_Volltext_Plaintext.txt) |
| **DDG** | Digitale-Dienste-Gesetz | [DDG_Volltext.xml](./DDG/DDG_Volltext.xml) | [Plaintext](./DDG/DDG_Volltext_Plaintext.txt) |
| **OZG** | Onlinezugangsgesetz | [OZG_Volltext.xml](./OZG/OZG_Volltext.xml) | [Plaintext](./OZG/OZG_Volltext_Plaintext.txt) |
| **RegMoG** | Registermodernisierungsgesetz | [RegMoG_Volltext.xml](./RegMoG/RegMoG_Volltext.xml) | [Plaintext](./RegMoG/RegMoG_Volltext_Plaintext.txt) |
| **GDNG** | Gesundheitsdatennutzungsgesetz | [GDNG_Volltext.xml](./GDNG/GDNG_Volltext.xml) | [Plaintext](./GDNG/GDNG_Volltext_Plaintext.txt) |
| **GeoZG** | Geodatenzugangsgesetz | [GeoZG_Volltext.xml](./GeoZG/GeoZG_Volltext.xml) | [Plaintext](./GeoZG/GeoZG_Volltext_Plaintext.txt) |
| **IFG** | Informationsfreiheitsgesetz | [IFG_Volltext.xml](./IFG/IFG_Volltext.xml) | [Plaintext](./IFG/IFG_Volltext_Plaintext.txt) |
| **DNG** | Datennutzungsgesetz | [DNG_Volltext.xml](./DNG/DNG_Volltext.xml) | [Plaintext](./DNG/DNG_Volltext_Plaintext.txt) |

## 3. Entwürfe & Durchführungsgesetze
Aktuelle Gesetzgebungsverfahren oder begleitende Durchführungsbestimmungen (Text-Format).

| Norm / Entwurf | Original | Optimiert (LLM) | Status |
| :--- | :--- | :--- | :--- |
| **NIS2-UmsG** | [NIS2-UmsG_Volltext.txt](./NIS2-UmsG/NIS2-UmsG_Volltext.txt) | [Plaintext](./NIS2-UmsG/NIS2-UmsG_Volltext_Plaintext.txt) | Verkündet |
| **DGG** (Daten-Governance-Gesetz) | [DGG_Entwurf.txt](./DGG/DGG_Entwurf.txt) | [Plaintext](./DGG/DGG_Entwurf_Plaintext.txt) | Entwurf |
| **MDG** (Mobilitätsdatengesetz) | [MDG_Entwurf.txt](./Mobilitätsdatengesetz/MDG_Entwurf.txt) | [Plaintext](./Mobilitätsdatengesetz/MDG_Entwurf_Plaintext.txt) | Entwurf |
| **FDG** (Forschungsdatengesetz) | [FDG_Eckpunkte.txt](./Forschungsdatengesetz/FDG_Eckpunkte.txt) | [Plaintext](./Forschungsdatengesetz/FDG_Eckpunkte_Plaintext.txt) | Entwurf |
| **DA-DG** (Data Act-Durchführungsgesetz) | [DA-DG_Entwurf.txt](./DA-DG/DA-DG_Entwurf.txt) | [Plaintext](./DA-DG/DA-DG_Entwurf_Plaintext.txt) | Entwurf |
| **KI-VO-DG** | [KI-VO-DG_Entwurf.txt](./KI-Verordnung/KI-VO-DG_Entwurf.txt) | [Plaintext](./KI-Verordnung/KI-VO-DG_Entwurf_Plaintext.txt) | Entwurf |

## 4. Ressourcen
- **PDFs:** Die ursprünglichen Quelldateien befinden sich unter [/PDFs/](./PDFs/).
- **Konfiguration:** Die Liste der erfassten Normen ist in [Normen.md](../Normen.md) definiert.
