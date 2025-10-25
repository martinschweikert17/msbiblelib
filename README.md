# msbiblelib — Python‑Bibliothek für das Finden von Bibelübersetzungen auf Servern & für Analyse und Validierung von Bibelstellenangaben

`msbiblelib` hilft dir beim **Parsen von Bibelstellen**, beim **Nachschlagen von 
Buch‑Metadaten** (Kapitel-/Versanzahl, Testament) sowie beim **Arbeiten mit externen 
Bibelservern** und **Übersetzungen** (deutsche und englische) sowie hebräischen und 
griechischen Grundtexten.
Die Bibliothek ist modular aufgebaut und nutzt XML‑Dateien als Datenquellen.

> Status: frühe Version – API kann sich noch ändern. Pull Requests willkommen!

---

## Inhalt

- [Features](#features)
- [Installation](#installation)
- [Schnellstart](#schnellstart)
- [Module & API](#module--api)
  - [`mblbooks` – Bücher & Kapitel/Versetabellen](#mblbooks--bücher--kapitelversetabellen)
  - [`mblservers` – Externe Bibelserver](#mblservers--externe-bibelserver)
  - [`mblversions` – Versionen/Übersetzungen](#mblversions--versionenübersetzungen)
  - [`mblreferences` – Bibelstellen parsen](#mblreferences--bibelstellen-parsen)
  - [`main.py` – Mini-Demo](#mainpy--mini-demo)
- [Datenquellen (XML)](#datenquellen-xml)
- [Bekannte Besonderheiten](#bekannte-besonderheiten)
- [Entwicklung](#entwicklung)
- [Lizenz](#lizenz)
- [Quellen](#quellen)

---

## Features

- 💡 **Parsing von Bibelstellenangaben** (z. B. `Gen1.1-2.6`, `2Joh3-8`) inkl. Normalisierung und Plausibilitätschecks.[1]  
- 📚 **Buch-Metadaten**: Abkürzungen, max. Kapitel, Verszahlen pro Kapitel, Testament (AT/NT).[2]  
- 🌐 **Bibelserver-Katalog** mit Name, Basis‑URL, Kapitel‑URL‑Schablone und Buchnamens‑Mapping je Server.[3]  
- 🔤 **Übersetzungen** inkl. Sprache, Anzeigename, Server‑Zugehörigkeit, optionalem Zusatzinhalt.[4]

---

## Installation

```bash
# lokal in ein virtuelles Environment installieren
pip install -e .
```

*(Das Paket ist als Bibliothek gedacht; ein Python 3.x‑Interpreter genügt.)*

---

## Schnellstart

```python
from msbiblelib.mblbooks import Books
from msbiblelib.mblservers import Bibleservers
from msbiblelib.mblreferences import References
from msbiblelib.mblversions import Versions

books = Books()           # lädt books.xml
servers = Bibleservers()  # lädt servers.xml
refs = References()       # nutzt Books intern
vers = Versions()         # lädt versions.xml

# 1) Buchinfos
print(books.get_max_chapter("GEN"))        # -> 50
print(books.get_max_verse("GEN", 1))       # -> 31
print(books.get_testament("RÖM"))          # -> "NT"

# 2) Referenzen parsen
r = refs.parse_reference("2Joh3-8")
print(r["reference"])                       # -> "2JOH1.3-8"

# 3) Server auflisten
for s in servers.get_servers():
    print(s["name"], s["url"])

# 4) Versionen filtern (z. B. alle deutschen)
de_versions = vers.get_versions_filtered(None, ["de"], None)
```

Die Klassen lesen ihre Daten aus den mitgelieferten XML‑Dateien und geben dir Python‑Datenstrukturen (Listen/Dictionaries) zurück.[2][3][4]

---

## Module & API

### `mblbooks` – Bücher & Kapitel/Verstabellen

**Klasse:** `Books`

- Lädt `books.xml` und bietet Lookup‑Funktionen für Abkürzungen, Kapitel‑/Versanzahl, Testament und LaTeX‑Abkürzung.[2]  
- Wichtige Methoden:
  - `get_valid_abbreviations() → list[str]` – alle bekannten Buchabkürzungen.
  - `is_valid_abbreviation(abbrev) → bool` – prüft Abkürzung.
  - `get_sort_value(abbrev) → int` – Position in der Kanon‑Sortierung.
  - `get_max_chapter(abbrev) → int` – höchstes Kapitel eines Buches.
  - `get_max_verse(abbrev, chapter) → int|None` – Versanzahl in einem Kapitel.
  - `get_testament(abbrev) → "OT"|"NT"|None` – Zugehörigkeit.
  - `get_psalms_with_heading() → list[int]` / `is_psalm_with_heading(ch) → bool` – Liste/Prüfung für Psalmen mit Überschrift.[5]

**Hinweis:** Eine interne Liste markiert *Ein‑Kapitel‑Bücher* (Obadja, Philemon, 2/3 Johannes, Judas), da ein Server diese auslässt.[5]

---

### `mblservers` – Bibelserver

**Klasse:** `Bibleservers`

- Lädt `servers.xml` und liefert eine Liste von Server‑Dictionaries mit `name`, `url`, `chapterurl`, optional `status` (Standard „active“) und einem `books`‑Array mit server‑spezifischen Buchnamen (de/en/extra) + projektweiter Abkürzung.[3]  
- Methoden:
  - `get_servers() → list[dict]` – alle Server.
  - `get_server_by_name(name) → dict|None` – serverobjekt per Name (case‑insensitiv).

Die Kapitel‑URL‑Schablonen verwenden Platzhalter wie `{book}`, `{chapter}`, `{version}`, `{la}`/`{language}` oder `{testament}` je nach Server. Beispiele und Kommentare findest du in `servers.xml`.[3]

---

### `mblversions` – Versionen/Übersetzungen

**Klasse:** `Versions`

- Lädt `versions.xml` (nicht im Repo enthalten; siehe Schema unten). Ein Eintrag enthält `name`, `servername`, `language`, `content`, `server`, `fullname` und optional `extracontent` (Komma‑Liste).[4]  
- Methoden:
  - `get_versions() → list[dict]` – Rohdaten.
  - `get_versions_filtered(vfilter, lfilter, sfilter) → list[dict]` – Filter nach Versionsnamen, Sprache und (beabsichtigt) Server.

> ⚠️ **Hinweis:** In der aktuellen Implementierung wird der `sfilter` (Serverfilter) nicht aktiviert, da die Variable `server_filter` nicht aus `sfilter` gesetzt wird – ein kleiner Bug.[6]

**Minimal‑Schema für `versions.xml`:**

```xml
<versions>
  <version>
    <name>NIV</name>
    <servername>NIV</servername>
    <language>en</language>
    <content>FB</content>
    <server>Biblegateway</server>
    <fullname>New International Version</fullname>
    <extracontent>intro,footnotes</extracontent> <!-- optional, komma-getrennt -->
  </version>
</versions>
```

---

### `mblreferences` – Bibelstellen parsen

**Klasse:** `References` (nutzt intern `Books`)

- `parse_reference(text: str) → dict` analysiert eine Referenz, normalisiert Trennzeichen (`,`/`:` → `.`), erkennt Muster von komplex nach einfach, und führt Plausibilitätsprüfungen durch (Abkürzungen, Kapitel-/Versgrenzen). Ein‑Kapitel‑Bücher werden automatisch auf Kapitel 1 korrigiert (z. B. `2Joh3-8` → `2JOH1.3-8`).[1]

**Unterstützte Formen (Beispiele):**

- `Gen1.1-2.6` → Bereich über Kapitelgrenzen (FBFCFVTCTV - "From Book From Chapter From Verse To Chapter To Verse")  
- `Gen1.1-6` → Bereich innerhalb eines Kapitels (FBFCFVTV - "From Book From Chapter From Verse) To Verse")
- `Gen1.1` → (FBFCFV - "From Book From Chapter From Verse")
- `Gen1-2` → (FBFCTC - "From Book From Chapter To Chapter")
- `Gen1` → (FBFC - "From Book From Chapter")
- `Gen-Ex` → (FBTB - "From Book To Book")
- `Gen` → (FB - "From Book")

**Rückgabe (Auszug):**

```python
{
  "passed": True,          # False bei Fehlern
  "messages": "",          # Fehlertexte (deutsch)
  "reference": "GEN1.1-2.6",
  "type": "FBFCFVTCTV",
  "frombook": "GEN", "tobook": "",
  "fromchapter": 1, "tochapter": 2,
  "fromverse": 1, "toverse": 6
}
```

---

### `main.py` – Mini-Demo

Das Skript zeigt nur exemplarisch, wie die Klassen instanziiert werden (kein CLI).[7]

```python
from mblreferences import References
from mblservers import Bibleservers
from mblversions import Versions
from mblbooks import Books

def main():
    bibleservers = Bibleservers()
    bibleversions = Versions()
    biblebooks = Books()
    srv = bibleservers.get_servers()
```

---

## Datenquellen (XML)

- **`books.xml`** – Kanon mit Kapiteln/Versen, Testament pro Buch (`abbrev`, `maxchapter`, `testament`, `latex_abbrev`, `<chapter number="…" verses="…"/>`).[2]  
- **`servers.xml`** – Mehrere `<bibleserver>`‑Blöcke mit `name`, `url`, `chapterurl` (Platzhalter), und `<books>`‑Mapping je Server (teilweise mit abweichenden lokalen Buchnamen). Enthält auch Kommentare/Hinweise pro Server.[3]  
- **`versions.xml`** – nicht enthalten; Struktur siehe Abschnitt zu `mblversions`.[4]

---

## Bekannte Besonderheiten

- **Ein‑Kapitel‑Bücher**: Einige Server führen Ein‑Kapitel‑Bücher nicht – `Books` hält daher eine entsprechende Liste und `References` korrigiert Eingaben automatisch.[5]  
- **URL‑Platzhalter**: `chapterurl` kann `{book}`, `{chapter}`, `{version}`, `{la}`/`{language}` oder `{testament}` enthalten und variiert je Anbieter (siehe Beispiele in `servers.xml`).[3]  
- **Serverfilter in `Versions`**: Der `sfilter` ist in `get_versions_filtered` aktuell wirkungslos (siehe Hinweis).[6]

---

## Entwicklung

- **Tests/Playground**: Starte mit `main.py` oder schreibe eigene kleine Snippets.[7]  
- **Beitragen**: Issues/PRs für Bugfixes (z. B. `sfilter`), neue Serverdefinitionen oder zusätzliche Validierungen sind willkommen.
- **Stil**: Typannotationen & Docstrings gern gesehen; XML‑Schemata klein halten.

---

## Lizenz

GNU General Public License (GPL) v3

---

## Quellen

[1] `mblreferences.py` – Parser und Normalisierung von Bibelstellen; nutzt `Books` zur Validierung.  
[2] `books.xml` – Bestandteil dieses Repos; Datengrundlage für Buch‑Metadaten.  
[3] `servers.xml` – Datenbank externer Bibelserver inkl. URL‑Schablonen und Buch‑Mappings.  
[4] `versions.xml` – Datenbank für Übersetzungen  
[5] `mblbooks.py` – Enthält Hilfslogik/Listen für besondere Fälle (z. B. Ein‑Kapitel‑Bücher, Psalmen mit Überschrift).  
[6] `mblversions.py` – Verwaltung von Versionen/Übersetzungen; Hinweis auf den (noch) inaktiven `sfilter`.  
[7] `main.py` – Minimalbeispiel zur Initialisierung der Klassen.
