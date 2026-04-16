# Phase 1 — Python-Tooling & Entwicklungsumgebung

**Ziel:** Am Ende dieser Phase hast du ein sauberes Python-Projekt aufgesetzt, kannst Dependencies verwalten, Code formatieren, Tests schreiben — und alles von der Kommandozeile aus bedienen. Das ist das Fundament, auf dem dein LIMS aufbaut.

**Zeitaufwand:** 2–4 Tage (je nach Tempo und Vorwissen)

**Voraussetzungen:** VS Code installiert, Git installiert, Zugang zu einem Terminal (PowerShell unter Windows, Bash unter Pop!_OS)

---

## Inhaltsverzeichnis

1. [Terminal-Grundlagen](#1-terminal-grundlagen)
2. [Python installieren](#2-python-installieren)
3. [VS Code für Python einrichten](#3-vs-code-für-python-einrichten)
4. [Python-Grundkonzepte (Crashkurs)](#4-python-grundkonzepte-crashkurs)
5. [uv — Der Paketmanager](#5-uv--der-paketmanager)
6. [pyproject.toml verstehen](#6-pyprojecttoml-verstehen)
7. [ruff — Linter und Formatter](#7-ruff--linter-und-formatter)
8. [pytest — Tests schreiben](#8-pytest--tests-schreiben)
9. [Git von der Kommandozeile](#9-git-von-der-kommandozeile)
10. [Abschluss-Übung: Alles zusammenbauen](#10-abschluss-übung-alles-zusammenbauen)
11. [Checkliste: Bin ich bereit für Phase 2?](#11-checkliste-bin-ich-bereit-für-phase-2)

---

## 1. Terminal-Grundlagen

> **Warum das wichtig ist:** Python-Entwicklung lebt auf der Kommandozeile. Server starten, Tests ausführen, Dependencies installieren, Git-Operationen — das alles passiert im Terminal. Du musst kein Shell-Scripting-Experte werden, aber eine Handvoll Befehle sicher beherrschen.

### 1.1 Terminal öffnen

**Windows:**
- VS Code: `Ctrl+Ö` (deutsches Layout) oder `Ctrl+Backtick` öffnet das integrierte Terminal
- Wähle **PowerShell** als Standard-Shell (nicht CMD)
- Alternativ: Windows Terminal App aus dem Microsoft Store (empfohlen für Standalone-Nutzung)

**Pop!_OS:**
- VS Code: `Ctrl+Ö` oder `Ctrl+Backtick`
- Standalone: `Super`-Taste → "Terminal" tippen
- Standard-Shell ist Bash — das ist perfekt

### 1.2 Wichtige Befehle

Diese Befehle funktionieren sowohl in PowerShell (Windows) als auch in Bash (Linux). Wo es Unterschiede gibt, sind beide angegeben.

```bash
# Wo bin ich gerade?
pwd

# Ordnerinhalt anzeigen
ls                        # Beide OS
ls -la                    # Linux: auch versteckte Dateien und Details
dir                       # Windows-Alternative

# Ordner wechseln
cd ~/projects             # In den projects-Ordner im Home-Verzeichnis
cd ..                     # Eine Ebene nach oben
cd -                      # Zurück zum vorherigen Ordner (nur Linux)

# Ordner erstellen
mkdir ms-lims             # Neuen Ordner erstellen
mkdir -p ms-lims/src      # Mit Unterordnern (Linux)

# Datei anzeigen
cat pyproject.toml        # Beide OS
less pyproject.toml       # Linux: scrollbar (q zum Beenden)

# Datei erstellen (leer)
touch README.md           # Linux
New-Item README.md        # Windows PowerShell

# Löschen
rm datei.txt              # Datei löschen
rm -r ordner/             # Ordner mit Inhalt löschen (Vorsicht!)

# Suchen
which python              # Linux: Wo ist Python installiert?
where.exe python          # Windows: Wo ist Python installiert?

# Vorherige Befehle
↑ / ↓                     # Durch Befehlshistorie blättern
Ctrl+R                    # In Historie suchen (tippen → Enter)
```

### 1.3 Tipps für den Alltag

**Tab-Completion:** Tipp den Anfang eines Dateinamens oder Befehls und drücke `Tab` — das Terminal ergänzt automatisch. Das spart enorm Zeit und verhindert Tippfehler.

**Copy/Paste im Terminal:**
- Windows Terminal / PowerShell: `Ctrl+C` / `Ctrl+V` wie gewohnt
- Linux Terminal: `Ctrl+Shift+C` / `Ctrl+Shift+V` (ohne Shift ist `Ctrl+C` = Programm abbrechen!)

**Mehrere Befehle:** Verbinde Befehle mit `&&` — der zweite läuft nur, wenn der erste erfolgreich war:
```bash
mkdir ms-lims && cd ms-lims
```

> **Übung 1.1:** Öffne ein Terminal in VS Code. Navigiere zu deinem Home-Verzeichnis. Erstelle einen Ordner `projects`. Wechsle hinein. Erstelle darin einen Ordner `ms-lims`. Überprüfe mit `pwd`, dass du im richtigen Verzeichnis bist.

---

## 2. Python installieren

### 2.1 Welche Version?

Wir nutzen **Python 3.12 oder 3.13** — die aktuellsten stabilen Versionen. Django 5.x braucht mindestens Python 3.10, aber wir nehmen die neueste für bessere Performance und Type-Hint-Features.

### 2.2 Installation auf Windows

**Option A — Python.org (einfach):**
1. Gehe zu https://www.python.org/downloads/
2. Lade Python 3.12.x oder 3.13.x herunter
3. **WICHTIG:** Beim Installer den Haken bei "Add Python to PATH" setzen!
4. "Install Now" klicken

**Option B — winget (wenn du dich traust):**
```powershell
winget install Python.Python.3.12
```

**Überprüfen:**
```powershell
python --version
# Sollte sowas wie "Python 3.12.7" ausgeben
```

### 2.3 Installation auf Pop!_OS

Python ist vorinstalliert, aber möglicherweise eine ältere Version. Überprüfe zuerst:

```bash
python3 --version
```

Falls du eine neuere Version brauchst:
```bash
sudo apt update
sudo apt install python3.12 python3.12-venv python3.12-dev
```

> **Hinweis Pop!_OS:** Unter Linux heißt der Befehl oft `python3` statt `python`. Das wird `uv` später für dich abstrahieren — aber gut zu wissen falls du mal direkt Python aufrufst.

### 2.4 Überprüfung auf beiden OS

```bash
# Python-Version
python --version          # oder python3 --version auf Linux

# pip ist dabei (wird aber bald durch uv ersetzt)
pip --version             # oder pip3 --version auf Linux
```

> **Übung 2.1:** Installiere Python und überprüfe die Version. Starte die Python-REPL (tippe `python` ins Terminal) und tippe `print("Hello from MS-LIMS")`. Beende mit `exit()`.

---

## 3. VS Code für Python einrichten

### 3.1 Essenzielle Extensions

Öffne VS Code, gehe zur Extensions-Sidebar (`Ctrl+Shift+X`), und installiere:

1. **Python** (von Microsoft) — Syntax-Highlighting, IntelliSense, Debugging, venv-Erkennung
2. **Ruff** (von Astral) — Linting und Formatting (ersetzt Pylint, Black, isort)
3. **Even Better TOML** — Syntax-Highlighting für `pyproject.toml`
4. **GitLens** (optional aber empfohlen) — erweiterte Git-Integration, die du aus VS Code kennst

### 3.2 VS Code Settings für Python

Öffne die Settings (`Ctrl+,`), klicke oben rechts auf das JSON-Icon, und füge hinzu:

```json
{
    // Python
    "[python]": {
        "editor.defaultFormatter": "charliermarsh.ruff",
        "editor.formatOnSave": true,
        "editor.codeActionsOnSave": {
            "source.fixAll.ruff": "explicit",
            "source.organizeImports.ruff": "explicit"
        }
    },

    // Terminal-Einstellungen
    "terminal.integrated.defaultProfile.windows": "PowerShell",
    "terminal.integrated.defaultProfile.linux": "bash",

    // Allgemein nützlich
    "files.trimTrailingWhitespace": true,
    "files.insertFinalNewline": true,
    "editor.rulers": [88]
}
```

**Was das bewirkt:**
- Beim Speichern wird dein Python-Code automatisch formatiert (Ruff)
- Unbenutzte Imports werden automatisch entfernt
- Eine vertikale Linie bei Zeichen 88 zeigt dir die empfohlene Zeilenlänge
- Trailing Whitespace wird automatisch entfernt

### 3.3 Das integrierte Terminal

VS Code hat ein eingebautes Terminal — nutze es! `Ctrl+Ö` zum Öffnen/Schließen. Du kannst mehrere Terminals offen haben (z.B. eines für den Server, eines für Tests).

**Tipp:** Wenn du einen Ordner in VS Code öffnest (`File → Open Folder`), startet das Terminal automatisch in diesem Ordner. Öffne also immer den Projekt-Root.

> **Übung 3.1:** Installiere die Extensions. Erstelle eine Datei `test.py` mit dem Inhalt `x=1+2` (absichtlich ohne Leerzeichen). Speichere — Ruff sollte es automatisch zu `x = 1 + 2` formatieren.

---

## 4. Python-Grundkonzepte (Crashkurs)

> **Warum dieser Abschnitt:** Django, pytest, und alles was folgt nutzt Python-Features, die du kennen musst bevor du loslegst. Das hier ist kein vollständiger Python-Kurs — es sind die Konzepte, die du in den nächsten Phasen ständig sehen wirst.

### 4.1 Variablen und Typen

Python ist dynamisch typisiert (wie R, anders als C#). Du deklarierst keine Typen, aber du kannst sie annotieren (dazu später mehr).

```python
# Grundtypen
name = "Serum Sample"          # str
count = 42                      # int
concentration = 3.14            # float
is_valid = True                 # bool (großgeschrieben, anders als R!)
nothing = None                  # None (wie NULL in R, null in C#)

# Collections
analytes = ["Phe", "Tyr", "Val"]                    # list (wie c() in R)
sample = {"barcode": "S-001", "status": "new"}      # dict (wie named list in R)
positions = (1, 2, 3)                                # tuple (unveränderliche Liste)
unique_ids = {"A", "B", "C"}                         # set
```

**R → Python Übersetzung:**
| R | Python | Anmerkung |
|---|--------|-----------|
| `c(1, 2, 3)` | `[1, 2, 3]` | Liste (veränderbar) |
| `list(a=1, b=2)` | `{"a": 1, "b": 2}` | Dictionary |
| `TRUE / FALSE` | `True / False` | Großschreibung! |
| `NULL` | `None` | |
| `NA` | `None` oder `float('nan')` | Kein direktes Äquivalent |
| `paste0("a", "b")` | `"a" + "b"` oder `f"{'a'}{'b'}"` | |

### 4.2 Funktionen

```python
# Einfache Funktion
def generate_barcode(prefix, number):
    return f"{prefix}-{number:05d}"

result = generate_barcode("S", 42)  # "S-00042"

# Mit Typannotationen (empfohlen)
def generate_barcode(prefix: str, number: int) -> str:
    return f"{prefix}-{number:05d}"

# Mit Defaultwerten
def generate_barcode(prefix: str = "S", number: int = 1) -> str:
    return f"{prefix}-{number:05d}"
```

**f-Strings** sind die Python-Art, Variablen in Strings einzubauen (wie `glue::glue()` in R oder String Interpolation in C#):
```python
barcode = "S-001"
status = "received"
print(f"Sample {barcode} is now {status}")
# "Sample S-001 is now received"
```

### 4.3 Type Hints

Python-Code funktioniert ohne Typannotationen — aber mit ihnen ist der Code lesbarer und VS Code kann bessere Autovervollständigung bieten. In Django-Projekten sind sie Standard.

```python
# Ohne Type Hints — funktioniert, aber unklar
def find_sample(barcode, samples):
    for s in samples:
        if s["barcode"] == barcode:
            return s
    return None

# Mit Type Hints — sofort verständlich
def find_sample(barcode: str, samples: list[dict]) -> dict | None:
    for s in samples:
        if s["barcode"] == barcode:
            return s
    return None
```

**Häufige Type Hints:**
```python
name: str                          # Ein String
count: int                         # Eine Ganzzahl
values: list[float]                # Liste von Floats
sample: dict[str, str]             # Dictionary mit String-Keys und -Values
result: str | None                 # String ODER None (wie Optional in C#)
callback: Callable[[int], str]     # Funktion: nimmt int, gibt str zurück
```

> **Tipp:** Du musst Type Hints nicht von Anfang an überall einsetzen. Aber gewöhne dir an, Funktions-Signaturen zu annotieren — das hilft dir und anderen enorm beim Lesen.

### 4.4 Klassen (OOP-Basics)

In Django ist alles Klassen-basiert — Models, Views, Forms. Du musst OOP nicht lieben, aber die Syntax verstehen.

```python
class Sample:
    """Repräsentiert eine Laborprobe."""

    def __init__(self, barcode: str, sample_type: str):
        # __init__ ist der Konstruktor (wie Konstruktor in C#)
        self.barcode = barcode
        self.sample_type = sample_type
        self.status = "registered"        # Standardwert

    def receive(self):
        """Markiert die Probe als empfangen."""
        if self.status != "registered":
            raise ValueError(f"Cannot receive sample in state '{self.status}'")
        self.status = "received"

    def __str__(self):
        return f"Sample({self.barcode}, {self.status})"


# Nutzung
s = Sample("S-001", "serum")
print(s)            # "Sample(S-001, registered)"
s.receive()
print(s.status)     # "received"
```

**C# → Python Übersetzung:**
| C# | Python | Anmerkung |
|----|--------|-----------|
| `public class Sample` | `class Sample:` | Kein public/private |
| `public Sample(...)` | `def __init__(self, ...):` | Konstruktor |
| `this.barcode` | `self.barcode` | `self` statt `this` |
| `public string Barcode { get; set; }` | `self.barcode = barcode` | Keine Properties nötig |
| `ToString()` | `__str__()` | Dunder-Methods |
| `throw new Exception(...)` | `raise ValueError(...)` | Exceptions |

**`self` erklärt:** Jede Methode einer Klasse bekommt als ersten Parameter `self` — das ist die Instanz selbst (wie `this` in C#, aber explizit). Du rufst Methoden als `s.receive()` auf, aber intern bekommt `receive` automatisch `self=s` übergeben.

### 4.5 Decorators

Decorators sind ein Python-Feature, das du in Django und pytest ständig siehst. Sie "wrappen" eine Funktion oder Methode mit zusätzlichem Verhalten.

```python
# Ein Decorator ist eine Funktion, die eine Funktion modifiziert
# Du erkennst ihn am @-Zeichen

# Beispiel 1: pytest Fixture
import pytest

@pytest.fixture                    # ← Das ist der Decorator
def sample_data():
    return {"barcode": "S-001"}

# Beispiel 2: Django-Login-Check
from django.contrib.auth.decorators import login_required

@login_required                    # ← Nur eingeloggte User kommen durch
def sample_list(request):
    ...

# Beispiel 3: Django FSM Transition
from django_fsm import transition

@transition(field='state', source='registered', target='received')
def receive(self):
    self.received_at = timezone.now()
```

**Was passiert hier?** Der Decorator nimmt deine Funktion, packt sie in eine andere Funktion mit Zusatzlogik (z.B. "prüfe ob der User eingeloggt ist"), und gibt die modifizierte Version zurück. Du musst Decorators nicht selbst schreiben — nur verstehen, dass `@something` über einer Funktion bedeutet: "Diese Funktion hat Zusatzverhalten."

### 4.6 Kontrollstrukturen

```python
# if/elif/else
if status == "registered":
    print("Warten auf Empfang")
elif status == "received":
    print("Bereit zur Verarbeitung")
else:
    print(f"Unbekannter Status: {status}")

# for-Schleifen
for sample in samples:
    print(sample["barcode"])

# for mit Index
for i, sample in enumerate(samples):
    print(f"{i}: {sample['barcode']}")

# for über Dictionary
for key, value in sample.items():
    print(f"{key}: {value}")

# List Comprehension (wie purrr::map in R, LINQ in C#)
barcodes = [s["barcode"] for s in samples]
valid = [s for s in samples if s["status"] == "received"]
```

**Wichtig:** Python nutzt **Einrückung** statt geschweifter Klammern `{}` für Blöcke. Standard sind 4 Leerzeichen (ruff erzwingt das). Das ist anfangs ungewohnt, wird aber schnell intuitiv.

### 4.7 Module und Imports

```python
# Standard-Bibliothek
from datetime import datetime, timezone
import os
from pathlib import Path

# Eigener Code — Datei models/sample.py importieren
from models.sample import Sample

# Installierte Pakete
from django.db import models
import pytest
```

**Merke:** `from X import Y` importiert ein spezifisches Objekt. `import X` importiert das gesamte Modul (du rufst dann `X.Y` auf). Bevorzuge `from X import Y` wenn du weißt, was du brauchst.

### 4.8 Fehlerbehandlung

```python
try:
    sample = get_sample_by_barcode("S-999")
    sample.receive()
except SampleNotFoundError:
    print("Probe nicht gefunden")
except ValueError as e:
    print(f"Ungültiger Übergang: {e}")
finally:
    # Wird IMMER ausgeführt (wie finally in C#)
    print("Fertig")
```

> **Übung 4.1:** Erstelle eine Datei `sample.py` mit einer `Sample`-Klasse (barcode, sample_type, status). Implementiere `receive()` und `store()` mit einfacher Statusprüfung. Erstelle in einer separaten Datei `main.py` drei Samples, rufe `receive()` auf, und gib den Status aus. Lauf es mit `python main.py`.

---

## 5. uv — Der Paketmanager

> **Warum uv?** Python hat historisch ein fragmentiertes Tooling: `pip` installiert Pakete, `venv` erstellt Umgebungen, `pip-tools` lockt Dependencies, `pyenv` verwaltet Python-Versionen. `uv` ersetzt alle vier in einem schnellen, konsistenten Tool. Es ist 10–100x schneller als pip und wird schnell zum Standard.

### 5.1 uv installieren

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Pop!_OS:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Überprüfen (beide OS):**
```bash
uv --version
# Sollte sowas wie "uv 0.5.x" ausgeben
```

> **Falls der Befehl nicht gefunden wird:** Schließe das Terminal und öffne ein neues — der PATH wird erst beim Neustart der Shell aktualisiert.

### 5.2 Projekt erstellen

```bash
# Wechsle in deinen Projektordner
cd ~/projects

# Erstelle ein neues Projekt
uv init ms-lims

# Wechsle hinein
cd ms-lims

# Schau dir an, was erstellt wurde
ls -la
```

Was `uv init` erstellt:
```
ms-lims/
├── .python-version      # Gewünschte Python-Version (z.B. "3.12")
├── pyproject.toml        # Projekt-Konfiguration
├── README.md             # Leere Readme
└── hello.py              # Beispieldatei (kannst du löschen)
```

### 5.3 Dependencies verwalten

```bash
# Paket hinzufügen (installiert UND trägt es in pyproject.toml ein)
uv add django

# Entwicklungs-Dependencies (nur für Entwicklung, nicht für Produktion)
uv add --dev pytest pytest-django ruff

# Was wurde installiert?
uv tree
# Zeigt den Dependency-Tree (wie renv::status() in R)

# Paket entfernen
uv remove paketname

# Alle Dependencies frisch installieren (z.B. nach Git-Clone)
uv sync
```

**Wichtiger Unterschied zu pip:**
| pip (alter Weg) | uv (neuer Weg) | Was passiert |
|-----------------|-----------------|--------------|
| `pip install django` | `uv add django` | Installiert UND dokumentiert |
| `pip freeze > requirements.txt` | (automatisch: `uv.lock`) | Lockfile wird automatisch aktualisiert |
| `pip install -r requirements.txt` | `uv sync` | Reproduziert exakte Umgebung |
| `python -m venv .venv` | (automatisch) | venv wird bei Bedarf erstellt |

### 5.4 Code ausführen

```bash
# Statt "python script.py" verwendest du:
uv run python script.py

# Das funktioniert auch für installierte Tools:
uv run pytest
uv run ruff check .

# Django-Management-Commands (ab Phase 2):
uv run python manage.py runserver
```

**Warum `uv run`?** Es aktiviert automatisch die virtuelle Umgebung und stellt sicher, dass der richtige Python-Interpreter und alle installierten Pakete verfügbar sind. Du musst nie manuell `source .venv/bin/activate` aufrufen.

### 5.5 Was eine virtuelle Umgebung ist (Hintergrundwissen)

Wenn du `uv add django` aufrufst, erstellt uv automatisch einen `.venv`-Ordner in deinem Projekt. Darin liegt:
- Eine Kopie des Python-Interpreters
- Alle installierten Pakete (nur für dieses Projekt)
- Binaries/Scripts der installierten Tools

Das bedeutet: Wenn du zwei Projekte hast — eines mit Django 4.2, eines mit Django 5.1 — kollidieren sie nie, weil jedes seine eigene `.venv` hat.

```bash
# Schau dir die venv an
ls .venv/
# Du siehst: bin/ (oder Scripts/ auf Windows), lib/, include/, ...

# Wo ist Python jetzt?
uv run which python         # Linux
uv run where.exe python     # Windows
# Zeigt: .../ms-lims/.venv/bin/python (nicht das System-Python)
```

**Du musst die .venv nie manuell anfassen.** `uv run` kümmert sich um alles. Aber es ist gut zu wissen, was da passiert.

> **Übung 5.1:** Erstelle das Projekt mit `uv init ms-lims`. Füge `django` und `pytest` als Dependencies hinzu. Lasse `uv tree` laufen und schau dir die Ausgabe an. Führe `uv run python -c "import django; print(django.__version__)"` aus — es sollte die Django-Version ausgeben.

---

## 6. pyproject.toml verstehen

Die `pyproject.toml` ist das Herzstück deiner Projektkonfiguration. Nach `uv init` und `uv add` sieht sie ungefähr so aus:

```toml
[project]
name = "ms-lims"
version = "0.1.0"
description = "Lightweight LIMS for mass spectrometry laboratories"
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "django>=5.1",
]

[dependency-groups]
dev = [
    "pytest>=8.0",
    "pytest-django>=4.9",
    "ruff>=0.8",
]
```

### 6.1 Sektionen erklärt

**`[project]`** — Metadaten und Produktions-Dependencies.
- `name`: Projektname (keine Leerzeichen, Kleinbuchstaben)
- `version`: Semantische Versionierung (MAJOR.MINOR.PATCH)
- `requires-python`: Minimale Python-Version
- `dependencies`: Pakete die für den Betrieb nötig sind

**`[dependency-groups]`** — Gruppen von Extras.
- `dev`: Nur für Entwicklung (Tests, Linter, Debugger). Werden nicht mit der Anwendung ausgeliefert.

**Versionsconstraints:**
```toml
"django>=5.1"         # 5.1 oder neuer (empfohlen)
"django>=5.1,<6.0"    # Mindestens 5.1, aber unter 6.0
"django==5.1.3"       # Exakt diese Version (selten nötig)
"django~=5.1"         # Compatible Release: >=5.1, <5.2
```

### 6.2 Tool-Konfiguration hinzufügen

Viele Python-Tools lassen sich direkt in `pyproject.toml` konfigurieren — keine separaten Config-Files nötig. Füge folgende Sektionen hinzu:

```toml
# ── pytest Konfiguration ──────────────────────────────
[tool.pytest.ini_options]
# Django-Settings für Tests (ab Phase 2 relevant)
DJANGO_SETTINGS_MODULE = "config.settings"
# Wo pytest nach Tests sucht
testpaths = ["tests"]
# Ausgabe-Format: verbose
addopts = "-v"

# ── ruff Konfiguration ───────────────────────────────
[tool.ruff]
# Maximale Zeilenlänge
line-length = 88
# Python-Version für Syntax-Checks
target-version = "py312"

[tool.ruff.lint]
# Aktivierte Regel-Sets
select = [
    "E",    # pycodestyle errors (Stil-Fehler)
    "F",    # pyflakes (logische Fehler, z.B. unbenutzte Imports)
    "I",    # isort (Import-Sortierung)
    "UP",   # pyupgrade (modernere Syntax vorschlagen)
    "B",    # bugbear (häufige Bugs)
    "SIM",  # simplify (vereinfachbare Konstrukte)
]
```

### 6.3 uv.lock — das Lockfile

Neben `pyproject.toml` erstellt uv eine `uv.lock`-Datei. Die enthält die exakten, aufgelösten Versionen aller Pakete inklusive aller Unter-Dependencies.

**Du editierst diese Datei nie manuell.** Sie wird automatisch aktualisiert wenn du `uv add`, `uv remove`, oder `uv lock` aufrufst.

**Commit `uv.lock` in Git!** Es stellt sicher, dass jeder Entwickler (und der CI-Server) exakt die gleichen Paketversionen verwendet. Das ist wie `renv.lock` in R.

> **Übung 6.1:** Öffne deine `pyproject.toml` in VS Code. Füge die Tool-Konfigurationen für pytest und ruff hinzu. Schau dir `uv.lock` an (nur ansehen, nicht editieren) — du wirst sehen, wie viele Unter-Dependencies Django mitbringt.

---

## 7. ruff — Linter und Formatter

> **Analogie:** `ruff` ist wie `lintr` + `styler` in R in einem Tool, nur hundertmal schneller. Es findet Probleme (Linting) und formatiert deinen Code einheitlich (Formatting).

### 7.1 Grundbefehle

```bash
# Linting: Probleme finden
uv run ruff check .

# Linting: automatisch fixbare Probleme beheben
uv run ruff check . --fix

# Formatting: Code einheitlich formatieren
uv run ruff format .

# Prüfen ob alles formatiert ist (ohne zu ändern)
uv run ruff format . --check
```

### 7.2 Was ruff prüft (Beispiele)

Erstelle eine absichtlich schlechte Datei `bad_code.py`:

```python
import os
import sys
from datetime import datetime
import json

def process_sample( barcode,status ):
    x = 1
    if status == "registered":
        sample_list = []
        for i in range(10):
            sample_list.append(i)
        return True
    elif status == "received":
        return True
    else:
        return False

result=process_sample("S-001","registered")
```

Jetzt lauf `uv run ruff check bad_code.py`:

```
bad_code.py:1:8: F401 `os` imported but unused
bad_code.py:2:8: F401 `sys` imported but unused
bad_code.py:4:8: F401 `json` imported but unused
bad_code.py:7:5: F841 Local variable `x` is assigned to but never used
```

Und `uv run ruff format bad_code.py` formatiert:
- Leerzeichen um `=` und nach Kommas
- Einrückung konsistent
- Trailing Whitespace entfernt
- Leere Zeilen zwischen Definitionen

### 7.3 Wichtige Regeln kennen

| Code | Bedeutung | Beispiel |
|------|-----------|---------|
| F401 | Ungenutzter Import | `import os` ohne os zu nutzen |
| F841 | Ungenutzte Variable | `x = 1` ohne x zu nutzen |
| E501 | Zeile zu lang | Über 88 Zeichen |
| I001 | Import-Sortierung | stdlib → third-party → local |
| UP006 | Veraltete Syntax | `List[int]` → `list[int]` |
| B006 | Mutable Default-Argument | `def f(x=[]):` ist ein Bug! |

### 7.4 VS Code Integration

Wenn du die Ruff-Extension installiert hast und die Settings aus Abschnitt 3.2 konfiguriert hast, passiert das alles automatisch beim Speichern. Trotzdem ist es gut, die Befehle zu kennen — du brauchst sie für CI/CD-Pipelines und zum Debuggen.

> **Übung 7.1:** Erstelle die `bad_code.py` von oben. Lauf `uv run ruff check bad_code.py`. Fix die Probleme manuell oder mit `--fix`. Dann `uv run ruff format bad_code.py`. Vergleiche vorher/nachher.

---

## 8. pytest — Tests schreiben

> **Analogie:** `pytest` ist das `testthat` von Python. Wenn du `testthat` kennst, fühlst du dich sofort zuhause. Die Philosophie ist die gleiche: Tests sollen einfach zu schreiben, zu lesen, und auszuführen sein.

### 8.1 Grundstruktur

Erstelle einen `tests/`-Ordner mit einer leeren `__init__.py`:

```bash
mkdir tests
touch tests/__init__.py        # Linux
New-Item tests/__init__.py     # Windows
```

> **Was ist `__init__.py`?** Es markiert einen Ordner als Python-Package (importierbar). Auch wenn die Datei leer ist, muss sie da sein, damit pytest und Python den Ordner als Modul erkennen.

### 8.2 Dein erster Test

Erstelle `tests/test_barcode.py`:

```python
# tests/test_barcode.py

def generate_barcode(prefix: str, number: int) -> str:
    """Generiert einen Barcode im Format PREFIX-00042."""
    return f"{prefix}-{number:05d}"


# ── Tests ─────────────────────────────────────────────

def test_barcode_has_correct_format():
    barcode = generate_barcode("S", 42)
    assert barcode == "S-00042"

def test_barcode_pads_with_zeros():
    barcode = generate_barcode("S", 1)
    assert barcode == "S-00001"

def test_barcode_uses_prefix():
    barcode = generate_barcode("QC", 99)
    assert barcode.startswith("QC-")

def test_barcode_has_fixed_length():
    barcode = generate_barcode("S", 1)
    # Prefix (1-2 Zeichen) + "-" + 5 Ziffern
    assert len(barcode) >= 7
```

### 8.3 Tests ausführen

```bash
# Alle Tests
uv run pytest

# Erwartete Ausgabe:
# tests/test_barcode.py::test_barcode_has_correct_format PASSED
# tests/test_barcode.py::test_barcode_pads_with_zeros PASSED
# tests/test_barcode.py::test_barcode_uses_prefix PASSED
# tests/test_barcode.py::test_barcode_has_fixed_length PASSED
# =============== 4 passed in 0.01s ===============

# Verbose (zeigt jeden Test einzeln)
uv run pytest -v

# Nur eine bestimmte Testdatei
uv run pytest tests/test_barcode.py

# Nur einen bestimmten Test
uv run pytest tests/test_barcode.py::test_barcode_has_correct_format

# Bei erstem Fehler abbrechen
uv run pytest -x

# Letzte fehlgeschlagene Tests nochmal laufen lassen
uv run pytest --lf
```

### 8.4 assert vs. testthat

| testthat (R) | pytest (Python) | Prüft |
|-------------|-----------------|-------|
| `expect_equal(x, 42)` | `assert x == 42` | Gleichheit |
| `expect_true(x)` | `assert x` oder `assert x is True` | Wahrheitswert |
| `expect_error(f())` | `with pytest.raises(ValueError):` | Exception |
| `expect_length(x, 3)` | `assert len(x) == 3` | Länge |
| `expect_match(x, "S-")` | `assert "S-" in x` | Enthält String |
| `expect_null(x)` | `assert x is None` | Ist None |

**Exception-Tests:**
```python
import pytest

def test_receive_from_wrong_state_raises():
    s = Sample("S-001", "serum")
    s.status = "stored"  # nicht "registered"!

    with pytest.raises(ValueError, match="Cannot receive"):
        s.receive()
```

### 8.5 Fixtures (Test-Setups)

Fixtures sind wiederverwendbare Test-Vorbereitungen. Statt in jedem Test denselben Setup-Code zu schreiben, definierst du eine Fixture und pytest injiziert sie automatisch.

```python
import pytest

@pytest.fixture
def serum_sample():
    """Erstellt eine frische Serum-Probe für jeden Test."""
    return Sample("S-001", "serum")

@pytest.fixture
def received_sample(serum_sample):
    """Eine bereits empfangene Probe. Baut auf serum_sample auf."""
    serum_sample.receive()
    return serum_sample


# Tests nutzen Fixtures als Parameter:

def test_new_sample_is_registered(serum_sample):
    assert serum_sample.status == "registered"

def test_received_sample_can_be_stored(received_sample):
    received_sample.storage_location = "Freezer-A-03"
    received_sample.store()
    assert received_sample.status == "stored"
```

**Wie das funktioniert:** pytest sieht, dass `test_new_sample_is_registered` einen Parameter `serum_sample` hat. Es sucht eine Fixture mit dem gleichen Namen, ruft sie auf, und übergibt das Ergebnis als Argument. Jeder Test bekommt eine frische Instanz — Fixtures werden pro Test neu erstellt (Isolation).

**`conftest.py`:** Fixtures die in mehreren Testdateien gebraucht werden, legst du in `tests/conftest.py`. pytest findet sie dort automatisch — kein Import nötig:

```python
# tests/conftest.py — wird automatisch von allen Tests gefunden
import pytest

@pytest.fixture
def sample_data():
    return {
        "barcode": "S-2024-00001",
        "sample_type": "serum",
        "status": "registered",
    }
```

### 8.6 Tests in VS Code

Die Python-Extension erkennt pytest automatisch. Du siehst:
- Grüne/rote Dreiecke neben Testfunktionen (klicken zum Ausführen)
- Ein Test-Explorer in der Sidebar (Becher-Icon)
- Inline-Fehlermeldungen bei fehlgeschlagenen Tests

> **Übung 8.1:** Erstelle die `tests/test_barcode.py` von oben. Lass die Tests laufen mit `uv run pytest -v`. Füge einen absichtlich fehlenden Test hinzu (`assert 1 == 2`) und schau dir die Fehlermeldung an — pytest zeigt dir genau, welcher Wert erwartet wurde und welcher kam.

> **Übung 8.2:** Erstelle die Sample-Klasse aus Übung 4.1 und schreibe Tests dafür mit Fixtures. Prüfe: Neues Sample hat Status "registered". `receive()` setzt Status auf "received". `receive()` auf ein bereits empfangenes Sample wirft einen Fehler.

---

## 9. Git von der Kommandozeile

> **Warum Kommandozeile wenn VS Code das auch kann?** Zwei Gründe: Erstens verstehst du besser, was passiert. Zweitens brauchst du es für CI/CD-Pipelines und Server, wo es keine GUI gibt. Du musst nicht alles auf der Kommandozeile machen — aber die wichtigsten Befehle solltest du kennen.

### 9.1 Repository initialisieren

```bash
# Im Projekt-Root
cd ~/projects/ms-lims

# Git initialisieren (falls nicht schon durch uv init passiert)
git init

# .gitignore erstellen — SEHR WICHTIG
# Diese Dateien gehören NICHT ins Repository
```

Erstelle eine `.gitignore`:

```gitignore
# Python
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/

# Virtual Environment (wird von uv verwaltet)
.venv/

# IDE
.vscode/settings.json
.idea/

# OS
.DS_Store
Thumbs.db

# Environment variables (Passwörter etc.)
.env

# Database (lokale SQLite für Entwicklung)
db.sqlite3
```

### 9.2 Grundlegende Git-Befehle

```bash
# Status: Was hat sich geändert?
git status

# Alle Änderungen zum Staging hinzufügen
git add .

# Oder einzelne Dateien
git add pyproject.toml src/sample.py

# Commit erstellen
git commit -m "Initial project setup with uv"

# Log anzeigen (letzte Commits)
git log --oneline

# Diff anzeigen (was hat sich geändert?)
git diff                    # Ungestagete Änderungen
git diff --staged           # Gestagete Änderungen (vor Commit)
```

### 9.3 Typischer Workflow

```bash
# 1. Änderungen machen (Code schreiben)

# 2. Prüfen was sich geändert hat
git status

# 3. Linter/Formatter laufen lassen
uv run ruff check . --fix
uv run ruff format .

# 4. Tests laufen lassen
uv run pytest

# 5. Wenn alles grün: committen
git add .
git commit -m "Add Sample model with state validation"
```

### 9.4 Branches (Kurzüberblick)

```bash
# Neuen Branch erstellen und wechseln
git checkout -b feature/sample-model

# Zwischen Branches wechseln
git checkout main

# Branch-Übersicht
git branch

# Branch mergen (zurück auf main)
git checkout main
git merge feature/sample-model
```

### 9.5 VS Code + CLI kombinieren

**Der pragmatische Ansatz:** Nutze VS Code für Diffs (visuell viel besser), für Merge-Konflikte, und um schnell den Status zu sehen. Nutze die Kommandozeile für Commits, Branches, und alles was Scripting braucht. Beides zusammen ist mächtiger als nur eines von beiden.

> **Übung 9.1:** Initialisiere ein Git-Repository in deinem ms-lims-Projekt. Erstelle die `.gitignore`. Mache deinen ersten Commit mit allen bisherigen Dateien. Führe `git log --oneline` aus.

---

## 10. Abschluss-Übung: Alles zusammenbauen

Jetzt baust du alles aus dieser Phase zu einem Mini-Projekt zusammen. Das ist dein "Phase 1 Abschluss-Commit" — danach bist du bereit für Django.

### 10.1 Aufgabe

Erstelle ein Projekt mit folgender Struktur:

```
ms-lims/
├── .gitignore
├── .python-version
├── pyproject.toml              # mit Django, pytest, ruff
├── uv.lock
├── README.md
├── src/
│   └── ms_lims/
│       ├── __init__.py
│       └── sample.py           # Sample-Klasse
└── tests/
    ├── __init__.py
    ├── conftest.py             # Shared Fixtures
    └── test_sample.py          # Tests
```

### 10.2 Die Sample-Klasse (`src/ms_lims/sample.py`)

Implementiere eine einfache `Sample`-Klasse mit:
- Attributen: `barcode` (str), `sample_type` (str), `status` (str, default "registered"), `created_at` (datetime)
- Methode `receive()`: setzt Status auf "received" (nur wenn aktuell "registered")
- Methode `store(location: str)`: setzt Status auf "stored" und speichert den Lagerort (nur wenn "received")
- Methode `release()`: setzt Status auf "released_for_testing" (nur wenn "stored")
- Alle ungültigen Transitions werfen `ValueError`

### 10.3 Tests (`tests/test_sample.py`)

Schreibe Tests für:
- Neues Sample hat Status "registered"
- `receive()` funktioniert bei korrektem Ausgangsstatus
- `receive()` wirft Fehler bei falschem Ausgangsstatus
- `store()` braucht einen Lagerort
- Die vollständige Kette: registered → received → stored → released

### 10.4 Qualitätsprüfung

Bevor du committest:
```bash
# Code formatieren
uv run ruff format .

# Linting
uv run ruff check .

# Tests
uv run pytest -v

# Wenn alles grün:
git add .
git commit -m "Phase 1 complete: Project setup with Sample class and tests"
```

### 10.5 Erwartetes Ergebnis

Wenn du fertig bist, sollte das passieren:

```bash
$ uv run pytest -v
tests/test_sample.py::test_new_sample_is_registered PASSED
tests/test_sample.py::test_receive_changes_status PASSED
tests/test_sample.py::test_receive_from_wrong_state_raises PASSED
tests/test_sample.py::test_store_requires_location PASSED
tests/test_sample.py::test_full_lifecycle PASSED
================ 5 passed in 0.01s ================

$ uv run ruff check .
All checks passed!
```

---

## 11. Checkliste: Bin ich bereit für Phase 2?

Gehe diese Punkte durch. Wenn du alle mit "Ja" beantworten kannst, bist du bereit für Phase 2 (Django Fundamentals).

- [ ] Ich kann ein Terminal in VS Code öffnen und grundlegende Befehle nutzen (cd, ls, mkdir)
- [ ] Python ist installiert und `python --version` funktioniert
- [ ] VS Code ist für Python eingerichtet (Extension, Ruff, Formatting on Save)
- [ ] Ich verstehe, was Klassen, Decorators, und Type Hints in Python sind
- [ ] Ich kann ein Projekt mit `uv init` erstellen
- [ ] Ich kann Dependencies mit `uv add` hinzufügen
- [ ] Ich weiß, was eine virtuelle Umgebung ist und dass `uv run` sie automatisch nutzt
- [ ] Ich kann `pyproject.toml` lesen und die Sektionen zuordnen
- [ ] Ich kann `ruff` laufen lassen und Probleme beheben
- [ ] Ich kann Tests mit `pytest` schreiben und ausführen
- [ ] Ich kenne Fixtures und weiß, wofür `conftest.py` da ist
- [ ] Ich kann grundlegende Git-Operationen auf der Kommandozeile (init, add, commit, status)
- [ ] Mein Abschluss-Projekt ist committed: Sample-Klasse + Tests + sauberer Code

---

## Was kommt in Phase 2?

In Phase 2 ersetzt du deine handgeschriebene `Sample`-Klasse durch ein Django-Model, das automatisch eine PostgreSQL-Tabelle erstellt. Du lernst das Django-Projekt aufzusetzen, Views und Templates zu schreiben, und das Admin-Panel zu konfigurieren. Die Sample-Klasse, die du hier gebaut hast, wird zum Django-Model — und plötzlich hast du eine Web-UI, Datenbankpersistenz, und einen Admin-Bereich, fast ohne Mehrarbeit.
