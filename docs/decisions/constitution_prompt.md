Erstelle die Projekt-Constitution für das MS-LIMS.
Lies zuerst diese beiden Dokumente vollständig und extrahiere daraus
die governing principles:

- docs/decisions/ms-lims-requirements.md
- docs/decisions/ms-lims-tech-stack-referenz-v2.md

Strukturiere die Constitution in folgende Sections:

## Core Principles

Die fünf fundamentalen Prinzipien aus den Design-Leitprinzipien:

1. Manual-First — Automatisierung (Hamilton, Result-Parser, Task Queues)
   kommt erst wenn der manuelle Prozess digital abgebildet und verstanden ist.
2. Schneller-als-Excel — Wenn ein Workflow im LIMS länger dauert als in Excel,
   hat das Feature versagt. Messbar vor allem bei Probenregistrierung und
   Batch-Bildung.
3. Niedrige Einstiegshürde — Portable Deployment. Ein Kollege muss das LIMS
   innerhalb von 2 Minuten ausprobieren können. SQLite statt Postgres für v1.
   Kein Datenbankserver.
4. Modularität — Konkret und prüfbar (siehe eigene Section unten). lipidquant
   als eigenständiges Package ohne Django-Dependency.
5. YAGNI — Features wie Task Queues (django-q2, Celery), DRF,
   Hamilton-Integration werden erst eingebaut wenn konkreter Bedarf besteht,
   nicht prophylaktisch.

## Tech Stack Constraints (nicht verhandelbar ohne explizite Constitution-Änderung)

- Python 3.13.4
- Django 6.0.4
- SQLite als primäre Datenbank (Postgres nur bei konkretem Bedarf —
  Upgrade-Pfad offen)
- uv als Paketmanager
- pytest + pytest-django als Test-Framework
- ruff als Linter/Formatter (target-version py313)
- django-fsm-2 für State Machines (nicht viewflow.fsm)
- HTMX 2.x + Alpine.js 3.x via CDN für Frontend-Interaktivität
  (kein npm, kein Build-Step)
- Server-Side Rendering als Default (keine SPA)

## Design Patterns (pragmatisch, Django-aware)

- State Machine (django-fsm-2) ist das Herz — jede Sample-, Batch-, Run-Entity
  hat formalen Lifecycle mit auditierbaren Transitions.
- Fat Models, Skinny Views — Business-Logik in Models und Managers, nicht
  in Views. Views sind HTTP-Translatoren.
- Service Layer für apps-übergreifende Operationen — Code der zwei oder mehr
  Apps anfasst wohnt in {app}/services.py.
- Adapter Pattern für externe Systeme — Hamilton, MS-Vendor-Parser bekommen
  ein Protocol mit File-Exchange als Default und Mock für Tests.
- Pure Functions für Datentransformationen — Plate-Layout, QC-Bewertung,
  Result-Parsing, lipidquant-Math. Kein DB-Zugriff in diesen Funktionen.

Explizit NICHT verwendet (weil durch Django bereits abgedeckt):
- Explizites Repository Pattern — Django Manager/QuerySet ist das Repository.
- Unit of Work Klasse — Django transaction.atomic() ist die Unit of Work.
- Data Access Object — unnötige Abstraktion über dem ORM.

## Modularität — harte Regeln

Modularität ist nicht-verhandelbar. Diese Regeln sind prüfbar, nicht
interpretierbar:

1. Ein Konzept = eine Django-App. Aktuell geplante Apps:
   - parties       Institution, ResearchGroup, Person
   - projects      Project, SampleIntake
   - samples       OriginalSample, Extract
   - storage       Freezer, Drawer, Rack, Position
   - extractions   Protocol, Batch, MasterMix
   - analyses      MeasurementRun, AnalysisResult
   - instruments   Instrument, Adapter
   - lipidquant    als eigenständiges Python-Package, kein Django

   Weitere Apps (reporting, users, audit) können später nach diesen Regeln
   ergänzt werden.

2. Apps kommunizieren ausschließlich über {app}/api.py oder {app}/services.py.
   Direkte Imports aus anderen Apps' models.py oder views.py sind verboten.

3. Keine zirkulären Abhängigkeiten zwischen Apps. Bei unvermeidbarer Kopplung
   Django Signals verwenden.

4. lipidquant ist Django-frei. Keine django-Imports erlaubt. pandas/numpy ja.
   Prüfbar: grep -r "django" lipidquant/ muss leer sein.

5. Neue Features starten als eigene App, auch wenn sie klein beginnen.
   Kosten: 5 Minuten für startapp. Nutzen: isolierte Grenzen von Geburt an.

6. App-Größen-Warnung: Mehr als ~8 Models oder ~2000 Zeilen Code in einer
   App = Aufspaltungs-Signal.

Jede Spec und jeder Plan muss gegen diese Modularitäts-Regeln geprüft werden.

## Quality Standards

- Jedes Feature hat Tests. Keine Ausnahmen bei State-Transitions.
- ruff muss grün sein vor jedem Commit.
- Audit Trail für Sample-State-Änderungen auch ohne regulatorischen Zwang
  (django-fsm-log).
- Druckbare Dokumente (Probenlisten, Extraktionsprotokolle) sind
  First-Class-Citizens — nicht nachträglicher Export, sondern integraler
  Bestandteil der Module.

## Architektur-Leitplanken

- Drei Säulen: Sample Management, Extraction Management, Analysis Management.
- Die Sample State Machine ist das Herz — jeder Schritt einer Probe von
  Registrierung bis Befund ist formal, auditierbar, nachvollziehbar.
- Composition over Inheritance. Python Protocols statt tiefer
  Vererbungshierarchien.
- Funktional für Datentransformation (Plate-Layout, QC-Bewertung,
  Result-Parsing). OOP für Zustand/Identität (Models, Adapter, Repositories).

## Scope-Leitplanken (explizit außerhalb v1)

- Keine klinischen Patientenproben — nur biologische Forschungsproben.
- Kein multi-user, keine Netzwerk-Installation (nur lokal, Portable Folder).
- Keine Instrument-Direktanbindung (Hamilton, MS-Vendor-Parser) —
  File-Exchange als Default, Direktanbindung vertagt.
- Keine Regulierung (21 CFR Part 11, ISO 17025) als Anforderung — nur als
  Hintergrundwissen.

## Governance

- Die Constitution wird bei jeder /speckit.specify, /speckit.plan,
  /speckit.analyze als Bezugspunkt genutzt.
- Änderungen an der Constitution erfordern einen eigenen Commit mit Begründung.
- Bei Konflikt zwischen Constitution und einer neuen Spec: Constitution
  gewinnt, oder die Constitution wird explizit angepasst.
- Authoritative Quelle für detaillierte Requirements bleibt
  docs/decisions/ms-lims-requirements.md.
- Authoritative Quelle für Tech-Stack-Details bleibt
  docs/decisions/ms-lims-tech-stack-referenz-v2.md.

Schreibe die Constitution prägnant — jedes Prinzip mit 2-4 Sätzen Begründung,
nicht mehr. Die Details stehen in den verlinkten Dokumenten. Sprache: Englisch.
