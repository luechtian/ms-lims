# MS-LIMS — Requirements-Dokument

> **Zweck:** Konsolidierte fachliche Anforderungen für das MS-LIMS — das Domänenmodell aus Sicht der Nutzer. Dient als Grundlage für die Spezifikation einzelner Features. Wird fortlaufend verfeinert.
>
> **Stand:** April 2026 (aktualisiert nach Einführung der Projekt-Constitution)
> **Verbindliche Prinzipien:** `.specify/memory/constitution.md` (Tech-Stack, Modularitäts-Regeln, Design Patterns)
> **Tech-Hintergrund:** `docs/decisions/ms-lims-tech-stack-referenz-v2.md` (Entscheidungsbegründungen, Ideenspeicher)
>
> Dieses Dokument beschreibt *was* das LIMS können muss (fachlich). *Wie* es implementiert wird, steht in der Constitution und in den einzelnen Specs unter `specs/`.

---

## 1. Projekt-Überblick

### 1.1 Was ist das MS-LIMS?

Ein leichtgewichtiges, web-basiertes Laboratory Information Management System für Massenspektrometrie-Labore. Es bildet den vollständigen Weg einer Probe ab — von der Projektvereinbarung über Probeneingang, Lagerung, Extraktion, Messung bis zur Quantifizierung.

### 1.2 Design-Prinzipien

**Manual-First:** Jeder Workflow wird zuerst für manuelle Durchführung gebaut. Automatisierung (Hamilton, Result-Parser) kommt erst wenn der manuelle Prozess digital abgebildet und verstanden ist.

**Schneller als Excel:** Wenn ein Workflow im LIMS länger dauert als in Excel, hat das Feature versagt. Das gilt besonders für Probenregistrierung und Batch-Bildung.

**Niedrige Einstiegshürde:** Portable Deployment (Ordner kopieren, Doppelklick). Kein Datenbankserver, keine Installation. Ein Kollege muss das LIMS innerhalb von 2 Minuten ausprobieren können.

**Modularität:** Quantifizierungslogik (`lipidquant`) ist eigenständig nutzbar. Module sind unabhängig voneinander erweiterbar.

### 1.3 Nutzerkontext

- **Primäre Nutzer:** 1–2 Laboranten (Probeneingang, Extraktion, Messung)
- **Sekundäre Nutzer:** Laborleiterin (Überblick, Projekt-Management)
- **Umgebung:** Windows 11, Firefox, internes Labor (nicht reguliert)
- **Probentypen:** Biologische Proben (Gewebe, Zelllysat, Plasma etc.), keine klinischen Patientenproben

---

## 2. Workflow-Übersicht (End-to-End)

```
 Projekt                PROBENEINGANG              LAGERUNG
┌─────────────┐    ┌──────────────────────────┐    ┌──────────────┐
│ Vorgespräch │    │ Kunde sendet ausgefülltes │    │ Originalprobe│
│ mit Kunde   │───→│ Excel-Template + Proben   │───→│ bei -80°C    │
│             │    │ → Import ins LIMS         │    │ einlagern    │
│ Messungen   │    │ → Proben registriert      │    │              │
│ vereinbaren │    └──────────────────────────┘    └──────┬───────┘
└─────────────┘                                           │
                                              (kann mehrfach passieren)
                                                          │
 EXTRAKTION                                               ▼
┌─────────────────────────────────────────────────────────────────┐
│ 1. Subset aus Probeneingang wählen                              │
│ 2. Extraktionsprotokoll wählen (z.B. "SPE Standard")           │
│ 3. Mastermix konfigurieren (IS auswählen, Konz./Volumen)       │
│ 4. Probenliste + Protokoll drucken                              │
│ 5. Extraktion an der Bench durchführen                          │
│ 6. Rückdokumentation ins LIMS (ein Klick)                       │
│ 7. Originalproben zurück in -80°C, Extrakte in -20°C           │
│                                                                 │
│ → Wiederholbar: Vorextraktion, Standard, Spezial, Derivat      │
│ → Subsets: 50 Proben können in 3×15+5 aufgeteilt werden        │
└─────────────────────────────────────────────────────────────────┘
                              │
 MESSVORBEREITUNG             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 1. Extrakt-Batch aus -20°C holen                                │
│ 2. Resuspendieren                                               │
│ 3. Teil auf 96-Well-Plate verdünnen                             │
│ 4. Rest zurück in -20°C                                         │
│ 5. Plate in Autosampler → Messung starten                       │
└─────────────────────────────────────────────────────────────────┘
                              │
 MESSUNG & AUSWERTUNG         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 1. MS-Messung läuft (extern, auf dem Instrument)                │
│ 2. LIMS: Run als "gemessen" markieren                           │
│ 3. Peak-Processing extern (LipidView / LipidXplorer)           │
│    → Intensity-Tabelle (txt/csv)                (Tage später)   │
│ 4. LIMS: Intensity-Datei hochladen & verknüpfen                │
│ 5. Quantifizierung (lipidquant): IS-Norm → Blank Sub →         │
│    Response-Faktoren → Regression                               │
│ 6. Ergebnisse pro Probe im LIMS gespeichert                    │
│ 7. Batch-übergreifende Zusammenführung bei Bedarf               │
│    (alle Subsets einer Studie zusammen auswerten)               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Daten-Hierarchie

### 3.1 Parties (Stammdaten — wer liefert Proben?)

Die stabile Achse ist die **ResearchGroup** (Arbeitsgruppe / Firma mit ihrem PI). Projekte laufen oft über Jahre; Personen innerhalb einer Gruppe (Postdocs, Doktoranden) wechseln häufiger. Für interne Messungen wird das eigene Lab ebenfalls als ResearchGroup modelliert.

```
Institution (optional, Kontext)
│  Name, Adresse — z.B. "Universität Heidelberg", "Pharma GmbH"
│
└── ResearchGroup (stabile Achse)
    │  Name, PI (FK → Person), Institution (optional)
    │  Beispiel: "AG Müller", "Labor Schmidt"
    │
    └── Person (wechselt häufiger)
        │  Vorname, Nachname, E-Mail, Rolle (PI/Postdoc/PhD/Techniker)
        │  research_group (FK → ResearchGroup)
```

**Regeln:**
- Jede Person gehört zu genau einer ResearchGroup (1:N). Gruppen-Wechsel ⇒ neue Person-Anlage, alte bleibt historisch erhalten.
- Der PI einer ResearchGroup ist eine Person dieser Gruppe (Selbstreferenz via `research_group.pi`).
- Eine Institution kann optional mehrere ResearchGroups haben (reine Kontextinformation, keine harte Abhängigkeit).

### 3.2 Projekte & Probeneingänge

```
Project (Messvereinbarung, intern oder extern)
│  Name, responsible_pi (FK → Person), vereinbarter Umfang, Zeitraum, Status
│
├── SampleIntake (konkrete Probenlieferung)
│   │  Datum, submitter (FK → Person, wer die Lieferung gemacht hat)
│   │  importiertes Excel (archiviert), Anmerkungen
│   │
│   └── OriginalSample (1:n)
│       │  Kunden-Label (deren Beschriftung), LIMS-ID (unsere, auto)
│       │  Matrix (Gewebe/Zelllysat/Plasma/...), Volumen, Kommentar
│       │  Status, Lagerort (-80°C)
│       │
│       ├── Extract (Vorextraktion, Protokoll: "Pre-Screen")
│       │     LIMS-ID, Status, Lagerort (-20°C), Protokoll, MasterMix
│       │
│       ├── Extract (Standardextraktion, Protokoll: "SPE Standard")
│       │   │  LIMS-ID, Status, Lagerort (-20°C)
│       │   │
│       │   └── Extract (Derivatisierung AUF diesem Extrakt)
│       │         LIMS-ID, Status, Lagerort (-20°C)
│       │
│       └── Extract (Spezialextraktion, Protokoll: "LLE Spezial")
│             LIMS-ID, Status, Lagerort (-20°C)
```

**Rollen-Unterscheidung pro Projekt:**
- `Project.responsible_pi` — langfristig zuständig, meist der PI der liefernden Gruppe. Stabil über die Projekt-Laufzeit.
- `SampleIntake.submitter` — wer diese konkrete Lieferung gemacht hat. Kann bei Projekt-Laufzeit von 2 Jahren mehrmals wechseln (z.B. Postdoc macht Lieferung 1, Doktorand macht Lieferung 2).

**Schlüsselregel:** Jeder Extract hat immer eine direkte Referenz zur Originalprobe (`original_sample`), auch bei Derivaten. Zusätzlich hat ein Derivat eine Referenz zum Eltern-Extrakt (`parent_extract`). So kann von jedem Punkt im Baum sofort zur Originalprobe navigiert werden.

---

## 4. Module & Features

### 4.1 Modul: Parties, Projekte & Probeneingang

**Zweck:** Verwaltung von Stammdaten (Institutionen, Forschungsgruppen, Personen), Projekten (Messvereinbarungen), Probenlieferungen und der initialen Probenregistrierung.

**Apps:** `parties`, `projects`, `samples` (siehe Constitution, Section "Modularität").

#### Parties (parties-App)

| Feature | Beschreibung | Priorität |
|---|---|---|
| Institution anlegen | Name, Adresse (Freitext), optionale Web-URL | v1 |
| ResearchGroup anlegen | Name, Institution (FK, optional), PI (FK auf Person, nach erster Person anlegbar) | v1 |
| Person anlegen | Vorname, Nachname, E-Mail, Rolle, ResearchGroup (FK) | v1 |
| Internes Lab als ResearchGroup | Seed-Data beim ersten Start; eigenes Personal als Personen darin | v1 |
| Personen-Suche | Nach Name, E-Mail, ResearchGroup | v1 |
| Aktive Mitglieder einer Gruppe | "Wer arbeitet gerade in AG Müller?" | v1 |

#### Project (projects-App)

| Feature | Beschreibung | Priorität |
|---|---|---|
| Projekt anlegen | Name, responsible_pi (FK → Person), vereinbarter Umfang (n_samples, Methoden), Zeitraum, Status | v1 |
| Übersicht | Liste aller Projekte mit Status (planned, active, completed, archived) | v1 |
| Fortschritts-Tracking | "Von 50 Proben sind 32 extrahiert, 18 stehen aus" — automatisch berechnet | v1 |
| Interne vs. externe Projekte | Unterscheidung über ResearchGroup (internes Lab vs. externe Gruppe) | v1 |
| Dokument-Ablage | Vereinbarungen, Korrespondenz als Dateien anhängen | Später |

#### SampleIntake (Probeneingang)

| Feature | Beschreibung | Priorität |
|---|---|---|
| Probeneingang erstellen | Datum, Projekt zuordnen, Anmerkungen | v1 |
| Excel-Import | Template hochladen → Preview → Validierung → Proben anlegen | v1 |
| Import-Validierung | Fehlende Pflichtfelder, Duplikat-Kunden-IDs, Format-Checks | v1 |
| Excel-Archivierung | Original-Datei wird gespeichert als Beleg | v1 |
| Excel-Template-Download | Leeres Template zum Versenden an Kunden | v1 |
| Manuelle Eingabe | Einzelne Proben ohne Excel anlegen (Fallback) | v1 |

**Excel-Template — Pflichtfelder:**
- Kunden-ID / Label (was auf dem Tube steht)
- Probenmatrix (Gewebe, Zelllysat, Plasma, Serum, Urin, Sonstiges)

**Excel-Template — Optionale Felder:**
- Volumen / Menge
- Probanden-ID
- Kommentar / Freitext
- Weitere Metadaten (flexibel, als Schlüssel-Wert-Paare oder JSON)

#### OriginalSample

| Feature | Beschreibung | Priorität |
|---|---|---|
| Duale Identifikation | Kunden-Label + auto-generierte LIMS-ID | v1 |
| LIMS-ID-Format | Konfigurierbares Prefix + Sequenz (z.B. S-2025-00001) | v1 |
| Status-Tracking | State Machine (siehe Abschnitt 5) | v1 |
| Proben-Detail | Alle Infos, alle Extrakte, vollständige Historie | v1 |
| Suche | Nach Kunden-Label, LIMS-ID, Projekt, Matrix, Status | v1 |
| Lagerort-Zuordnung | Position im -80°C Freezer (Freezer → Schublade → Rack → Position) | v1 (simpel) |
| Freeze-Thaw-Zähler | Wie oft wurde die Probe aufgetaut? Automatisch bei Status-Wechsel. | v1 |

---

### 4.2 Modul: Extraction Management

**Zweck:** Planung, Durchführung und Dokumentation von Extraktionen. Inkl. IS/Mastermix-Konfiguration und druckbaren Bench-Dokumenten.

#### ExtractionProtocol

| Feature | Beschreibung | Priorität |
|---|---|---|
| Protokoll-Verwaltung | Name, Beschreibung, Schritte, Reagenzien, Standard-MasterMix-Template | v1 |
| Protokoll-Typen | Vorextraktion, Standardextraktion, Spezialextraktion, Derivatisierung | v1 |
| Mehrstufigkeit | Protokoll kann als "Folge-Protokoll" auf einem anderen basieren (Derivatisierung) | v1 |

#### IS & Mastermix (Untermodul)

| Feature | Beschreibung | Priorität |
|---|---|---|
| InternalStandard-Katalog | Name, Kürzel, Stammlösungs-Konzentration, Lösungsmittel, Lot-Nr, Ablaufdatum | v1 |
| MasterMixTemplate | Default-Rezept pro Protokoll: welche IS, welche Konzentration, welches Volumen pro Probe | v1 |
| MasterMixPreparation | Was tatsächlich in einen Batch reinkam: basierend auf Template, mit Abweichungen dokumentierbar | v1 |
| IS austauschen/ergänzen | Beim Batch-Erstellen: IS abwählen, andere hinzufügen, Konzentrationen anpassen | v1 |
| Lot-Nr pro Batch | Welche Stammlösung (Lot) wurde für welchen IS verwendet | v1 |
| IS-Lager-Tracking | Bestandsführung, Ablaufdatum-Warnungen, Lagerorte | Später |

#### ExtractionBatch

| Feature | Beschreibung | Priorität |
|---|---|---|
| Batch-Erstellung | Protokoll wählen → verfügbare Proben sehen → Subset auswählen | v1 |
| Freie Zusammenstellung | Proben aus beliebigen Probeneingängen mischbar (meist gleiche Studie, aber nicht erzwungen) | v1 |
| Mastermix konfigurieren | Template vorladen → bestätigen oder anpassen | v1 |
| Druckbare Probenliste | Tabellarisch: Position, Kunden-Label, LIMS-ID, Matrix, Volumen | v1 |
| Druckbares Extraktionsprotokoll | Methode, Reagenzien, Schritte mit Checkboxen, MasterMix-Zusammensetzung | v1 |
| Druckbare Plate-Map | Visuelle Draufsicht (bei Plate-Workflows) mit Farbcodierung | v1 |
| Batch-Header auf Drucken | Batch-ID, Datum, Analyst, Protokoll, Druckzeitpunkt | v1 |
| Rückdokumentation | "Extraktion abgeschlossen" — ein Klick. Proben → Status PREPARED. | v1 |
| Abweichungen dokumentieren | Freitextfeld für Auffälligkeiten bei der Bench-Arbeit | v1 |
| Einzelne Proben als fehlgeschlagen markieren | Pro Probe im Batch: "Extraktion fehlgeschlagen" mit Grund | v1 |
| Batch-Status-Tracking | State Machine (siehe Abschnitt 5) | v1 |
| Hamilton-Worklist | CSV-Export für Hamilton Starlet statt druckbarer Liste | Optional/Später |

#### Extract (Ergebnis einer Extraktion)

| Feature | Beschreibung | Priorität |
|---|---|---|
| Auto-Erstellung | Beim Abschließen eines Batches werden Extracts für alle Proben erstellt | v1 |
| Verknüpfung | → OriginalSample (immer), → ParentExtract (bei Derivaten), → ExtractionBatch, → Protokoll | v1 |
| Eigene LIMS-ID | Auto-generiert, z.B. E-2025-00001 | v1 |
| Lagerort-Zuordnung | Position im -20°C Freezer | v1 |
| Status-Tracking | Eigene State Machine (siehe Abschnitt 5) | v1 |
| Derivatisierung | Ein Extrakt kann Ausgangsmaterial für einen weiteren Extraktions-Batch sein (Folge-Protokoll) | v1 |

---

### 4.3 Modul: Analysis & Quantification

**Zweck:** Tracking von MS-Messungen, Import von Rohdaten, Quantifizierung, batch-übergreifende Auswertung.

#### MeasurementRun

| Feature | Beschreibung | Priorität |
|---|---|---|
| Run erstellen | Verknüpfung mit ExtractionBatch, Instrument, Messmethode | v1 |
| Messvorbereitung dokumentieren | Resuspension, Verdünnung auf 96-Well-Plate, Plate-Layout | v1 |
| Run als "gemessen" markieren | Status-Wechsel, Datum, Analyst, Instrument | v1 |
| Rohdaten-Referenz | Dateipfad/-name der Instrument-Rohdaten (z.B. .wiff, .raw) | v1 |
| 96-Well-Plate-Tracking | Welcher Extrakt in welchem Well — Verknüpfung für Ergebnis-Zuordnung | v1 |

#### Intensity Import & Quantifizierung

| Feature | Beschreibung | Priorität |
|---|---|---|
| Intensity-Datei hochladen | txt/csv von LipidView oder LipidXplorer, verknüpft mit MeasurementRun | v1 |
| lipidquant-Integration | IS-Normalisierung → Blank Subtraction → Response-Faktoren → Regression | v1 (simpel) |
| Sample-Type automatisch | Blank/QC/Calibrator/Unknown aus LIMS-Kontext, kein manuelles Zuordnen | v1 |
| IS-Konzentrationen aus MasterMix | Automatisch aus ExtractionBatch.MasterMixPreparation | v1 |
| Ergebnisse speichern | Konzentrationen pro Analyt pro Probe, verknüpft mit OriginalSample | v1 |
| Ergebnis-Export | Excel-Workbook mit quantifizierten Daten (wie aktuell ShinyLipidcountr) | v1 |

#### Batch-übergreifende Auswertung

| Feature | Beschreibung | Priorität |
|---|---|---|
| Zusammenführung | Ergebnisse aus mehreren ExtractionBatches/MeasurementRuns aggregieren | v1 |
| Fortschritt anzeigen | "Studie Weber: 32/50 Proben gemessen, 18 ausstehend" | v1 |
| Zusammenfassungs-Export | Gesamtergebnis über alle Batches einer Projekt als Excel | v1 |
| Einzel- vs. Gesamtauswertung | Batches können einzeln ausgewertet werden und am Ende zusammengefügt | v1 |

---

### 4.4 Modul: Storage (vereinfacht für v1)

**Zweck:** Nachvollziehen wo sich Proben und Extrakte befinden. Zwei getrennte Temperaturzonen.

#### -80°C Welt (Originalproben)

| Feature | Beschreibung | Priorität |
|---|---|---|
| Freezer-Struktur | Freezer → Schublade → Rack → Position | v1 (Datenmodell) |
| Probe zuordnen | Bei Einlagerung: Position zuweisen | v1 |
| Probe herausnehmen/zurückstellen | Status-Wechsel + Freeze-Thaw-Zähler automatisch | v1 |
| Suche | "Wo ist Probe X?" → Freezer A, Schublade 3, Rack B, Pos 4-2 | v1 |
| Freezer-Browser (visuell) | Drill-Down-Navigation mit Alpine.js | Später |

#### -20°C Welt (Extrakte)

| Feature | Beschreibung | Priorität |
|---|---|---|
| Freezer-Struktur | Freezer → Schublade → Rack → Position | v1 (Datenmodell) |
| Extrakt-Batch-Suche | "Wo sind die SPE-Standard-Extrakte von Studie Weber?" | v1 |
| Rein/Raus-Tracking | Extrakte werden häufig bewegt (Messvorbereitung, zurückstellen) | v1 |
| Freezer-Browser (visuell) | Farbcodierte Racks, Drill-Down, Position-Highlight bei Suche | Später |

---

### 4.5 Querschnitt-Features

| Feature | Beschreibung | Priorität |
|---|---|---|
| User-Accounts | Django Auth: Username, Passwort, Rolle | v1 |
| Rollen | Admin, Laborant, Viewer (read-only) | v1 |
| Audit Trail | Wer hat wann was geändert (django-fsm-log für Transitions) | v1 |
| Globale Suche | Proben, Extrakte, Batches, Projekten durchsuchbar | v1 |
| Dashboard | Übersicht: offene Batches, anstehende Messungen, Fortschritt pro Studie | Später |

---

## 5. State Machines

### 5.1 OriginalSample — zyklischer Lifecycle

Originalproben wechseln **mehrfach** zwischen Lagerung und Extraktion. Das ist kein linearer Pfad sondern ein Zyklus.

```
                    ┌──────────────────────┐
                    │                      │
                    ▼                      │
REGISTERED → STORED_80C → IN_EXTRACTION ──┘
                │
                ▼
             DEPLETED (aufgebraucht)

Jeder State → ON_HOLD (Investigation) möglich
Jeder State → CANCELLED (Terminal) möglich
```

**Transitions:**

| Von | Nach | Auslöser | Guard |
|---|---|---|---|
| REGISTERED | STORED_80C | Lagerort zugewiesen | Lagerort muss gesetzt sein |
| STORED_80C | IN_EXTRACTION | In Extraktions-Batch aufgenommen | — |
| IN_EXTRACTION | STORED_80C | Extraktion abgeschlossen, zurück in Freezer | Batch muss abgeschlossen sein |
| STORED_80C | DEPLETED | Probe aufgebraucht markiert | — |
| * | ON_HOLD | Manuelle Sperrung | Grund muss angegeben werden |
| * | CANCELLED | Stornierung | Grund muss angegeben werden |

**Automatisch bei Transition STORED_80C → IN_EXTRACTION:** Freeze-Thaw-Zähler +1.

### 5.2 Extract — zyklischer Lifecycle

Extrakte werden ebenfalls mehrfach bewegt: Messvorbereitung, Messung, zurück in Freezer, ggf. nochmal messen.

```
                ┌───────────────────────────────────┐
                │                                   │
                ▼                                   │
CREATED → STORED_20C → RESUSPENDED → PLATED → MEASURED ──┘
              │                                 │
              ▼                                 ▼
           DEPLETED                    IN_DERIVATIZATION
                                            │
                                            ▼
                                      (neuer Extract)
```

**Transitions:**

| Von | Nach | Auslöser |
|---|---|---|
| CREATED | STORED_20C | Extraktions-Batch abgeschlossen, Lagerort zugewiesen |
| STORED_20C | RESUSPENDED | Messvorbereitung gestartet |
| RESUSPENDED | PLATED | Auf 96-Well-Plate verdünnt |
| PLATED | MEASURED | MS-Run abgeschlossen |
| MEASURED | STORED_20C | Zurück in -20°C (für weitere Messung oder Aufbewahrung) |
| STORED_20C | IN_DERIVATIZATION | In Derivatisierungs-Batch aufgenommen |
| STORED_20C | DEPLETED | Extrakt aufgebraucht |

### 5.3 ExtractionBatch — linearer Lifecycle

```
CREATED → PLANNED → IN_PROGRESS → COMPLETED → CLOSED
```

| Von | Nach | Auslöser |
|---|---|---|
| CREATED | PLANNED | Proben ausgewählt, MasterMix konfiguriert |
| PLANNED | IN_PROGRESS | Probenliste gedruckt / Bench-Arbeit begonnen |
| IN_PROGRESS | COMPLETED | Rückdokumentation: "Extraktion abgeschlossen" |
| COMPLETED | CLOSED | Alle Extrakte eingelagert und verknüpft |

**Kaskadierung:** COMPLETED → alle Proben im Batch: Extract-Objekte erstellen, OriginalSamples → STORED_80C (zurück in Freezer).

### 5.4 MeasurementRun — linearer Lifecycle

```
CREATED → RUNNING → ACQUIRED → DATA_UPLOADED → QUANTIFIED → REPORTED
```

| Von | Nach | Auslöser |
|---|---|---|
| CREATED | RUNNING | Plate im Autosampler, Messung gestartet |
| RUNNING | ACQUIRED | Messung abgeschlossen |
| ACQUIRED | DATA_UPLOADED | Intensity-Datei hochgeladen |
| DATA_UPLOADED | QUANTIFIED | lipidquant-Berechnung durchgeführt |
| QUANTIFIED | REPORTED | Ergebnisse freigegeben / exportiert |

---

## 6. Datenmodell (Entity-Überblick)

### 6.1 Kern-Entities

```
Institution ──1:n──→ ResearchGroup ──1:n──→ Person
                           │  (PI-Referenz: ResearchGroup.pi → Person)
                           │
                           └── responsible_pi ─┐
                                               ▼
                                            Project ──1:n──→ SampleIntake ──1:n──→ OriginalSample
                                                                    │                      │
                                                           submitter (FK → Person)    1:n  │
                                                                                           ▼
ExtractionProtocol ←── ExtractionBatch ──n:m──→ OriginalSample
        │                     │
        │                     ├──1:1──→ MasterMixPreparation ──1:n──→ PrepComponent
        │                     │
        │                     └──1:n──→ Extract ─── parent_extract (self-ref, für Derivate)
        │                                  │
        └── MasterMixTemplate              │
              └──1:n──→ TemplateComponent   │
                            │               │
                    InternalStandard ←──────┘ (über PrepComponent)

MeasurementRun ──→ ExtractionBatch
      │
      ├──1:n──→ PlateWell ──→ Extract
      │
      └──1:1──→ IntensityFile
                    │
                    ▼
              AnalysisResult ──→ OriginalSample + Extract + Analyte
```

### 6.2 Storage-Entities

```
StorageUnit (Freezer)
  └── Drawer (Schublade)
       └── Rack
            └── RackPosition ──→ OriginalSample ODER Extract
```

### 6.3 Zwei IDs pro Probe

| Feld | Beschreibung | Beispiel |
|---|---|---|
| `customer_label` | Was der Kunde auf das Tube geschrieben hat / im Excel geliefert hat | "MUMC-P12-D7" |
| `lims_id` | Interne, auto-generierte ID | "S-2025-00347" |

Beide sind durchsuchbar. Der Kunde fragt nach seiner ID, das Labor arbeitet mit der LIMS-ID.

---

## 7. lipidquant — Quantifizierungs-Library

### 7.1 Architektur

Eigenständiges Python-Package ohne Django-Dependency. Kann im LIMS integriert oder standalone genutzt werden.

```
lipidquant (Pure Python Library, pandas-basiert)
├── normalization.py    IS-Normalisierung (Intensität / IS-Intensität)
├── blank.py            Blank Subtraction (benötigt Sample-Type-Zuordnung)
├── response.py         Response-Faktoren anwenden
├── calibration.py      Lineare Regression (Kalibrierkurve)
├── pipeline.py         Orchestriert alle Schritte
└── io.py               CSV/Excel/txt lesen und schreiben
```

### 7.2 Schnittstelle

```python
def quantify(
    intensities: pd.DataFrame,           # Rohdaten aus LipidView/LipidXplorer
    sample_types: dict[str, str],         # {"S-001": "unknown", "BLK-1": "blank"}
    is_config: list[dict],                # IS-Namen + Konzentrationen
    calibration_config: dict | None,      # Optional: Kalibrierpunkte
) -> pd.DataFrame:                        # Konzentrationen pro Analyt pro Probe
```

### 7.3 Nutzungsmodi

| Modus | Beschreibung | Input-Quelle |
|---|---|---|
| **LIMS-integriert** | Django-View ruft `quantify()` auf. Sample-Types und IS-Config kommen aus der Datenbank. | LIMS-DB |
| **Standalone CLI** | `lipidquant calculate --input data.csv --config is.json` | Dateien |
| **Standalone API** | FastAPI-Microservice (optional, für andere Tools) | HTTP/JSON |

### 7.4 LIMS-Vorteil

Was im standalone Modus manuell konfiguriert werden muss, weiß das LIMS bereits:
- **Sample-Types** → aus Batch-Zusammenstellung (welche Proben sind Blanks, QCs, Unknowns)
- **IS-Konzentrationen** → aus MasterMixPreparation (was tatsächlich reinkam)
- **Proben-Zuordnung** → aus PlateWell → Extract → OriginalSample (automatisches Matching)

---

## 8. UI/UX-Anforderungen

### 8.1 Allgemein

| Anforderung | Beschreibung |
|---|---|
| Server-Side Rendering | Django Templates + HTMX für 80% der Interaktion |
| Interaktive Inseln | Alpine.js für Freezer-Browser, Plate-Map, Batch-Builder |
| Print-Layouts | CSS `@media print` für alle Bench-Dokumente |
| Responsive | Muss auf Standard-Bildschirm (1920×1080) gut aussehen, kein Mobile nötig |
| Schnelle Navigation | Von jeder Probe in max. 2 Klicks zu: Extrakt-Liste, Batch-Info, Projekt |

### 8.2 Schlüssel-Screens

**Projekt--Übersicht:** Liste aller Projekten mit Fortschrittsbalken ("32/50 Proben gemessen").

**Probeneingang:** Excel hochladen → Preview-Tabelle → Validierung → Bestätigen. Einzelerfassung als Fallback.

**Proben-Detail:** Alle Infos zur Originalprobe, Baum-Darstellung aller Extrakte und Derivate, Lagerort, vollständige Status-Historie.

**Extraktions-Batch erstellen:** Protokoll wählen → verfügbare Proben filtern (nach Projekt, Status) → Subset auswählen → MasterMix konfigurieren (Template vorladen, anpassen) → Probenliste-Preview → Drucken/Bestätigen.

**Rückdokumentation:** Batch öffnen → Übersicht der Proben → "Extraktion abgeschlossen" (ein Klick). Optional: einzelne Proben als fehlgeschlagen markieren, Abweichungen notieren.

**Probensuche:** Ein Suchfeld, findet Kunden-Labels, LIMS-IDs, Projekten. Ergebnis zeigt Probe + aktuellen Status + Lagerort.

**Freezer-Browser (später):** Visuelle Drill-Down-Navigation: Freezer → Schublade → Rack → Position. Farbcodierung nach Probentyp oder Studie. Suchfunktion die Position highlightet.

---

## 9. Import/Export

### 9.1 Importe

| Was | Format | Wann |
|---|---|---|
| Probeneingangs-Excel | .xlsx / .csv | Bei jedem Probeneingang |
| Intensity-Tabellen | .txt / .csv (LipidView / LipidXplorer Format) | Nach Peak-Processing |
| Hamilton-Ergebnisse | .csv (TADM, Barcodes, Mapping) | Optional / Zukunft |

### 9.2 Exporte

| Was | Format | Wann |
|---|---|---|
| Probenliste (Druck) | HTML → Print / PDF | Vor Extraktion |
| Extraktionsprotokoll (Druck) | HTML → Print / PDF | Vor Extraktion |
| Hamilton-Worklist | .csv | Optional / Zukunft |
| MS-Sequence-File | Vendor-spezifisch | Später |
| Quantifizierungs-Ergebnis | .xlsx (wie ShinyLipidcountr-Output) | Nach Quantifizierung |
| Studien-Gesamtergebnis | .xlsx | Bei batch-übergreifender Auswertung |
| Excel-Template (leer) | .xlsx | Zum Versenden an Kunden |

---

## 10. Implementierungs-Prioritäten

### Phase A — Fundament (erstes lauffähiges System)

```
1. Project + SampleIntake + OriginalSample CRUD
2. Excel-Import mit Validierung und Preview
3. State Machine für OriginalSample
4. Extraktionsprotokoll + MasterMix-Template-Verwaltung
5. ExtractionBatch-Erstellung mit Probenauswahl + MasterMix
6. Druckbare Probenliste und Protokoll
7. Rückdokumentation (Batch abschließen → Extracts erstellen)
8. Extract-Modell mit Lagerort und Status
9. Suche (Proben nach Kunden-Label, LIMS-ID, Projekt)
10. Grundlegendes Storage (Freezer/Schublade/Rack/Position als Textfeld oder FK)
```

### Phase B — Messung & Auswertung

```
11. MeasurementRun-Tracking (erstellen, Status-Übergänge)
12. 96-Well-Plate-Zuordnung (Extract → Well)
13. Intensity-Datei-Upload und Verknüpfung
14. lipidquant Python-Port (Kern: IS-Norm, Blank Sub, Response, Regression)
15. LIMS-Integration von lipidquant (Sample-Types + IS-Config aus DB)
16. Ergebnis-Speicherung und Excel-Export
17. Batch-übergreifende Zusammenführung
```

### Phase C — UX & Visualisierung

```
18. Dashboard (Übersicht Studien-Fortschritt, offene Batches)
19. Freezer-Browser (Alpine.js, visuelles Drill-Down)
20. Plate-Map-Visualisierung
21. Erweiterte Suche / Filter
22. Derivatisierungs-Workflow (Extrakt → neuer Batch → neuer Extrakt)
```

### Phase D — Automatisierung (optional)

```
23. Hamilton Starlet-Anbindung (CSV-Worklist-Export)
24. MS Result-File-Parser (vendor-spezifisch)
25. MS Sequence-File-Generierung
26. IS-Lager-Tracking mit Bestandsführung
27. QC-Automatik
```

---

## 11. Offene Fragen (für spätere Klärung)

| Frage | Kontext |
|---|---|
| Welches Barcode-/Label-System einführen? | Aktuell handschriftlich. CryoLabels mit Barcode? QR-Codes? Labeldrucker? |
| Wie granular ist die Plate-Position-Zuordnung in v1? | Braucht man einen visuellen Plate-Editor, oder reicht eine Positions-Nummer? |
| Welche Metadaten kommen von Kunden, die das System flexibel abbilden muss? | Manche Kunden liefern Zeitpunkte, Dosen, Gewichte, Zellzahlen — alles unterschiedlich. |
| Resuspensions-Dokumentation — wie detailliert? | Nur "resuspendiert am Datum" oder Lösungsmittel, Volumen, Dauer? |
| Soll das LIMS die Rohdaten-Dateien selbst speichern oder nur Pfade/Referenzen? | Instrument-Dateien können groß sein (.wiff = mehrere GB). |
| Erster MS-Vendor-Parser: LipidView oder LipidXplorer? | Bestimmt das Format des Intensity-Imports. |
| Wie sieht die batch-übergreifende Auswertung konkret aus? | Einfaches Zusammenfügen der Tabellen, oder statistische Aggregation? |
