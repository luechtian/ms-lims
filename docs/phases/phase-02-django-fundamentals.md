# Phase 2 — Django Fundamentals

**Ziel:** Am Ende dieser Phase hast du eine laufende Django-Webanwendung mit einem `Sample`-Model in PostgreSQL, einem konfigurierten Admin-Panel, einfachen Views und Templates, und einem Verständnis davon, wie Django Request → URL → View → Template → Response orchestriert.

**Zeitaufwand:** 5–7 Tage

**Voraussetzungen:** Phase 1 abgeschlossen (uv, pytest, ruff, Python-Grundlagen)

---

## Inhaltsverzeichnis

1. [Was ist Django? (Architektur-Überblick)](#1-was-ist-django-architektur-überblick)
2. [Django-Projekt erstellen](#2-django-projekt-erstellen)
3. [Die Projektstruktur verstehen](#3-die-projektstruktur-verstehen)
4. [Settings konfigurieren](#4-settings-konfigurieren)
5. [Apps — Djangos Modularisierung](#5-apps--djangos-modularisierung)
6. [Models — Datenbank ohne SQL](#6-models--datenbank-ohne-sql)
7. [Migrations — Versionskontrolle für die Datenbank](#7-migrations--versionskontrolle-für-die-datenbank)
8. [Die Django Shell — dein interaktives Labor](#8-die-django-shell--dein-interaktives-labor)
9. [Django Admin — dein geschenktes Backend](#9-django-admin--dein-geschenktes-backend)
10. [URLs — das Routing-System](#10-urls--das-routing-system)
11. [Views — Request rein, Response raus](#11-views--request-rein-response-raus)
12. [Templates — HTML mit Superkräften](#12-templates--html-mit-superkräften)
13. [Statische Dateien (CSS/JS)](#13-statische-dateien-cssjs)
14. [Formulare — Daten vom User entgegennehmen](#14-formulare--daten-vom-user-entgegennehmen)
15. [Tests in Django](#15-tests-in-django)
16. [Abschluss-Übung: Mini-LIMS](#16-abschluss-übung-mini-lims)
17. [Checkliste: Bin ich bereit für Phase 3?](#17-checkliste-bin-ich-bereit-für-phase-3)

---

## 1. Was ist Django? (Architektur-Überblick)

Django ist ein Python-Web-Framework das dem **MTV-Pattern** folgt: Model, Template, View. Das ist fast identisch mit MVC (Model-View-Controller), nur anders benannt:

| MVC (C#, allgemein) | Django (MTV) | Was es tut |
|---------------------|-------------|------------|
| Model | **Model** | Datenstruktur + Datenbankzugriff |
| View | **Template** | HTML-Darstellung |
| Controller | **View** | Geschäftslogik, verbindet Model mit Template |

> **Merke:** Djangos "View" ist was in C#/MVC der "Controller" wäre. Djangos "Template" ist was in MVC die "View" wäre. Die Benennung ist verwirrend, aber die Konzepte sind identisch.

### Wie ein Request durch Django fließt

```
Browser                Django
──────                 ──────
GET /samples/  ──→  1. URL-Router    (urls.py: welcher View?)
                    2. View          (views.py: Daten holen, Logik)
                    3. Model         (models.py: Datenbank-Query)
                    4. Template      (sample_list.html: HTML rendern)
               ←──  5. HTTP Response (fertiges HTML zurück)
```

Das ist der Zyklus den du in dieser Phase von Grund auf baust.

### Warum Django für dein LIMS?

Django bringt Dinge mit, die du sonst selbst bauen müsstest:
- **ORM** — Datenbankzugriff ohne SQL (wie Entity Framework in C#)
- **Admin-Panel** — CRUD-Interface für alle Models, sofort einsatzbereit
- **Auth-System** — User, Gruppen, Permissions (21 CFR Part 11 Basis)
- **Migrations** — Versionskontrolle für Datenbankänderungen
- **Form-Validierung** — Server-seitige Eingabeprüfung
- **CSRF-Schutz** — Sicherheit gegen Cross-Site-Angriffe (eingebaut)

---

## 2. Django-Projekt erstellen

### 2.1 Startpunkt: Dein Phase-1-Projekt

Du hast aus Phase 1 bereits ein Projekt mit `uv`. Wir bauen darauf auf.

```bash
cd ~/projects/ms-lims

# Falls Django noch nicht installiert ist:
uv add django

# Django-Projekt erstellen
# Der Punkt am Ende ist wichtig — er sagt "hier in diesem Ordner"
uv run django-admin startproject config .
```

> **Warum `config`?** Django erstellt einen Ordner mit Settings, URLs und WSGI-Konfiguration. Viele Tutorials nennen ihn genauso wie das Projekt (z.B. `ms_lims`), aber `config` ist klarer — es ist die Konfiguration, nicht die Anwendungslogik.

> **Warum der Punkt `.`?** Ohne den Punkt erstellt Django einen zusätzlichen Wrapper-Ordner (`ms-lims/ms-lims/config/`). Mit dem Punkt bleibt die Struktur flach.

### 2.2 Überprüfen: Server starten

```bash
uv run python manage.py runserver
```

Öffne deinen Browser auf **http://127.0.0.1:8000/** — du solltest eine Django-Willkommensseite sehen ("The install worked successfully!").

**Stoppen:** `Ctrl+C` im Terminal.

> **Was ist `manage.py`?** Das ist Djangos Kommandozentrale — wie ein Schweizer Taschenmesser. Alles was du mit Django auf der Kommandozeile machst, geht über `python manage.py <befehl>`. Du wirst es hundertfach benutzen.

> **Übung 2.1:** Erstelle das Django-Projekt und starte den Server. Öffne die Willkommensseite im Browser. Stoppe den Server mit `Ctrl+C`.

---

## 3. Die Projektstruktur verstehen

Nach `startproject` sieht dein Ordner so aus:

```
ms-lims/
├── config/                  # Django-Konfiguration
│   ├── __init__.py          # Macht config zu einem Python-Package
│   ├── asgi.py              # ASGI-Einstiegspunkt (async Server)
│   ├── settings.py          # ⭐ ZENTRALE Konfiguration
│   ├── urls.py              # ⭐ URL-Routing (Haupt-Router)
│   └── wsgi.py              # WSGI-Einstiegspunkt (sync Server)
├── manage.py                # ⭐ Kommandozeilen-Tool
├── pyproject.toml           # Dein Paketmanager (aus Phase 1)
├── uv.lock
├── src/                     # Dein Code aus Phase 1
│   └── ms_lims/
├── tests/                   # Deine Tests aus Phase 1
└── .gitignore
```

**Die drei Dateien die du ständig anfasst:**
- `config/settings.py` — hier konfigurierst du alles: Datenbank, installierte Apps, Middleware, Templates
- `config/urls.py` — hier sagst du Django: "Wenn jemand `/samples/` aufruft, geh zu diesem View"
- `manage.py` — hier führst du Befehle aus (Server starten, Migrationen, Shell öffnen)

**Die zwei Dateien die du ignorieren kannst:**
- `asgi.py` und `wsgi.py` — Einstiegspunkte für Produktions-Server. Die fasst du erst an, wenn du deployest.

---

## 4. Settings konfigurieren

`config/settings.py` ist die Schaltzentrale. Öffne die Datei und mache dich mit den wichtigsten Einstellungen vertraut.

### 4.1 SECRET_KEY

```python
SECRET_KEY = 'django-insecure-...'
```

Das ist ein kryptographischer Schlüssel für Sessions, CSRF-Tokens, und Passwort-Hashing. Für Entwicklung ist der generierte Wert okay. **Für Produktion muss er geheim sein und aus einer Umgebungsvariable kommen** — das machen wir später.

### 4.2 DEBUG

```python
DEBUG = True
```

Im Debug-Modus zeigt Django detaillierte Fehlermeldungen mit Stacktrace im Browser. **In Produktion MUSS das `False` sein** — sonst sehen User interne Fehlermeldungen und Datenbankdetails.

### 4.3 INSTALLED_APPS

```python
INSTALLED_APPS = [
    'django.contrib.admin',          # Admin-Panel
    'django.contrib.auth',           # User & Permissions
    'django.contrib.contenttypes',   # Content-Type-Framework
    'django.contrib.sessions',       # Session-Management
    'django.contrib.messages',       # Flash-Messages
    'django.contrib.staticfiles',    # CSS/JS-Dateien
]
```

**Jede Django-App die du erstellst oder installierst, muss hier eingetragen werden.** Das ist wie `library()` in R oder `using` in C# — Django weiß erst von einer App, wenn sie hier steht.

### 4.4 DATABASES (später: PostgreSQL)

Standardmäßig nutzt Django SQLite:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

Das reicht für den Anfang dieser Phase. In Phase 3 stellen wir auf PostgreSQL um. SQLite ist eine Datei-basierte Datenbank — kein Server nötig, perfekt zum Lernen.

### 4.5 Sprache und Zeitzone anpassen

Ändere die Defaults auf deutsche Lokalisierung:

```python
LANGUAGE_CODE = 'de-de'      # War: 'en-us'
TIME_ZONE = 'Europe/Berlin'  # War: 'UTC'
USE_I18N = True
USE_TZ = True                # Wichtig: Timestamps immer mit Timezone!
```

> **Übung 4.1:** Öffne `config/settings.py`. Ändere `LANGUAGE_CODE` und `TIME_ZONE`. Starte den Server — die Willkommensseite sollte jetzt auf Deutsch sein.

---

## 5. Apps — Djangos Modularisierung

### 5.1 Was ist eine App?

In Django ist ein Projekt aus mehreren **Apps** zusammengesetzt. Eine App ist ein in sich geschlossenes Modul mit eigenen Models, Views, Templates und Tests. Für dein LIMS haben wir drei Apps geplant:

| App | Verantwortung |
|-----|---------------|
| `samples` | Proben-Registrierung, Storage, Lifecycle |
| `extractions` | Batch-Verwaltung, Plate/Tube-Layouts, Hamilton |
| `analyses` | MS-Runs, Ergebnisse, QC |

Plus eine optionale `core`-App für gemeinsam genutzte Dinge (User-Erweiterungen, Audit-Log, Container-Modell).

**In dieser Phase erstellen wir nur die `samples`-App.** Die anderen folgen in späteren Phasen.

### 5.2 App erstellen

```bash
# Erstelle die samples-App
uv run python manage.py startapp samples
```

Das erzeugt:

```
samples/
├── __init__.py
├── admin.py            # ⭐ Admin-Panel-Konfiguration
├── apps.py             # App-Metadaten
├── migrations/         # ⭐ Datenbank-Migrationen (auto-generiert)
│   └── __init__.py
├── models.py           # ⭐ Datenmodelle
├── tests.py            # Tests (wir nutzen stattdessen tests/)
└── views.py            # ⭐ Views (Request-Handler)
```

### 5.3 App registrieren

Jede neue App muss in `config/settings.py` eingetragen werden:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Eigene Apps
    'samples',                         # ← NEU
]
```

> **Häufiger Fehler:** App erstellen aber vergessen, sie in `INSTALLED_APPS` einzutragen. Django ignoriert die App dann komplett — keine Models, keine Migrations, kein Admin.

> **Übung 5.1:** Erstelle die `samples`-App und registriere sie in den Settings. Starte den Server — es sollte keine Fehler geben.

---

## 6. Models — Datenbank ohne SQL

> **Analogie:** Ein Django-Model ist wie eine C#-Klasse mit Entity Framework Annotations — du definierst die Struktur in Python, und Django generiert die Datenbanktabelle. Du schreibst kein SQL, aber du bekommst eine echte relationale Tabelle.

### 6.1 Dein erstes Model

Öffne `samples/models.py` und ersetze den Inhalt:

```python
# samples/models.py

from django.db import models
from django.utils import timezone


class Sample(models.Model):
    """Eine Laborprobe im LIMS.

    Dies ist die zentrale Entität des Systems. Jede Probe durchläuft
    einen definierten Lifecycle von der Registrierung bis zur Archivierung.
    """

    # ── Choices ──────────────────────────────────────────────
    # Choices sind Djangos Art, Enum-artige Felder zu definieren.
    # Erstes Element: Datenbankwert. Zweites: Anzeige-Label.

    class Status(models.TextChoices):
        REGISTERED = "registered", "Registriert"
        RECEIVED = "received", "Empfangen"
        STORED = "stored", "Eingelagert"
        RELEASED = "released", "Freigegeben"

    class SampleType(models.TextChoices):
        SERUM = "serum", "Serum"
        PLASMA = "plasma", "Plasma"
        URINE = "urine", "Urin"
        DBS = "dbs", "Dried Blood Spot"
        CSF = "csf", "Liquor"
        OTHER = "other", "Sonstiges"

    # ── Felder ───────────────────────────────────────────────

    barcode = models.CharField(
        max_length=30,
        unique=True,            # Kein Barcode darf doppelt existieren
        verbose_name="Barcode",
        help_text="Eindeutiger Proben-Barcode (z.B. S-2024-00001)",
    )

    sample_type = models.CharField(
        max_length=20,
        choices=SampleType.choices,
        verbose_name="Probenart",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.REGISTERED,
        verbose_name="Status",
    )

    storage_location = models.CharField(
        max_length=100,
        blank=True,             # Darf leer sein (im Formular)
        default="",
        verbose_name="Lagerort",
        help_text="z.B. Freezer-A, Regal 3, Position 12",
    )

    notes = models.TextField(
        blank=True,
        default="",
        verbose_name="Bemerkungen",
    )

    # ── Timestamps ───────────────────────────────────────────

    created_at = models.DateTimeField(
        auto_now_add=True,      # Wird automatisch beim Erstellen gesetzt
        verbose_name="Erstellt am",
    )

    updated_at = models.DateTimeField(
        auto_now=True,          # Wird bei jedem Speichern aktualisiert
        verbose_name="Geändert am",
    )

    received_at = models.DateTimeField(
        null=True,              # Darf NULL in der Datenbank sein
        blank=True,
        verbose_name="Empfangen am",
    )

    # ── Meta ─────────────────────────────────────────────────

    class Meta:
        ordering = ["-created_at"]               # Neueste zuerst
        verbose_name = "Probe"
        verbose_name_plural = "Proben"

    # ── Methoden ─────────────────────────────────────────────

    def __str__(self):
        """Wird überall angezeigt wo Django das Objekt als String braucht."""
        return f"{self.barcode} ({self.get_status_display()})"
```

### 6.2 Feld-Typen erklärt

Hier die Feld-Typen die du am häufigsten brauchst:

| Django-Feld | SQL-Typ | Python-Typ | Anmerkung |
|-------------|---------|------------|-----------|
| `CharField(max_length=N)` | VARCHAR(N) | str | Für kurze Texte, max_length ist Pflicht |
| `TextField()` | TEXT | str | Für lange Texte, kein Limit |
| `IntegerField()` | INTEGER | int | Ganzzahlen |
| `FloatField()` | DOUBLE | float | Fließkommazahlen |
| `DecimalField(max_digits, decimal_places)` | NUMERIC | Decimal | Präzise Zahlen (für Konzentrationen!) |
| `BooleanField()` | BOOLEAN | bool | True/False |
| `DateTimeField()` | TIMESTAMP | datetime | Datum + Uhrzeit |
| `DateField()` | DATE | date | Nur Datum |
| `ForeignKey(OtherModel)` | INT + FK | OtherModel | Beziehung zu anderem Model |
| `ManyToManyField(OtherModel)` | Junction Table | QuerySet | n:m-Beziehung |

### 6.3 Wichtige Feld-Optionen

```python
# null vs. blank — das verwirrt am Anfang JEDEN:
#   null=True   → Datenbank erlaubt NULL (DB-Ebene)
#   blank=True  → Formular erlaubt leeres Feld (Validierungs-Ebene)
#
# Für Strings: Nutze blank=True + default="" statt null=True
# Für Dates/Numbers: Nutze null=True + blank=True

# Beispiele:
name = models.CharField(max_length=100)                    # Pflichtfeld
name = models.CharField(max_length=100, blank=True, default="")  # Optional
date = models.DateTimeField(null=True, blank=True)         # Optionales Datum
code = models.CharField(max_length=10, unique=True)        # Muss eindeutig sein
```

> **Faustregel `null` vs. `blank`:**
> - String-Felder: `blank=True, default=""` (leerer String statt NULL)
> - Alles andere (Dates, Numbers, ForeignKeys): `null=True, blank=True`
> - Django-Konvention: vermeide `null=True` auf String-Feldern, weil du sonst zwei "leere" Werte hast (NULL und "")

### 6.4 Beziehungen zwischen Models

Du brauchst sie noch nicht sofort, aber hier ist die Übersicht für das LIMS:

```python
# ── ForeignKey: "gehört zu einem" (n:1) ──────────────
class ContainerPosition(models.Model):
    container = models.ForeignKey(
        "Container",
        on_delete=models.CASCADE,      # Wenn Container gelöscht → Positionen auch
        related_name="positions",       # container.positions.all()
    )
    sample = models.ForeignKey(
        "Sample",
        on_delete=models.PROTECT,      # Verbiete Löschen wenn Sample zugewiesen
        null=True, blank=True,
    )
    position_label = models.CharField(max_length=10)  # "A1", "B3", etc.

# on_delete Optionen:
#   CASCADE  → Lösche abhängige Objekte mit (Container weg → Positionen weg)
#   PROTECT  → Verbiete Löschen (Sample kann nicht gelöscht werden wenn zugewiesen)
#   SET_NULL → Setze auf NULL (braucht null=True)
```

> **Übung 6.1:** Erstelle das Sample-Model in `samples/models.py` wie oben gezeigt. Lies jeden Kommentar. Starte den Server — Django sollte warnen, dass es unapplied migrations gibt. Das ist korrekt — die kommen im nächsten Abschnitt.

---

## 7. Migrations — Versionskontrolle für die Datenbank

> **Analogie:** Migrations sind wie Git-Commits für dein Datenbankschema. Jede Änderung an einem Model (neues Feld, Feld umbenannt, Feld gelöscht) wird als Migration-Datei gespeichert. Du kannst vorwärts (apply) und rückwärts (rollback) migrieren. Das ist Alembic, nur eingebaut.

### 7.1 Migration erstellen

```bash
uv run python manage.py makemigrations
```

Erwartete Ausgabe:
```
Migrations for 'samples':
  samples/migrations/0001_initial.py
    - Create model Sample
```

Django hat dein Model analysiert und eine Migration-Datei erstellt. Schau sie dir an:

```bash
cat samples/migrations/0001_initial.py
```

Du siehst Python-Code der beschreibt: "Erstelle eine Tabelle `samples_sample` mit diesen Spalten." Du musst diese Datei nie manuell editieren — aber es ist gut zu wissen, was drin steht.

### 7.2 Migration anwenden

```bash
uv run python manage.py migrate
```

Erwartete Ausgabe:
```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, samples, sessions
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  ...
  Applying samples.0001_initial... OK
```

Jetzt existiert die Tabelle in der Datenbank. Bei SQLite wurde eine `db.sqlite3`-Datei erstellt.

### 7.3 SQL anschauen (optional)

Wenn du sehen willst, welches SQL Django generiert:

```bash
uv run python manage.py sqlmigrate samples 0001
```

Ausgabe (vereinfacht):
```sql
CREATE TABLE "samples_sample" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "barcode" varchar(30) NOT NULL UNIQUE,
    "sample_type" varchar(20) NOT NULL,
    "status" varchar(20) NOT NULL,
    "storage_location" varchar(100) NOT NULL,
    "notes" text NOT NULL,
    "created_at" datetime NOT NULL,
    "updated_at" datetime NOT NULL,
    "received_at" datetime NULL
);
```

> **Beachte:** Django fügt automatisch ein `id`-Feld als Primary Key hinzu, wenn du keins definierst. Das ist ein Auto-Increment Integer.

### 7.4 Der Migration-Workflow

Jedes Mal wenn du ein Model änderst (Feld hinzufügen, entfernen, umbenennen):

```bash
# 1. Model ändern (in models.py)

# 2. Migration erstellen
uv run python manage.py makemigrations

# 3. Prüfen was passiert (optional)
uv run python manage.py sqlmigrate samples 0002

# 4. Migration anwenden
uv run python manage.py migrate
```

**Goldene Regel:** Editiere niemals eine Migration-Datei die bereits committed und von anderen angewendet wurde. Erstelle stattdessen eine neue Migration.

### 7.5 Nützliche Befehle

```bash
# Status aller Migrations anzeigen
uv run python manage.py showmigrations

# Zu einem bestimmten Stand zurückrollen
uv run python manage.py migrate samples 0001   # Zurück zu Migration 0001
uv run python manage.py migrate samples zero    # Alle Migrations rückgängig
```

> **Übung 7.1:** Erstelle die Migration mit `makemigrations`. Schau dir das generierte SQL an mit `sqlmigrate`. Wende die Migration an mit `migrate`. Dann füge dem Sample-Model ein neues Feld hinzu — z.B. `patient_id = models.CharField(max_length=30, blank=True, default="")` — und wiederhole den Prozess. Du solltest eine `0002_sample_patient_id.py`-Migration sehen.

---

## 8. Die Django Shell — dein interaktives Labor

> **Analogie:** Die Django Shell ist wie die R-Konsole oder die C#-Interactive-Window — du kannst live mit deinen Models und der Datenbank interagieren. Perfekt zum Experimentieren und Debuggen.

### 8.1 Shell starten

```bash
uv run python manage.py shell
```

Du bist jetzt in einer Python-REPL, aber mit Django geladen — alle Models, Settings und Datenbankverbindungen sind verfügbar.

### 8.2 CRUD-Operationen

```python
# ── CREATE ───────────────────────────────────────────
from samples.models import Sample

s = Sample(barcode="S-2024-00001", sample_type="serum")
s.save()
# Oder in einem Schritt:
s = Sample.objects.create(barcode="S-2024-00002", sample_type="plasma")

# ── READ ─────────────────────────────────────────────
# Alle Proben
all_samples = Sample.objects.all()
print(all_samples)
# <QuerySet [<Sample: S-2024-00002 (Registriert)>, <Sample: S-2024-00001 (Registriert)>]>

# Eine bestimmte Probe
s = Sample.objects.get(barcode="S-2024-00001")
print(s.sample_type)   # "serum"
print(s.created_at)    # 2024-12-15 14:30:22+01:00

# Filtern
serum_samples = Sample.objects.filter(sample_type="serum")
registered = Sample.objects.filter(status=Sample.Status.REGISTERED)

# Filtern mit Lookups
recent = Sample.objects.filter(created_at__date="2024-12-15")  # Exaktes Datum
contains = Sample.objects.filter(barcode__contains="2024")     # Enthält String
starts = Sample.objects.filter(barcode__startswith="S-")       # Beginnt mit

# Zählen
count = Sample.objects.filter(sample_type="serum").count()

# Existiert?
exists = Sample.objects.filter(barcode="S-2024-00001").exists()

# ── UPDATE ───────────────────────────────────────────
s = Sample.objects.get(barcode="S-2024-00001")
s.status = Sample.Status.RECEIVED
s.received_at = timezone.now()
s.save()

# Oder mehrere auf einmal:
Sample.objects.filter(status="registered").update(status="received")

# ── DELETE ───────────────────────────────────────────
s = Sample.objects.get(barcode="S-2024-00002")
s.delete()
```

### 8.3 QuerySets sind lazy

Ein wichtiges Konzept: QuerySets werden erst ausgeführt, wenn du die Daten wirklich brauchst.

```python
# Das hier macht noch KEINEN Datenbank-Query:
qs = Sample.objects.filter(sample_type="serum").order_by("barcode")

# Erst wenn du die Daten abrufst, wird SQL ausgeführt:
list(qs)          # Jetzt!
for s in qs:      # Oder jetzt!
    print(s)
qs.count()        # Oder jetzt! (SELECT COUNT(*))
```

Das heißt: Du kannst QuerySets verketten (chaining) ohne Performance-Kosten:

```python
qs = Sample.objects.all()
qs = qs.filter(sample_type="serum")
qs = qs.filter(status="registered")
qs = qs.order_by("-created_at")
# Erst eine SQL-Query, nicht drei!
```

> **R-Analogie:** Das ist wie `dplyr`-Pipes: `samples |> filter(type == "serum") |> arrange(desc(date))` — die Query wird erst am Ende ausgeführt (lazy evaluation).

### 8.4 Shell verlassen

```python
exit()
```

> **Tipp:** Installiere `django-extensions` für eine verbesserte Shell:
> ```bash
> uv add --dev django-extensions
> ```
> Dann in `INSTALLED_APPS`: `'django_extensions'`
> Und starte mit: `uv run python manage.py shell_plus`
> `shell_plus` importiert automatisch alle Models — du sparst die `from samples.models import Sample`-Zeile.

> **Übung 8.1:** Öffne die Django Shell. Erstelle 5 Proben mit verschiedenen Barcodes und Probenarten. Filtere nach Probenart. Ändere den Status einer Probe. Lösche eine Probe. Zähle die verbleibenden.

---

## 9. Django Admin — dein geschenktes Backend

> **Das ist der Punkt, wo Django-Skeptiker zu Django-Fans werden.** Mit wenigen Zeilen Code bekommst du ein vollständiges Backend mit Listen, Suche, Filtern, Sortierung und CRUD — responsiv und sofort nutzbar.

### 9.1 Superuser erstellen

```bash
uv run python manage.py createsuperuser
```

Django fragt nach Username, E-Mail und Passwort. Wähle etwas Einfaches für die Entwicklung (z.B. `admin` / `admin@lims.local` / `admin1234`).

### 9.2 Admin starten und einloggen

```bash
uv run python manage.py runserver
```

Öffne **http://127.0.0.1:8000/admin/** — du siehst die Login-Seite. Logge dich mit deinem Superuser ein. Du siehst erstmal nur "Groups" und "Users" — dein Sample-Model ist noch nicht registriert.

### 9.3 Model im Admin registrieren (minimal)

Öffne `samples/admin.py`:

```python
# samples/admin.py

from django.contrib import admin
from .models import Sample

admin.site.register(Sample)
```

Lade die Admin-Seite neu — du siehst jetzt "Proben" in der Sidebar. Klicke drauf. Du kannst Proben anlegen, bearbeiten und löschen. Drei Zeilen Code.

### 9.4 Admin anpassen (empfohlen)

Die Basis-Registrierung funktioniert, aber mit ein paar Anpassungen wird der Admin richtig nützlich:

```python
# samples/admin.py

from django.contrib import admin
from .models import Sample


@admin.register(Sample)  # Decorator-Syntax statt admin.site.register()
class SampleAdmin(admin.ModelAdmin):
    """Admin-Konfiguration für Proben."""

    # ── Listenansicht ────────────────────────────────
    list_display = [
        "barcode",
        "sample_type",
        "status",
        "storage_location",
        "created_at",
    ]

    # Rechts: Filter-Sidebar
    list_filter = [
        "status",
        "sample_type",
        "created_at",
    ]

    # Oben: Suchfeld (durchsucht diese Felder)
    search_fields = [
        "barcode",
        "storage_location",
        "notes",
    ]

    # Standardsortierung
    ordering = ["-created_at"]

    # Klickbarer Link in der Liste (statt nur erste Spalte)
    list_display_links = ["barcode"]

    # ── Detailansicht (Formular) ─────────────────────
    # Felder gruppieren mit Fieldsets
    fieldsets = [
        (
            "Proben-Identifikation",
            {
                "fields": ["barcode", "sample_type"],
            },
        ),
        (
            "Status & Lagerung",
            {
                "fields": ["status", "storage_location"],
            },
        ),
        (
            "Zeitstempel",
            {
                "fields": ["created_at", "updated_at", "received_at"],
                "classes": ["collapse"],  # Einklappbar
            },
        ),
        (
            "Bemerkungen",
            {
                "fields": ["notes"],
                "classes": ["collapse"],
            },
        ),
    ]

    # Diese Felder sind readonly (auto-generiert)
    readonly_fields = ["created_at", "updated_at"]

    # Wie viele Einträge pro Seite?
    list_per_page = 50

    # Datum-basierte Navigation
    date_hierarchy = "created_at"
```

### 9.5 Was du jetzt hast

Lade die Admin-Seite neu. Du siehst jetzt:
- Eine Probenliste mit Barcode, Typ, Status, Lagerort und Datum
- Filter in der rechten Sidebar (nach Status, Typ, Erstelldatum)
- Ein Suchfeld das Barcode, Lagerort und Bemerkungen durchsucht
- Ein Detailformular mit gruppierten Feldern
- Pagination (50 Einträge pro Seite)
- Datumsnavigation oben

**Das ist dein konfigurierbares Backend — ohne eine einzige Zeile HTML.**

> **Weber's Punkt aus dem ResearchGate-Post:** "Setting up storage locations without needing a system admin" — genau das liefert der Admin. Ein Lab-Manager kann hier Proben anlegen, Status ändern und Lagerorte verwalten, ohne dass ein Entwickler involviert ist.

> **Übung 9.1:** Erstelle den Superuser. Registriere das Sample-Model mit der erweiterten `SampleAdmin`-Klasse. Lege 10 Proben über den Admin an (verschiedene Typen, Status-Werte). Nutze die Filter und Suche. Ändere den Status einer Probe über das Formular.

---

## 10. URLs — das Routing-System

> **Analogie:** URLs in Django sind wie Routes in FastAPI oder Route-Tabellen in WPF-Navigation. Sie mappen eine URL auf eine View-Funktion: "Wenn jemand `/samples/` aufruft, führe die Funktion `sample_list` aus."

### 10.1 Zwei Ebenen: Projekt-URLs und App-URLs

Django nutzt ein hierarchisches URL-System:

```
http://127.0.0.1:8000/samples/           → config/urls.py
                                            ↓ leitet weiter zu
                                           samples/urls.py
                                            ↓ ruft auf
                                           samples/views.py::sample_list
```

### 10.2 Projekt-URLs (config/urls.py)

```python
# config/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('samples/', include('samples.urls')),     # ← NEU
]
```

`include('samples.urls')` sagt: "Alles was mit `samples/` anfängt, leite an die URL-Datei der samples-App weiter."

### 10.3 App-URLs (samples/urls.py)

Erstelle eine neue Datei `samples/urls.py`:

```python
# samples/urls.py

from django.urls import path
from . import views

app_name = "samples"  # Namespace für URL-Referenzen

urlpatterns = [
    # /samples/              → Liste aller Proben
    path("", views.sample_list, name="list"),

    # /samples/42/           → Detail einer Probe (ID=42)
    path("<int:pk>/", views.sample_detail, name="detail"),

    # /samples/new/          → Neue Probe anlegen
    path("new/", views.sample_create, name="create"),
]
```

### 10.4 URL-Elemente erklärt

```python
path("", views.sample_list, name="list")
#     │        │                  │
#     │        │                  └── Name für Reverse-Lookups
#     │        └── View-Funktion die aufgerufen wird
#     └── URL-Pattern (leer = Basis-URL der App, also /samples/)

path("<int:pk>/", views.sample_detail, name="detail")
#     │
#     └── URL-Parameter: eine Ganzzahl, verfügbar als 'pk' im View
#         /samples/42/  →  pk=42
```

### 10.5 URLs im Template referenzieren

```html
<!-- Statt hartcodierter URLs: -->
<a href="/samples/">Alle Proben</a>              <!-- ❌ fragil -->

<!-- Nutze den URL-Namen: -->
<a href="{% url 'samples:list' %}">Alle Proben</a>    <!-- ✅ robust -->
<a href="{% url 'samples:detail' pk=42 %}">Probe 42</a>
```

Wenn du die URL-Struktur änderst (z.B. von `/samples/` zu `/proben/`), funktionieren alle Template-Links automatisch weiter.

> **Übung 10.1:** Erstelle `samples/urls.py` mit den drei URL-Patterns. Binde es in `config/urls.py` ein. Die Views existieren noch nicht — der Server würde Fehler werfen. Das ist okay, wir erstellen sie im nächsten Abschnitt.

---

## 11. Views — Request rein, Response raus

> **Analogie:** Ein View ist wie ein Controller-Action in C# MVC oder ein Route-Handler in FastAPI. Er bekommt einen HTTP-Request, holt Daten aus der Datenbank, und gibt eine HTTP-Response zurück (meistens gerendetes HTML).

### 11.1 Function-Based Views (FBVs)

Wir starten mit Function-Based Views — die sind explizit und leicht verständlich. Class-Based Views (CBVs) sind mächtiger aber abstrakter; die kommen später.

```python
# samples/views.py

from django.shortcuts import render, get_object_or_404, redirect
from .models import Sample


def sample_list(request):
    """Zeigt alle Proben als Liste."""
    samples = Sample.objects.all()
    context = {
        "samples": samples,
        "total_count": samples.count(),
    }
    return render(request, "samples/sample_list.html", context)


def sample_detail(request, pk):
    """Zeigt die Details einer einzelnen Probe."""
    # get_object_or_404: Gibt das Objekt zurück oder zeigt eine 404-Seite
    sample = get_object_or_404(Sample, pk=pk)
    context = {
        "sample": sample,
    }
    return render(request, "samples/sample_detail.html", context)


def sample_create(request):
    """Erstellt eine neue Probe."""
    if request.method == "POST":
        # Formular wurde abgeschickt
        sample = Sample.objects.create(
            barcode=request.POST["barcode"],
            sample_type=request.POST["sample_type"],
        )
        return redirect("samples:detail", pk=sample.pk)

    # GET: Leeres Formular anzeigen
    context = {
        "sample_types": Sample.SampleType.choices,
    }
    return render(request, "samples/sample_create.html", context)
```

### 11.2 Was passiert hier im Detail?

```python
def sample_list(request):
#                 │
#                 └── Django übergibt automatisch das HttpRequest-Objekt
#                     Enthält: request.method, request.GET, request.POST, request.user

    samples = Sample.objects.all()
#   └── QuerySet: SQL wird erst ausgeführt, wenn das Template die Daten nutzt

    context = {"samples": samples, "total_count": samples.count()}
#   └── Dictionary mit Variablen, die im Template verfügbar sind

    return render(request, "samples/sample_list.html", context)
#          │              │                              │
#          │              └── Template-Pfad               └── Template-Variablen
#          └── Hilfsfunktion: rendert Template zu HttpResponse
```

### 11.3 GET vs. POST Pattern

Das `sample_create`-View zeigt ein häufiges Django-Pattern:

```python
def sample_create(request):
    if request.method == "POST":
        # Formular wurde abgeschickt → Daten verarbeiten
        # ... Objekt erstellen ...
        return redirect(...)        # ← Redirect nach POST (PRG-Pattern)
    else:
        # GET-Request → leeres Formular anzeigen
        return render(request, "template.html", context)
```

**PRG (Post-Redirect-Get):** Nach einem erfolgreichen POST machst du immer einen Redirect. Sonst würde der User beim Neuladen der Seite die Daten erneut senden.

> **Übung 11.1:** Erstelle die drei Views in `samples/views.py`. Die Templates existieren noch nicht — das kommt gleich. Aber der Code sollte syntaktisch korrekt sein.

---

## 12. Templates — HTML mit Superkräften

> **Analogie:** Django-Templates sind wie XAML in WPF, nur für HTML. Du definierst die Struktur, bindest Daten ein (`{{ variable }}`), und nutzt Kontrollstrukturen (`{% if %}`, `{% for %}`). Statt `{Binding Barcode}` schreibst du `{{ sample.barcode }}`.

### 12.1 Template-Verzeichnis einrichten

Erstelle den Ordner für Templates:

```bash
mkdir -p samples/templates/samples
```

**Warum `samples/templates/samples/` (doppelt)?** Django sucht Templates in allen `templates/`-Ordnern aller Apps. Ohne den inneren `samples/`-Ordner könnten gleichnamige Templates verschiedener Apps kollidieren. Das ist der "App Namespace" für Templates.

### 12.2 Base-Template (Layout)

Erstelle zuerst ein Basis-Template, von dem alle anderen erben. Erstelle den Ordner und die Datei:

```bash
mkdir -p templates
```

In `config/settings.py` musst du Django sagen, wo es nach Projekt-weiten Templates suchen soll:

```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],          # ← NEU: Projekt-Templates
        'APP_DIRS': True,                           # Sucht auch in App-Ordnern
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
```

Erstelle `templates/base.html`:

```html
<!-- templates/base.html -->
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}MS-LIMS{% endblock %}</title>
    <style>
        /* Minimales Styling für Entwicklung */
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 1rem;
        }
        nav { background: #2c3e50; padding: 1rem; margin-bottom: 2rem; border-radius: 4px; }
        nav a { color: white; text-decoration: none; margin-right: 1.5rem; }
        nav a:hover { text-decoration: underline; }
        h1, h2 { margin-bottom: 1rem; color: #2c3e50; }
        table { width: 100%; border-collapse: collapse; margin-bottom: 1rem; }
        th, td { padding: 0.5rem; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #f5f5f5; font-weight: 600; }
        tr:hover { background: #f9f9f9; }
        .btn {
            display: inline-block; padding: 0.4rem 1rem; border-radius: 4px;
            text-decoration: none; font-size: 0.9rem; cursor: pointer; border: none;
        }
        .btn-primary { background: #3498db; color: white; }
        .btn-primary:hover { background: #2980b9; }
        .badge {
            display: inline-block; padding: 0.2rem 0.6rem; border-radius: 12px;
            font-size: 0.75rem; font-weight: 600;
        }
        .badge-registered { background: #e0e0e0; color: #555; }
        .badge-received { background: #fff3cd; color: #856404; }
        .badge-stored { background: #cce5ff; color: #004085; }
        .badge-released { background: #d4edda; color: #155724; }
        form label { display: block; margin-bottom: 0.3rem; font-weight: 600; }
        form input, form select, form textarea {
            width: 100%; padding: 0.5rem; margin-bottom: 1rem;
            border: 1px solid #ccc; border-radius: 4px; font-size: 1rem;
        }
        .flash { padding: 0.8rem; margin-bottom: 1rem; border-radius: 4px; }
        .flash-success { background: #d4edda; color: #155724; }
        .flash-error { background: #f8d7da; color: #721c24; }
    </style>
    {% block extra_css %}{% endblock %}
</head>
<body>
    <nav>
        <a href="{% url 'samples:list' %}">Proben</a>
        <a href="{% url 'samples:create' %}">+ Neue Probe</a>
        <a href="/admin/">Admin</a>
    </nav>

    {% if messages %}
        {% for message in messages %}
            <div class="flash flash-{{ message.tags }}">{{ message }}</div>
        {% endfor %}
    {% endif %}

    <main>
        {% block content %}{% endblock %}
    </main>
</body>
</html>
```

### 12.3 Template-Tags erklärt

```html
<!-- Variable ausgeben -->
{{ sample.barcode }}
{{ sample.get_status_display }}    <!-- Zeigt "Registriert" statt "registered" -->

<!-- Tags (Logik) -->
{% if sample.status == "registered" %}
    <span>Neu</span>
{% elif sample.status == "received" %}
    <span>Empfangen</span>
{% endif %}

{% for sample in samples %}
    <tr>{{ sample.barcode }}</tr>
{% empty %}
    <tr><td>Keine Proben vorhanden.</td></tr>
{% endfor %}

<!-- URL generieren -->
{% url 'samples:detail' pk=sample.pk %}

<!-- Template-Vererbung -->
{% extends "base.html" %}         <!-- Erbt von base.html -->
{% block content %}...{% endblock %}

<!-- Filter (Daten transformieren) -->
{{ sample.created_at|date:"d.m.Y H:i" }}    <!-- Datumsformatierung -->
{{ samples|length }}                          <!-- Anzahl Elemente -->
{{ sample.notes|default:"Keine Bemerkungen" }}
```

### 12.4 Proben-Liste (sample_list.html)

```html
<!-- samples/templates/samples/sample_list.html -->

{% extends "base.html" %}

{% block title %}Proben — MS-LIMS{% endblock %}

{% block content %}
<h1>Proben ({{ total_count }})</h1>

<table>
    <thead>
        <tr>
            <th>Barcode</th>
            <th>Probenart</th>
            <th>Status</th>
            <th>Lagerort</th>
            <th>Erstellt</th>
        </tr>
    </thead>
    <tbody>
        {% for sample in samples %}
        <tr>
            <td>
                <a href="{% url 'samples:detail' pk=sample.pk %}">
                    {{ sample.barcode }}
                </a>
            </td>
            <td>{{ sample.get_sample_type_display }}</td>
            <td>
                <span class="badge badge-{{ sample.status }}">
                    {{ sample.get_status_display }}
                </span>
            </td>
            <td>{{ sample.storage_location|default:"—" }}</td>
            <td>{{ sample.created_at|date:"d.m.Y H:i" }}</td>
        </tr>
        {% empty %}
        <tr>
            <td colspan="5">Keine Proben vorhanden. <a href="{% url 'samples:create' %}">Erste Probe anlegen</a></td>
        </tr>
        {% endfor %}
    </tbody>
</table>
{% endblock %}
```

### 12.5 Proben-Detail (sample_detail.html)

```html
<!-- samples/templates/samples/sample_detail.html -->

{% extends "base.html" %}

{% block title %}{{ sample.barcode }} — MS-LIMS{% endblock %}

{% block content %}
<h1>{{ sample.barcode }}</h1>

<table>
    <tr>
        <th>Probenart</th>
        <td>{{ sample.get_sample_type_display }}</td>
    </tr>
    <tr>
        <th>Status</th>
        <td>
            <span class="badge badge-{{ sample.status }}">
                {{ sample.get_status_display }}
            </span>
        </td>
    </tr>
    <tr>
        <th>Lagerort</th>
        <td>{{ sample.storage_location|default:"Nicht zugewiesen" }}</td>
    </tr>
    <tr>
        <th>Erstellt am</th>
        <td>{{ sample.created_at|date:"d.m.Y H:i:s" }}</td>
    </tr>
    <tr>
        <th>Empfangen am</th>
        <td>{{ sample.received_at|date:"d.m.Y H:i:s"|default:"—" }}</td>
    </tr>
    {% if sample.notes %}
    <tr>
        <th>Bemerkungen</th>
        <td>{{ sample.notes }}</td>
    </tr>
    {% endif %}
</table>

<div style="margin-top: 1rem;">
    <a href="{% url 'samples:list' %}" class="btn btn-primary">← Zurück zur Liste</a>
</div>
{% endblock %}
```

### 12.6 Proben-Erstellung (sample_create.html)

```html
<!-- samples/templates/samples/sample_create.html -->

{% extends "base.html" %}

{% block title %}Neue Probe — MS-LIMS{% endblock %}

{% block content %}
<h1>Neue Probe anlegen</h1>

<form method="post">
    {% csrf_token %}

    <label for="barcode">Barcode</label>
    <input type="text" id="barcode" name="barcode"
           placeholder="z.B. S-2024-00001" required>

    <label for="sample_type">Probenart</label>
    <select id="sample_type" name="sample_type" required>
        <option value="">— Bitte wählen —</option>
        {% for value, label in sample_types %}
            <option value="{{ value }}">{{ label }}</option>
        {% endfor %}
    </select>

    <button type="submit" class="btn btn-primary">Probe anlegen</button>
</form>
{% endblock %}
```

### 12.7 CSRF-Token erklärt

```html
{% csrf_token %}
```

Das ist ein Sicherheits-Feature. Django generiert ein zufälliges Token und prüft bei jedem POST-Request, ob das Token gültig ist. Das verhindert Cross-Site-Request-Forgery-Angriffe (jemand baut eine fremde Website die Formulare an dein LIMS sendet). **Vergiss `{% csrf_token %}` nie in einem `<form method="post">` — sonst lehnt Django den Request ab (403 Forbidden).**

> **Übung 12.1:** Erstelle alle drei Templates. Starte den Server. Rufe `/samples/` auf — du solltest eine leere Tabelle sehen. Rufe `/samples/new/` auf und lege eine Probe an. Du wirst zur Detailseite weitergeleitet. Gehe zurück zur Liste — deine Probe ist da.

---

## 13. Statische Dateien (CSS/JS)

Für Phase 2 reicht das inline `<style>` im Base-Template. Aber für die Vollständigkeit: So funktionieren statische Dateien in Django.

### 13.1 Kurzversion

```bash
# Ordner erstellen
mkdir -p static/css
```

In `config/settings.py`:

```python
# Unter STATIC_URL = 'static/' (existiert schon) hinzufügen:
STATICFILES_DIRS = [BASE_DIR / 'static']
```

In Templates:

```html
{% load static %}
<link rel="stylesheet" href="{% static 'css/main.css' %}">
```

### 13.2 Warum nicht einfach `/static/css/main.css`?

Django kann statische Dateien aus verschiedenen Quellen zusammensammeln (jede App hat ihre eigenen, plus Projekt-weite). `{% static %}` generiert den richtigen Pfad, egal wo die Datei herkommt. In Produktion werden statische Dateien von einem Web-Server (nginx) ausgeliefert, nicht von Django — und die URLs können sich ändern.

> **Für Phase 2 brauchst du das nicht aktiv.** Das Inline-CSS im Base-Template reicht zum Lernen. Wir führen ein richtiges CSS-Framework in einer späteren Phase ein.

---

## 14. Formulare — Daten vom User entgegennehmen

In unserem `sample_create`-View haben wir `request.POST["barcode"]` direkt gelesen. Das funktioniert, ist aber unsicher und mühsam (keine Validierung, keine Fehlermeldungen). Django Forms lösen das.

### 14.1 Ein Django-Form definieren

Erstelle `samples/forms.py`:

```python
# samples/forms.py

from django import forms
from .models import Sample


class SampleForm(forms.ModelForm):
    """Formular für die Proben-Erstellung.

    ModelForm generiert Formularfelder automatisch aus dem Model.
    Du musst nicht jedes Feld manuell definieren.
    """

    class Meta:
        model = Sample
        fields = ["barcode", "sample_type", "notes"]
        # Felder die NICHT im Formular erscheinen:
        # status (wird automatisch gesetzt), storage_location (kommt später),
        # created_at/updated_at (automatisch), received_at (automatisch)

        widgets = {
            "barcode": forms.TextInput(
                attrs={"placeholder": "z.B. S-2024-00001"}
            ),
            "notes": forms.Textarea(
                attrs={"rows": 3, "placeholder": "Optionale Bemerkungen"}
            ),
        }
```

### 14.2 View mit Form

Aktualisiere den `sample_create`-View:

```python
# In samples/views.py — ersetze den bestehenden sample_create:

from django.contrib import messages
from .forms import SampleForm


def sample_create(request):
    """Erstellt eine neue Probe mit validiertem Formular."""
    if request.method == "POST":
        form = SampleForm(request.POST)
        if form.is_valid():
            sample = form.save()
            messages.success(request, f"Probe {sample.barcode} wurde angelegt.")
            return redirect("samples:detail", pk=sample.pk)
        # Form ist ungültig → wird mit Fehlermeldungen neu angezeigt
    else:
        form = SampleForm()

    return render(request, "samples/sample_create.html", {"form": form})
```

### 14.3 Template mit Form

Ersetze das manuelle HTML-Formular in `sample_create.html`:

```html
<!-- samples/templates/samples/sample_create.html -->

{% extends "base.html" %}

{% block title %}Neue Probe — MS-LIMS{% endblock %}

{% block content %}
<h1>Neue Probe anlegen</h1>

<form method="post">
    {% csrf_token %}

    {% for field in form %}
    <div style="margin-bottom: 1rem;">
        <label for="{{ field.id_for_label }}">{{ field.label }}</label>
        {{ field }}
        {% if field.errors %}
            <div style="color: #dc3545; font-size: 0.85rem;">
                {% for error in field.errors %}
                    {{ error }}
                {% endfor %}
            </div>
        {% endif %}
        {% if field.help_text %}
            <small style="color: #6c757d;">{{ field.help_text }}</small>
        {% endif %}
    </div>
    {% endfor %}

    <button type="submit" class="btn btn-primary">Probe anlegen</button>
</form>
{% endblock %}
```

### 14.4 Was du bekommst

- **Automatische Validierung:** Pflichtfelder werden geprüft, `unique=True` auf Barcode verhindert Duplikate
- **Fehlermeldungen:** Werden direkt am Feld angezeigt
- **CSRF-Schutz:** Eingebaut
- **HTML-Generierung:** `{{ field }}` rendert das passende HTML-Element (Input, Select, Textarea)
- **Keine SQL-Injection:** Django escaped alles automatisch

> **C#-Analogie:** `ModelForm` ist wie ein ViewModel mit Data Annotations in ASP.NET MVC. `[Required]` → Pflichtfeld im Model, `form.is_valid()` → `ModelState.IsValid`.

> **Übung 14.1:** Erstelle `samples/forms.py` und aktualisiere View und Template. Versuche, eine Probe mit einem bereits existierenden Barcode anzulegen — du solltest eine Fehlermeldung sehen.

---

## 15. Tests in Django

### 15.1 pytest-django einrichten

Du hast in Phase 1 `pytest` und `pytest-django` installiert. Jetzt konfigurieren wir sie für Django.

In `pyproject.toml` (sollte teilweise schon vorhanden sein):

```toml
[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "config.settings"
pythonpath = ["."]
addopts = "-v --tb=short"
```

### 15.2 conftest.py für Datenbankzugriff

```python
# tests/conftest.py

import pytest
from samples.models import Sample


@pytest.fixture
def sample(db):
    """Erstellt eine Test-Probe.

    Das `db`-Fixture (von pytest-django) gibt dem Test
    Zugriff auf die Datenbank. Ohne `db` würde Django den
    Datenbankzugriff blockieren.
    """
    return Sample.objects.create(
        barcode="TEST-001",
        sample_type=Sample.SampleType.SERUM,
    )


@pytest.fixture
def sample_batch(db):
    """Erstellt mehrere Test-Proben."""
    samples = []
    for i in range(5):
        s = Sample.objects.create(
            barcode=f"TEST-{i+1:03d}",
            sample_type=Sample.SampleType.SERUM,
        )
        samples.append(s)
    return samples
```

> **Wichtig: `db`-Fixture!** In pytest-django ist Datenbankzugriff standardmäßig gesperrt (Performance & Sicherheit). Du musst entweder `db` als Fixture-Parameter angeben oder den Test mit `@pytest.mark.django_db` dekorieren.

### 15.3 Model-Tests

```python
# tests/test_models.py

import pytest
from samples.models import Sample


@pytest.mark.django_db
class TestSampleModel:
    """Tests für das Sample-Model."""

    def test_create_sample(self):
        sample = Sample.objects.create(
            barcode="S-001",
            sample_type="serum",
        )
        assert sample.barcode == "S-001"
        assert sample.status == Sample.Status.REGISTERED
        assert sample.pk is not None

    def test_str_representation(self, sample):
        assert "TEST-001" in str(sample)
        assert "Registriert" in str(sample)

    def test_default_status_is_registered(self, sample):
        assert sample.status == Sample.Status.REGISTERED

    def test_barcode_must_be_unique(self, sample):
        with pytest.raises(Exception):  # IntegrityError
            Sample.objects.create(
                barcode="TEST-001",       # Duplikat!
                sample_type="serum",
            )

    def test_ordering_newest_first(self, sample_batch):
        samples = list(Sample.objects.all())
        dates = [s.created_at for s in samples]
        assert dates == sorted(dates, reverse=True)
```

### 15.4 View-Tests

```python
# tests/test_views.py

import pytest
from django.test import Client


@pytest.fixture
def client():
    """Django Test-Client — simuliert einen Browser."""
    return Client()


@pytest.mark.django_db
class TestSampleViews:
    """Tests für die Sample-Views."""

    def test_sample_list_returns_200(self, client):
        response = client.get("/samples/")
        assert response.status_code == 200

    def test_sample_list_shows_samples(self, client, sample):
        response = client.get("/samples/")
        assert "TEST-001" in response.content.decode()

    def test_sample_detail_returns_200(self, client, sample):
        response = client.get(f"/samples/{sample.pk}/")
        assert response.status_code == 200
        assert "TEST-001" in response.content.decode()

    def test_sample_detail_404_for_nonexistent(self, client):
        response = client.get("/samples/99999/")
        assert response.status_code == 404

    def test_create_sample_via_post(self, client):
        response = client.post("/samples/new/", {
            "barcode": "NEW-001",
            "sample_type": "serum",
        })
        # Redirect nach erfolgreichem POST
        assert response.status_code == 302

        # Probe existiert in der DB
        from samples.models import Sample
        assert Sample.objects.filter(barcode="NEW-001").exists()

    def test_create_duplicate_barcode_shows_error(self, client, sample):
        response = client.post("/samples/new/", {
            "barcode": "TEST-001",     # Existiert schon!
            "sample_type": "serum",
        })
        # Kein Redirect, sondern Formular mit Fehler
        assert response.status_code == 200
        assert "bereits" in response.content.decode().lower() or \
               "already" in response.content.decode().lower()
```

### 15.5 Tests ausführen

```bash
# Alle Tests
uv run pytest

# Nur Model-Tests
uv run pytest tests/test_models.py

# Nur ein bestimmter Test
uv run pytest tests/test_views.py::TestSampleViews::test_create_sample_via_post

# Mit Print-Ausgaben (für Debugging)
uv run pytest -s
```

> **Was passiert unter der Haube?** pytest-django erstellt automatisch eine temporäre Testdatenbank, führt die Tests darin aus, und löscht sie danach. Jeder Test läuft in einer eigenen Transaktion die am Ende zurückgerollt wird — Tests beeinflussen sich nicht gegenseitig.

> **Übung 15.1:** Erstelle `tests/conftest.py`, `tests/test_models.py`, und `tests/test_views.py`. Lass alle Tests laufen. Alle sollten grün sein. Falls nicht — Debug! Die Fehlermeldungen von pytest sind sehr aussagekräftig.

---

## 16. Abschluss-Übung: Mini-LIMS

Jetzt baust du alles zu einem funktionierenden Mini-LIMS zusammen. Am Ende sollst du den folgenden End-to-End-Flow im Browser durchspielen können.

### 16.1 Ziel-Workflow

1. Öffne `/samples/` — leere Tabelle
2. Klicke "Neue Probe" — Formular erscheint
3. Gib Barcode und Probenart ein — Submit
4. Du wirst zur Detailseite weitergeleitet (Erfolgs-Meldung)
5. Klicke "Zurück zur Liste" — deine Probe ist in der Tabelle
6. Öffne `/admin/` — deine Probe ist auch dort sichtbar und editierbar
7. Ändere den Status im Admin auf "Empfangen"
8. Zurück zur Liste — Status-Badge hat sich geändert

### 16.2 Erwartete Projektstruktur

```
ms-lims/
├── config/
│   ├── __init__.py
│   ├── settings.py         # Mit samples-App, Template-Dirs, etc.
│   ├── urls.py             # Inkludiert samples.urls + admin
│   └── wsgi.py
├── samples/
│   ├── __init__.py
│   ├── admin.py            # SampleAdmin mit list_display, filters, etc.
│   ├── apps.py
│   ├── forms.py            # SampleForm (ModelForm)
│   ├── migrations/
│   │   ├── __init__.py
│   │   └── 0001_initial.py
│   ├── models.py           # Sample-Model mit Choices, Timestamps, Meta
│   ├── templates/
│   │   └── samples/
│   │       ├── sample_list.html
│   │       ├── sample_detail.html
│   │       └── sample_create.html
│   ├── urls.py             # 3 URL-Patterns
│   └── views.py            # 3 Views (list, detail, create)
├── templates/
│   └── base.html           # Basis-Layout
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_models.py
│   └── test_views.py
├── manage.py
├── pyproject.toml
├── uv.lock
├── .gitignore
└── db.sqlite3              # SQLite-Datenbank (auto-generiert, in .gitignore!)
```

### 16.3 Qualitätsprüfung

```bash
# Formatting
uv run ruff format .

# Linting
uv run ruff check .

# Tests
uv run pytest -v

# Server starten und manuell testen
uv run python manage.py runserver

# Wenn alles funktioniert:
git add .
git commit -m "Phase 2 complete: Django LIMS with Sample CRUD, Admin, and tests"
```

### 16.4 Bonus-Aufgaben (optional)

Falls du Lust hast, tiefer zu gehen:

**Bonus 1 — Proben-Counter:** Ergänze die Proben-Liste um eine Status-Zusammenfassung oben ("3 Registriert, 2 Empfangen, 1 Eingelagert"). Tipp: `Sample.objects.filter(status="registered").count()` im View berechnen und als Context übergeben.

**Bonus 2 — Barcode-Auto-Generierung:** Statt den Barcode manuell einzugeben, generiere ihn automatisch beim Erstellen (z.B. `S-2024-00042`). Tipp: Überschreibe die `save()`-Methode im Model oder nutze ein `pre_save`-Signal.

**Bonus 3 — Proben editieren:** Füge einen "Bearbeiten"-Button auf der Detailseite hinzu, der zu einem vorbefüllten Formular führt. Tipp: `SampleForm(instance=sample)` befüllt das Formular mit bestehenden Daten.

---

## 17. Checkliste: Bin ich bereit für Phase 3?

- [ ] Ich verstehe den MTV-Zyklus (Request → URL → View → Model → Template → Response)
- [ ] Ich kann ein Django-Projekt erstellen und den Server starten
- [ ] Ich kann eine App erstellen und in INSTALLED_APPS registrieren
- [ ] Ich kann Models definieren mit verschiedenen Feldtypen und Optionen
- [ ] Ich verstehe den Unterschied zwischen `null=True` und `blank=True`
- [ ] Ich kann Migrations erstellen und anwenden
- [ ] Ich kann die Django Shell nutzen um Daten zu erstellen und abzufragen
- [ ] Ich habe einen Admin-Bereich mit angepasster Konfiguration
- [ ] Ich kann URL-Patterns definieren und Apps per `include()` einbinden
- [ ] Ich kann Function-Based Views schreiben die Templates rendern
- [ ] Ich verstehe Template-Vererbung (`extends`, `block`)
- [ ] Ich kann Django Forms (ModelForm) für validierte Eingaben nutzen
- [ ] Ich kann Tests schreiben die Models und Views prüfen
- [ ] Mein Mini-LIMS funktioniert End-to-End im Browser

---

## Was kommt in Phase 3?

Phase 3 bringt **PostgreSQL und Docker** — du ersetzt SQLite durch eine richtige Datenbank, lernst `docker-compose` für reproduzierbare Entwicklungsumgebungen, und konfigurierst Django für den Betrieb mit Postgres. Außerdem führen wir **Environment Variables** für sensible Einstellungen ein (SECRET_KEY, DB-Passwort) — ein wichtiger Schritt Richtung Produktion und Compliance.
