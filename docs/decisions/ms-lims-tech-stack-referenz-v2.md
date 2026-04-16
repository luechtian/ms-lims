# MS-LIMS — Tech Stack & Architektur-Referenz

> **Zweck dieses Dokuments:** Referenz für alle Technologie-Entscheidungen, Design Patterns und Architektur-Prinzipien des geplanten lightweight LIMS für die MS-Facility. Wird fortlaufend aktualisiert, sobald Requirements konkreter werden.
>
> **Stand:** April 2026
> **Letzte Änderung:** Versionen fixiert, SQLite als Primär-DB, Extraction Pillar überarbeitet

---

## 1. Projekt-Vision

Ein **leichtgewichtiges, web-basiertes LIMS** (Laboratory Information Management System) für Massenspektrometrie-Labore. Kein Enterprise-Bloat, sondern ein fokussiertes Tool das drei Dinge exzellent kann:

1. **Sample Management** — Probeneingang, Registrierung, Lagerung, Lifecycle-Tracking
2. **Extraction Management** — Batch-Bildung, Plate/Tube-Layouts, druckbare Probenlisten & Extraktionsprotokolle, einfache Rückdokumentation ins LIMS. Hamilton-Anbindung optional als spätere Erweiterung.
3. **Analysis Management** — MS-Run-Tracking, Ergebnis-Import, QC-Bewertung

Das **Herz** des Systems ist die **Sample State Machine**: eine formale, auditierbare Zustandsmaschine die jeden Schritt einer Probe von der Registrierung bis zum Befund nachvollziehbar macht.

### Design-Leitprinzipien

> Wenn ein Workflow im LIMS länger dauert als in Excel, hat das Feature versagt.
> — Abgeleitet aus Anika Maria Weber, ResearchGate LIMS-Diskussion (März 2025)

> Starte einfach. SQLite, nicht Postgres. Manuelle Workflows, nicht Roboter-Integration. Druckbare Listen, nicht API-Anbindungen. Automatisierung kommt, wenn der manuelle Prozess verstanden und abgebildet ist.

---

## 2. Fixierte Versionen & Entwicklungsumgebung

| Komponente | Version / Tool | Anmerkung |
|---|---|---|
| **Python** | 3.13.4 | |
| **Django** | 6.0.4 | Dezember 2025 Release |
| **Datenbank (Primär)** | SQLite (eingebaut) | Mit WAL-Mode + PRAGMA-Tuning, siehe Abschnitt 3.3 |
| **Datenbank (Optional)** | PostgreSQL 16+ | Upgrade-Pfad wenn nötig, nicht für v1 |
| **Paketmanager** | uv | Bereits installiert |
| **Linter/Formatter** | ruff | |
| **Frontend (Interaktivität)** | HTMX 2.x + Alpine.js 3.x | CDN-Einbindung, kein Build-Step |
| **Test-Framework** | pytest + pytest-django | |
| **IDE** | VS Code | Mit Python + Ruff Extensions |
| **Primäres OS** | Windows 11 | Sekundär: Pop!_OS (Linux) |
| **Browser (Lab)** | Firefox | |
| **Versionskontrolle** | Git | VS Code Git Panel + CLI |

---

## 3. Tech Stack im Detail

### 3.1 Backend-Framework: Django

| Eigenschaft | Details |
|---|---|
| **Framework** | Django 6.0.4 |
| **Warum Django (statt FastAPI)** | Eingebauter Admin, ORM mit Migrations, Auth/Permissions, Session Management, Template Engine, Form-Validierung, `django-fsm-2` Ökosystem. Für ein internes Lab-Tool mit State Machine als Kern überwiegen Djangos Batteries-Included-Vorteile deutlich. |
| **Warum nicht FastAPI** | FastAPI wäre besser für eine reine API (SPA-Frontend, Microservices). Für unser LIMS mit Server-Side-Rendering, Admin-Panel und integrierter State Machine wäre zu viel Infrastruktur selbst zu bauen (Auth, Admin, Forms, Session). |
| **Warum nicht ASP.NET Core** | Kein eingebautes Admin-Panel. Steilere Lernkurve (DI Container, Startup-Konfiguration, Razor Pages). Mehr Boilerplate. Django bringt schneller sichtbare Ergebnisse — wichtig für ein Ein-Personen-Projekt. |
| **Server (Entwicklung)** | `runserver` (eingebaut) |
| **Server (Produktion)** | Gunicorn oder Uvicorn — erst relevant beim Deployment |

### 3.2 State Machine: django-fsm-2

| Eigenschaft | Details |
|---|---|
| **Paket** | `django-fsm-2` (v4.2+, aktiv maintainiert, MIT-Lizenz) |
| **Was es tut** | FSMField auf Django-Models, `@transition`-Decorators für deklarative State-Übergänge, Guard-Conditions, Permission-Checks pro Transition, Protected Fields |
| **Admin-Integration** | `FSMAdminMixin` — Transitions direkt als Buttons im Django Admin |
| **Audit-Logging** | `django-fsm-log` — automatisches Protokollieren jeder Transition (who, when, from, to, description) |
| **Warum nicht viewflow.fsm** | viewflow.fsm (Nachfolger von django-fsm) ist Teil eines größeren Workflow-Frameworks mit AGPL-Lizenz. django-fsm-2 ist fokussierter, MIT-lizenziert, Drop-in-Replacement |

### 3.3 Datenbank: SQLite (Primär)

| Eigenschaft | Details |
|---|---|
| **DBMS** | SQLite (eingebaut in Python 3.13) |
| **ORM** | Django ORM (eingebaut) |
| **Migrations** | Django Migrations (eingebaut) |
| **Warum SQLite** | Zero-Config, kein separater Server, Backup = Datei kopieren, perfekt für ein internes Lab-Tool mit wenigen gleichzeitigen Nutzern (2–10 Laboranten). Django 6.0 hat erstklassigen SQLite-Support mit `transaction_mode` und `init_command`. |
| **Warum nicht Postgres für v1** | Unnötige Komplexität für den Start. Docker-Setup, separater Server, Connection-Management — alles Infrastruktur die vom eigentlichen Ziel ablenkt. SQLite reicht für das erwartete Nutzungsprofil. |
| **Upgrade-Pfad** | Da Django ORM datenbank-agnostisch ist, ist der Wechsel zu PostgreSQL eine Änderung von ~5 Zeilen in `settings.py`. Kein Code-Rewrite nötig. |
| **Wann Postgres?** | Wenn: mehrere Server auf dieselbe DB zugreifen müssen, regelmäßige Lock-Timeouts auftreten, oder Postgres-spezifische Features gebraucht werden (Full-Text-Search, Array-Fields, LISTEN/NOTIFY). |

**Empfohlene SQLite-Konfiguration für Produktion:**

```python
# config/settings.py
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
        "OPTIONS": {
            "transaction_mode": "IMMEDIATE",
            "timeout": 5,
            "init_command": (
                "PRAGMA journal_mode=WAL;"
                "PRAGMA synchronous=NORMAL;"
                "PRAGMA mmap_size=134217728;"
                "PRAGMA journal_size_limit=27103364;"
                "PRAGMA cache_size=2000;"
            ),
        },
    }
}
```

**Was die PRAGMAs tun:**
- `journal_mode=WAL` — Write-Ahead-Logging: erlaubt gleichzeitiges Lesen und Schreiben (wichtigste Einstellung)
- `synchronous=NORMAL` — Guter Kompromiss zwischen Performance und Datensicherheit
- `transaction_mode=IMMEDIATE` — Schreib-Lock sofort holen statt erst beim Commit (verhindert "database is locked" Fehler)
- `mmap_size` — Memory-Mapped I/O für schnellere Reads
- `cache_size=2000` — Mehr Seiten im Cache halten

### 3.4 Frontend: Django Templates + HTMX + Alpine.js (Islands Architecture)

Die Frontend-Strategie folgt dem **Islands Architecture**-Prinzip: Die Basis ist serverseitig gerendertes HTML (Django Templates + HTMX). An Stellen, wo reichere Interaktivität gebraucht wird — z.B. ein visueller Freezer-Browser, Plate-Layout-Editor, Drag-and-Drop — werden **interaktive Inseln** mit Alpine.js (oder bei Bedarf React) eingebettet.

```
┌──────────────────────────────────────────────────┐
│  Django Template (HTMX)                          │
│  Probenlisten, Formulare, Status-Änderungen      │
│                                                  │
│  ┌─ Alpine.js Island ──────────────────────────┐ │
│  │ 🧊 Freezer-Browser: Drill-Down, Tooltips,  │ │
│  │    Hover, Farbcodierung, Suche-Highlight    │ │
│  └─────────────────────────────────────────────┘ │
│                                                  │
│  ┌─ Alpine.js Island ──────────────────────────┐ │
│  │ 🧫 Plate-Map: Visuelle Well-Zuordnung,     │ │
│  │    Position-Auswahl, Typ-Farbcodierung      │ │
│  └─────────────────────────────────────────────┘ │
│                                                  │
│  Django Template (HTMX)                          │
│  Audit-Log, Footer, Navigation                   │
└──────────────────────────────────────────────────┘
```

#### HTMX — Server-Driven Interaktivität (80% der UI)

| Eigenschaft | Details |
|---|---|
| **Paket** | HTMX 2.x |
| **Django-Integration** | `django-htmx` (v1.27+) — Middleware, CSRF-Handling |
| **Einsatz** | Probenlisten, Formulare, Status-Transitions, Suche, Inline-Edits, Pagination |
| **Prinzip** | Server rendert HTML-Fragmente, HTMX tauscht DOM-Elemente aus. Keine Client-Logik. |
| **Warum** | Kein Build-Tooling nötig. Kein State-Management im Client. Server-Logic bleibt in Python. |

#### Alpine.js — Client-Side Interaktivität (20% der UI)

| Eigenschaft | Details |
|---|---|
| **Paket** | Alpine.js 3.x (~15 KB, CDN-Einbindung, kein Build-Step) |
| **Einsatz** | Freezer-Browser (Drill-Down, Hover, Tooltips), Plate-Map (Position-Auswahl), Batch-Builder, Toggles, Tabs, Modals |
| **Prinzip** | Deklarative JS-Logik direkt in HTML-Attributen (`x-data`, `x-show`, `@click`). Fühlt sich an wie HTMX, aber für Client-seitige Zustände. |
| **Lernaufwand** | ~30 Minuten. Syntax ist minimal: `x-data` (State), `x-show` (Toggle), `x-for` (Loop), `@click` (Event), `x-transition` (Animation). |
| **Warum nicht React/Vue** | Kein npm, kein Build-Tooling, kein zweites Framework-Universum. Alpine lebt im Django-Template, nicht daneben. |

**Beispiel: Freezer-Schublade mit Drill-Down**

```html
<!-- Django Template mit Alpine.js Island -->
<div x-data="{ open: false }" class="drawer">
    <button @click="open = !open">
        Schublade 3 (23/50 belegt)
        <span x-show="!open">▶</span>
        <span x-show="open">▼</span>
    </button>
    <div x-show="open" x-transition>
        <!-- Rack-Inhalt via HTMX nachladen wenn Schublade geöffnet -->
        <div hx-get="/storage/freezer-a/drawer-3/racks/"
             hx-trigger="revealed"
             hx-swap="innerHTML">
            Lade Racks...
        </div>
    </div>
</div>
```

**Alpine.js + HTMX arbeiten zusammen:** Alpine verwaltet den Client-Zustand (Schublade auf/zu, Hover-State, Tab-Auswahl), HTMX holt die Daten vom Server (Rack-Inhalt, Proben-Details). Kein Konflikt, sie ergänzen sich.

#### React-Inseln — Nur bei Bedarf (Escape Hatch)

| Eigenschaft | Details |
|---|---|
| **Wann** | Nur wenn Alpine.js nicht reicht: komplexes Drag-and-Drop (Proben umlagern), Echtzeit-Canvas-Rendering, State-Management über viele Komponenten |
| **Wie** | Einzelne React-Komponente in `<div id="app">`, eingebettet in Django Template. Kommuniziert via JSON-API mit Django. |
| **Build-Tooling** | Vite (minimal, schnell). Nur für die React-Komponente, nicht für die ganze App. |
| **Aktuelle Einschätzung** | Wahrscheinlich nicht nötig für v1. Alpine.js + HTMX deckt den Freezer-Browser und Plate-Map ab. |

#### Weitere Frontend-Aspekte

| Eigenschaft | Details |
|---|---|
| **CSS** | Noch offen: Tailwind CSS, PicoCSS, DaisyUI, oder custom. Für MVP reicht minimales Custom-CSS. |
| **Print-Fähigkeit** | Wichtig für Extraktionsprotokolle und Probenlisten. CSS `@media print` für sauberes Drucklayout. |
| **SVG** | Server-generierte SVGs für Plate-Maps und Freezer-Visualisierungen. Alpine.js für Interaktivität darauf. |
| **Browser-Ziel** | Firefox (primär im Lab) |

### 3.5 API Layer: Django REST Framework

| Eigenschaft | Details |
|---|---|
| **Paket** | Django REST Framework (DRF) |
| **Zweck** | JSON API Endpunkte für Instrument-Integration (Hamilton, MS), ggf. externe Systeme |
| **Priorität** | Niedrig für v1 — erst relevant wenn Instrument-Anbindung kommt |
| **Features** | Serializers (Model → JSON), ViewSets, Authentication, Browsable API |

### 3.6 Task Queue (für async Operationen)

| Eigenschaft | Details |
|---|---|
| **Für MVP** | Nicht nötig — alles synchron |
| **Später (optional)** | django-q2 (nutzt SQLite als Broker!) oder Celery + Redis |
| **Zweck** | Result-File-Parsing, Report-Generierung, ggf. Hamilton-Kommunikation |
| **Prinzip** | YAGNI — erst einführen wenn tatsächlich async-Bedarf entsteht |

### 3.7 Instrument-Integration

#### Hamilton Starlet — optional, Zukunftsmusik

| Aspekt | Details |
|---|---|
| **Status** | Optional. Wird nicht in v1 implementiert. |
| **Grundidee** | LIMS generiert CSV-Worklist → VENUS liest sie → Hamilton schreibt Ergebnis-Dateien |
| **Voraussetzung** | Erst sinnvoll wenn der manuelle Extraktions-Workflow im LIMS stabil läuft. Die Hamilton-Anbindung automatisiert dann einen Prozess, der bereits digital abgebildet ist. |
| **Adapter-Pattern** | Vorbereitet: `InstrumentAdapter`-Interface mit `FileBasedHamiltonAdapter` (Produktion) und `MockHamiltonAdapter` (Tests). |
| **Offene Fragen** | Direkte Anbindung (PyHamilton, PyLabRobot) vs. File-Exchange. Entscheidung wird vertagt bis praktische Erfahrung mit dem manuellen Workflow vorliegt. |

#### Massenspektrometer — Referenz für später

| Vendor | Sequence-Import | Result-Export |
|---|---|---|
| **Thermo** (TraceFinder) | CSV Sample Lists | `.rsx` XML, CSV |
| **SCIEX** (Analyst/MultiQuant) | CSV/Text Batch | Delimited Text Export |
| **Waters** (MassLynx/TargetLynx) | CSV Worklists | LIMS Text/XML |
| **Agilent** (MassHunter) | CSV Sequence | "Copy to LIMS" CSV |

**Integrationsstrategie:** File-based als primärer Ansatz (vendor-agnostisch, einfach zu debuggen). Erst implementieren wenn der erste konkrete MS-Vendor feststeht.

### 3.8 DevOps & Tooling

| Tool | Zweck | Status |
|---|---|---|
| `uv` | Paketmanager | Installiert ✓ |
| `ruff` | Linter + Formatter | Einrichten in Phase 1 |
| `pytest` + `pytest-django` | Test-Framework | Einrichten in Phase 1 |
| `Git` | Versionskontrolle | VS Code Git Panel + CLI |
| `Docker` | Optional: nur für Postgres oder Deployment | Nicht für v1 nötig |
| `GitLab CI/CD` | Optional: automatisierte Tests | Später |

---

## 4. Architektur-Überblick

### 4.1 Schichten-Architektur

```
┌─────────────────────────────────────────────────────────────┐
│  Frontend                                                    │
│  Django Templates + HTMX (80%: Listen, Formulare, Status)   │
│  Alpine.js Islands (20%: Freezer-Browser, Plate-Map)         │
│  Print-Views für Probenlisten & Protokolle                   │
├─────────────────────────────────────────────────────────────┤
│  View Layer (Request → Response)                             │
│  Function-Based Views + Class-Based Views                    │
├─────────────────────────────────────────────────────────────┤
│  Service Layer (Business Logic)                              │
│  State Machine Transitions, Validierung, Batch-Logik         │
├─────────────────────────────────────────────────────────────┤
│  Model Layer (ORM + State Machine)                           │
│  Django ORM + django-fsm-2                                   │
├─────────────────────────────────────────────────────────────┤
│  SQLite (WAL-Mode)                                           │
│  Upgrade-Pfad → PostgreSQL bei Bedarf                        │
└─────────────────────────────────────────────────────────────┘
        ↕ Optional / Zukunft
  ┌─────────────┐    ┌──────────────────────┐
  │ Hamilton     │    │ MS Instruments       │
  │ Starlet      │    │ (File-based          │
  │ (optional)   │    │  Exchange)           │
  └─────────────┘    └──────────────────────┘
```

### 4.2 Django App-Struktur

```
ms-lims/
├── config/              # Django Settings, Root-URLs, WSGI
├── core/                # Shared: User-Erweiterungen, Audit-Log, Container-Model
├── samples/             # Säule 1: Sample CRUD, Storage, Lifecycle
├── extractions/         # Säule 2: Batch, Layout, Probenlisten, Protokolle
├── analyses/            # Säule 3: MS-Run, Results, QC-Bewertung
├── templates/           # Projekt-weite Templates (base.html, print-layouts)
├── static/              # CSS, JS, Icons
├── tests/               # Zentrale Test-Suite
├── db.sqlite3           # Die Datenbank (ein File!)
└── manage.py
```

---

## 5. Die drei Säulen im Detail

### 5.1 Säule 1 — Sample Management

**Scope:** Probeneingang, Registrierung, Barcode-Zuordnung, Lagerort-Verwaltung, Proben-Lifecycle.

**Kern-Features:**
- Sample-Registrierung (einzeln + Batch-Import)
- Barcode-Generierung (Custom-Prefix + Sequenz, z.B. S-2024-00001)
- Lagerort-Verwaltung (Freezer → Regal → Position)
- Status-Tracking via State Machine
- Suchfunktion (Barcode, Probentyp, Status, Datum)
- Proben-Historie (alle State-Änderungen chronologisch)

### 5.2 Säule 2 — Extraction Management

**Scope:** Batch-Bildung, Container-Layouts, Extraktionsplanung, druckbare Arbeitsdokumente, Rückdokumentation der durchgeführten Extraktion.

**Kern-Workflow (Manual-First):**

```
1. PLANEN       Analyst erstellt Extraktions-Batch im LIMS,
                wählt Proben aus, weist Positionen zu
                (Plate-Wells oder Tube-Rack-Positionen)
                     │
                     ▼
2. DRUCKEN      LIMS generiert druckbare Dokumente:
                • Probenliste (Barcode, Position, Probenart, Volumen)
                • Extraktionsprotokoll (Methode, Reagenzien, Schritte)
                • Ggf. Plate-Map als visuelle Übersicht
                     │
                     ▼
3. BENCH        Laborant führt Extraktion manuell an der Bench
                durch, nutzt ausgedruckte Dokumente als Leitfaden.
                Handschriftliche Notizen (Auffälligkeiten, Abweichungen)
                     │
                     ▼
4. DOKUMENTIEREN Laborant kommt zurück ans LIMS und dokumentiert:
                • Batch als "durchgeführt" markieren (ein Klick/Scan)
                • Ggf. Abweichungen notieren
                • Ggf. einzelne Proben als "fehlgeschlagen" markieren
                • State Machine setzt alle Proben → PREPARED
                     │
                     ▼
5. WEITER       Proben sind bereit für die MS-Analyse (Säule 3)
```

**Design-Ziel für Schritt 4:** Die Rückdokumentation muss so friktionsarm wie möglich sein. Ideal: Laborant scannt den Batch-Barcode, sieht die Übersicht, klickt "Extraktion abgeschlossen", fertig. Abweichungen nur wenn nötig. **Kein Mehraufwand gegenüber dem aktuellen Papier-Workflow.**

**Druckbare Dokumente — Anforderungen:**
- Probenliste: Tabellarisch, kompakt, mit Barcode, Position, Probenart, ggf. Patienteninfo
- Extraktionsprotokoll: Methode, Reagenzien, Schritte mit Checkboxen zum Abhaken
- Plate-Map (bei Plate-Workflows): Visuelle Draufsicht mit farbcodierten Probentypen
- Alle Dokumente mit Batch-ID, Datum, Analyst-Name, Druckzeitpunkt
- CSS `@media print` für sauberes Drucklayout ohne Browser-Chrome

**Hamilton-Anbindung (Zukunft/Optional):**
- Ersetzt Schritte 2–3 durch automatisierte Pipettierung
- LIMS generiert CSV-Worklist statt druckbarer Liste
- VENUS führt aus, Hamilton schreibt Ergebnis-Dateien
- Schritt 4 wird automatisiert: LIMS parsed Hamilton-Output
- Adapter-Pattern vorbereitet, aber nicht implementiert in v1

### 5.3 Säule 3 — Analysis Management

**Scope:** MS-Run-Tracking, Sequence-Generierung, Ergebnis-Import, QC-Bewertung, Review/Approval-Workflow.

**Kern-Features (v1 — vereinfacht):**
- MS-Run erstellen (verknüpft mit Extraktions-Batch + Instrument + Methode)
- Manuelle Ergebnis-Eingabe oder CSV-Import
- QC-Bewertung (Pass/Fail gegen konfigurierbare Kriterien)
- Review/Approval-Workflow mit elektronischer Signatur (Segregation of Duties)

**Erweitert (später):**
- Vendor-spezifische Sequence-File-Generierung
- Automatisches Result-File-Parsing
- Kalibrierungskurven-Management
- Ion Ratio Monitoring
- Reassay Decision Matrix

---

## 6. Datenmodell (Kern-Entitäten)

### 6.1 Entitäten-Überblick

```
Sample ──→ ContainerPosition ──→ Container ──→ ExtractionBatch
   │                                                │
   │                                          AnalysisRun
   │                                                │
   └────────────────────────── AnalysisResult ──────┘
```

### 6.2 Zentrale Models

**Sample** — Barcode, Probentyp, Status (FSMField), Metadaten, Timestamps. Die zentrale Entität.

**Container** — Polymorpher Container-Typ: `plate_96`, `plate_384`, `tube_rack`, `single_tube`. Barcode, Capacity, Layout-Format. Ermöglicht sowohl Plate-basierte als auch Tube-basierte Workflows.

**ContainerPosition** — Verknüpft Sample mit Container-Position (z.B. "Well A3" oder "Rack-Position 7"). Timestamped für Umzugs-Historie.

**ExtractionBatch** — Gruppiert Container/Samples für die Extraktion. Verknüpft mit Methode, Analyst, Status (eigene State Machine). Basis für druckbare Dokumente.

**AnalyticalMethod** — Zentrale Konfigurationsentität. Definiert Plate-Layout-Template, QC-Regeln, Akzeptanzkriterien. Analyst wählt Methode → System konfiguriert downstream.

**AnalysisRun** — MS-Lauf. Verknüpft mit ExtractionBatch, Instrument, Methode, Status.

**AnalysisResult** — Messwerte pro Analyt pro Sample.

### 6.3 Container-Abstraktion (Plate/Tube-agnostisch)

```python
class Container:
    container_type: "plate_96" | "plate_384" | "tube_rack" | "single_tube"
    barcode: str
    capacity: int        # 96, 24, 1, ...
    layout: str          # "grid_8x12", "grid_4x6", "linear", "single"

class ContainerPosition:
    container: ForeignKey(Container)
    position_label: str  # "A1" bei Plate, "1" bei Rack, "—" bei Einzeltube
    sample: ForeignKey(Sample)
    assigned_at: DateTimeField
```

Bei gemischten Workflows (Tube-Extraktion → Plate für Autosampler) wechselt die Probe den Container. Die History ist über timestamped ContainerPositions nachvollziehbar.

---

## 7. Design Patterns

### 7.1 State Machine Pattern (Kern-Pattern)

Dual koordinierte State Machines für Samples und Batches.

**Sample-States:**
```
REGISTERED → RECEIVED → STORED → RELEASED_FOR_TESTING →
QUEUED_FOR_PREP → IN_PREPARATION → PREPARED →
QUEUED_FOR_ANALYSIS → IN_ANALYSIS → ACQUIRED →
PROCESSED → IN_REVIEW → APPROVED → REPORTED → ARCHIVED
```

**Rückwärts-Transitions:** Processed → QUEUED_FOR_ANALYSIS (Reassay), Processed → QUEUED_FOR_PREP (Re-Extraktion), IN_REVIEW → PROCESSED (Investigation). Jeder aktive State kann zu ON_HOLD oder CANCELLED wechseln.

**Batch-States:**
```
CREATED → PLANNED → IN_PREPARATION → PREPARED →
QUEUED_FOR_INSTRUMENT → RUNNING → ACQUIRED →
PROCESSED → REVIEWED → CLOSED
```

**Kaskadierung:** Batch-Transitions kaskadieren auf Member-Samples. Einzelne Samples können individuell überschrieben werden.

**Implementierung:** `django-fsm-2` mit `@transition`-Decorators, Guard-Conditions, Permission-Checks, und `django-fsm-log` für immutables Audit-Logging.

### 7.2 Adapter Pattern (Instrument-Integration — Zukunft)

```python
class InstrumentAdapter(Protocol):
    def generate_worklist(self, batch: ExtractionBatch) -> Path: ...
    def parse_results(self, result_file: Path) -> list[RawResult]: ...

class HamiltonFileAdapter:     # Zukunft: CSV-Dateien für Hamilton
    ...

class ManualExtractionAdapter: # v1: Generiert druckbare Probenliste
    ...

class MockAdapter:             # Tests: Simuliert Ergebnisse
    ...
```

Auch der manuelle Workflow kann als Adapter modelliert werden — der Output ist ein druckbares Dokument statt einer CSV-Worklist. Gleiches Interface, andere Implementierung.

### 7.3 Repository Pattern (implizit durch Django ORM)

Django's Manager/QuerySet-System ist ein de-facto Repository:

```python
class SampleQuerySet(models.QuerySet):
    def pending_extraction(self):
        return self.filter(status="released_for_testing")

    def by_method(self, method):
        return self.filter(extraction_batch__method=method)
```

### 7.4 Event Sourcing (für Audit Trail)

Jede State-Transition generiert einen immutablen Event-Record via `django-fsm-log`. Erfüllt 21 CFR Part 11 §11.10(e).

### 7.5 Funktional vs. OOP (pragmatischer Mix)

| Wenn es... | Dann... | Beispiel |
|---|---|---|
| Daten transformiert | **Funktional** (pure functions) | Plate-Layout-Berechnung, QC-Bewertung, Result-Parsing |
| Zustand/Identität hat | **OOP** (Klassen) | Sample-Model, Adapter, DB-Repositories |
| Externe Ressource verwaltet | **OOP** | Datenbank-Verbindung, Instrument-Kommunikation |
| Validierungsregeln sind | **Funktional** | Akzeptanzkriterien, Barcode-Format-Prüfung |

Keine tiefen Vererbungshierarchien. Composition over Inheritance. Python Protocols statt abstrakte Basisklassen.

---

## 8. Python-Bibliotheken (Dependency Map)

### 8.1 Kern-Dependencies (Produktion)

```toml
[project]
requires-python = ">=3.13"
dependencies = [
    "django>=6.0,<7.0",
    "django-fsm-2>=4.2",           # State Machine
    "django-fsm-log>=4.0",         # Audit Trail für Transitions
    "django-htmx>=1.27",           # HTMX-Integration
    "django-environ>=0.11",        # Environment Variables (Settings)
]

# Alpine.js 3.x wird via CDN eingebunden (kein Python-Paket):
# <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3/dist/cdn.min.js"></script>
# Kein npm, kein Build-Step nötig.
```

### 8.2 Entwicklungs-Dependencies

```toml
[dependency-groups]
dev = [
    "pytest>=8.0",
    "pytest-django>=4.9",
    "ruff>=0.8",
    "django-extensions>=3.2",      # shell_plus, etc.
    "factory-boy>=3.3",            # Test-Fixtures (Factory Pattern)
    "django-debug-toolbar>=4.0",   # Performance & Query Debugging
]
```

### 8.3 Später bei Bedarf

```toml
# Instrument-Integration:
# djangorestframework   — REST API für Hamilton/MS
# pandas                — CSV/Excel Parsing für Worklists/Results
# lxml                  — XML Parsing (TraceFinder .rsx, Waters .xml)
# openpyxl              — Excel-Dateien lesen/schreiben
# watchdog              — Filesystem Event Monitoring
#
# Reporting:
# weasyprint            — HTML → PDF für druckbare Dokumente
# django-weasyprint     — Django-Integration
```

---

## 9. Lernpfad (Phasen-Übersicht)

| Phase | Thema | Zeitraum | Status |
|---|---|---|---|
| **Vorbereitung** | Offizielles Django-Tutorial (Teile 1–7) | 3–5 Tage | ⬅ Aktuell |
| **Phase 1** | Python-Tooling & Umgebung (uv, pytest, ruff, Git CLI) | 2–4 Tage | Dokument erstellt ✓ |
| **Phase 2** | Django Fundamentals (Models, Admin, Views, Templates, Forms, Tests) | 5–7 Tage | Dokument erstellt ✓ |
| **Phase 3** | State Machine (django-fsm-2, Audit Trail, Sample Lifecycle) | 3–5 Tage | Geplant |
| **Phase 4** | HTMX (dynamische UI) | 3–5 Tage | Geplant |
| **Phase 5** | LIMS-Skeleton (drei Säulen zusammenbauen) | 1 Woche | Geplant |
| **Phase 6** | Print-Views & Extraktionsprotokolle | 2–3 Tage | Geplant |
| **Phase 7** | Django REST Framework + erste Instrument-Integration | Optional | Geplant |

> **Hinweis:** Phase 3 (PostgreSQL + Docker) aus dem ursprünglichen Plan entfällt. SQLite eliminiert diesen Schritt komplett. Die State Machine rückt nach vorne.

---

## 10. Offene Entscheidungen

| Entscheidung | Optionen | Tendenz |
|---|---|---|
| CSS-Framework | Tailwind CSS, PicoCSS, DaisyUI, Custom | Offen |
| Barcode-Generierung | Auto-Increment, UUID, Custom-Prefix+Sequenz | Custom-Prefix+Sequenz |
| Plate-Layout-Editor | Alpine.js + SVG, React-Insel, Admin-only | Alpine.js + SVG |
| Freezer-Browser | Alpine.js + HTMX, React-Insel | Alpine.js + HTMX |
| PDF-Generierung (Protokolle) | WeasyPrint, xhtml2pdf, Browser Print | WeasyPrint (HTML→PDF) |
| Batch-Rückdokumentation | Barcode-Scan, Klick-Bestätigung, Checklist | Offen — UX-Prototyp nötig |
| Hamilton-Integration | File-Exchange, PyHamilton, PyLabRobot | Vertagt |
| Erster MS-Vendor-Parser | Thermo, SCIEX, Waters, Agilent | Abhängig von Instrument |
| Deployment | Portable Folder, Docker, bare metal | Portable Folder (Tendenz) |
| CI/CD | GitLab CI, GitHub Actions | GitLab CI (Chromsystems) |
| Task Queue (wenn nötig) | django-q2 (SQLite-kompatibel), Celery | django-q2 |

---

## 11. Referenz-Architekturen

| Projekt | Was du lernen kannst | Stack |
|---|---|---|
| **NEMO** (github.com/usnistgov/NEMO) | Exzellent strukturierte Django Lab-App | Django, PostgreSQL |
| **iSkyLIMS** (github.com/BU-ISCIII/iskylims) | State Machines für Lab-Workflows | Django |
| **SENAITE** (senaite.com) | Workflow-System mit formaler State Machine | Python/Plone |
| **Watson LIMS** (kommerziell) | Goldstandard Bioanalytik: Method-centric Design | Referenz für Konzepte |

---

## 12. Zusammenfassung: Warum dieser Stack?

Der Stack ist gewählt für **einen Entwickler mit Lab-Hintergrund, der ein fokussiertes internes Tool baut**.

**Django** weil es das meiste mitbringt und die Referenz-Implementierungen Django nutzen.

**django-fsm-2** weil die State Machine das Herz ist und dieses Paket genau dafür gemacht ist.

**SQLite** weil es für ein internes Lab-Tool mit wenigen Nutzern ausreicht, die Komplexität eines separaten DB-Servers eliminiert, und der Upgrade-Pfad zu Postgres offen bleibt.

**HTMX + Alpine.js** weil HTMX Server-Side-Rendering beibehält und Alpine.js reichere Interaktivität ermöglicht (Freezer-Browser, Plate-Maps) — ohne Build-Tooling, ohne npm, ohne zweites Framework-Universum. React als Escape Hatch wenn nötig, aber wahrscheinlich nicht für v1.

**Manual-First für Extraktion** weil der Papier-Workflow verstanden und digital abgebildet sein muss, bevor Automatisierung (Hamilton) Sinn macht. Druckbare Probenlisten und einfache Rückdokumentation sind der erste Schritt.

**File-based Instrument-Integration** (wenn es soweit ist) weil es mit jedem Vendor funktioniert und einfach zu debuggen ist.

Das Ergebnis: **Ein System das tief in seinen drei Säulen ist und bewusst flach überall sonst.**

---

## Appendix A — Regulatorische Referenz (nachrangig)

> **Hinweis:** Das LIMS wird voraussichtlich nicht in einem regulierten Umfeld eingesetzt. Die folgenden Informationen sind als Hintergrundwissen dokumentiert, nicht als Anforderungen für die Implementierung. Falls sich der Einsatzkontext ändert, kann dieser Appendix zum Anforderungskatalog aufgewertet werden.

**Relevante Standards (Kurzreferenz):** FDA 21 CFR Part 11 (Audit Trail, E-Signatures, Access Control), ISO 17025 (Chain of Custody, Kalibrierung), ISO 15189 (klinisches Labor), ALCOA+ (Datenintegrität), GAMP 5 (Validierung).

**Typische Compliance-Features:** Immutable Audit Trail, Unique User Accounts, NTP-Timestamps, Soft-Delete statt Hard-Delete, Segregation of Duties, elektronische Signaturen.

**Trotzdem sinnvoll für jedes LIMS (auch nicht-reguliert):** Ein Audit Trail (wer hat wann was geändert) und rollenbasierte Berechtigungen sind auch ohne regulatorischen Zwang gute Praxis — sie helfen beim Debugging, bei der Nachvollziehbarkeit, und beim Vertrauen der Nutzer in das System.

---

## Appendix B — MS-Lab-spezifische Features (Referenz für später)

> **Hinweis:** Diese Features sind relevant wenn das LIMS über das MVP hinaus wächst. Sie sind hier als Ideenspeicher dokumentiert.

**Plate-Layout-Management** — Visuelle Plate-Map, strukturiertes Layout (Blanks, Kalibratoren, QCs, Unknowns), reusable Templates pro Methode.

**Kalibrierungskurven** — Regressionsparameter, Back-Calculation, Auto-Flagging (±15%, ±20% bei LLOQ), Kalibrator-Ausschluss mit Begründung.

**QC-Management** — Solvent Blanks (Carryover), Matrix Blanks (Interferenz), QC-Level, IS-Response-Tracking, Ion Ratios (±20%).

**Sequence-File-Generierung** — Vendor-spezifische Formate (Xcalibur, Analyst, MassLynx, MassHunter).

**Result-File-Parsing** — Vendor-spezifische Formate parsen, Auto-Match gegen LIMS-Records.

**Analytical Method als Config-Objekt** — Methode definiert Layout, QC-Regeln, Akzeptanzkriterien, Sequence-Ordering, MRM-Transitions. Analyst wählt Methode → alles konfiguriert sich downstream. (Pattern von Watson LIMS.)

---

## Appendix C — Deployment-Strategie: Portable Folder

> **Kernidee:** SQLite + Django ermöglicht ein LIMS das als einfacher Ordner verteilt werden kann — ohne Installation, ohne Administrator-Rechte, ohne Datenbank-Server. Die Einstiegshürde für Kollegen zum Ausprobieren soll maximal niedrig sein.

### Empfohlen: Portable Folder (Level 1)

Ein Ordner der alles enthält — Python, App, Dependencies, Datenbank:

```
ms-lims-portable/
├── start-lims.bat              # Doppelklick → LIMS startet + Browser öffnet
├── python/                     # Python Embeddable Package (~30 MB, von python.org)
│   ├── python.exe
│   ├── python313.dll
│   └── ...
├── app/                        # Django-Projekt
│   ├── manage.py
│   ├── config/
│   ├── samples/
│   ├── extractions/
│   ├── analyses/
│   └── ...
├── venv/                       # Vorinstallierte Dependencies (Django, etc.)
├── db.sqlite3                  # Datenbank (reist mit!)
└── README.txt                  # Kurzanleitung
```

**Startskript (start-lims.bat):**

```batch
@echo off
echo ========================================
echo   MS-LIMS starten...
echo   Browser oeffnet sich automatisch.
echo   Dieses Fenster NICHT schliessen!
echo ========================================
cd /d "%~dp0"
start http://127.0.0.1:8000
python\python.exe app\manage.py runserver 127.0.0.1:8000 --noreload
pause
```

**Hürde für den User:** Ordner kopieren (USB-Stick, Netzlaufwerk, ZIP), `start-lims.bat` doppelklicken. Fertig. Vergleichbar mit portablen Apps wie Notepad++ Portable oder KeePass.

**Voraussetzungen auf dem Zielrechner:** Windows 10/11. Sonst nichts — kein Python, kein pip, keine Admin-Rechte.

### Szenarien

| Szenario | Was passiert |
|---|---|
| **Kollege will ausprobieren** | Ordner kopieren, .bat doppelklicken, fertig |
| **Eigene Testdaten** | Jeder hat seine eigene `db.sqlite3` im Ordner |
| **Daten teilen** | `db.sqlite3` kopieren/austauschen |
| **Frisch anfangen** | `db.sqlite3` löschen, `manage.py migrate` → leere DB |
| **Update verteilen** | Neuen Ordner verteilen, alte `db.sqlite3` reinkopieren |

### Einschränkungen

**Nur lokal:** Das LIMS läuft als lokaler Webserver auf `127.0.0.1:8000`. Nur der eigene Rechner kann zugreifen. Für Netzwerk-Betrieb (mehrere Laboranten gleichzeitig) braucht es ein Server-Deployment — das ist ein anderes Szenario.

**Nur Windows:** Das Embeddable Python Package ist Windows-spezifisch. Für Linux/macOS braucht der User eine Python-Installation. Für das Lab (Windows-Umgebung) ist das kein Problem.

**Kein Auto-Update:** Neue Versionen müssen manuell als neuer Ordner verteilt werden. Für ein internes Tool ist das akzeptabel.

### Alternative: PyInstaller (Level 2, optional)

PyInstaller kann Django in eine einzelne .exe bündeln — maximale Einfachheit für den User (eine Datei statt eines Ordners). Aber: höherer Aufwand für den Entwickler (Hidden-Imports konfigurieren, Templates/Static-Files manuell einbinden, plattformspezifische Builds). Lohnt sich erst wenn das LIMS stabil ist und breit verteilt werden soll.

### Auswirkung auf die Architektur

Die Portable-Folder-Strategie bestätigt die SQLite-Entscheidung: Mit PostgreSQL wäre dieses Deployment-Modell unmöglich. SQLite ist nicht nur "gut genug" — es ist ein Feature das die Verteilbarkeit des LIMS grundlegend ermöglicht.
