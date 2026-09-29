# Elba – vorbereitete Tauchplätze (wartet auf Freigabe)

**Status:** vorbereitet, **noch nicht aktiv.** `destinations.json`, `data/osm_clean/` und `divesites/` im Repo sind unverändert. Alles liegt in diesem Ordner, im selben Layout wie im Repo:

```
staging/elba/
  destinations-entry.json         # neuer Eintrag für destinations.json (slug "elba", parentSlug "italy")
  data/osm_clean/elba.json        # 35 Tauchplätze im osm_clean-Format (Source of Truth)
  divesites/elba/*.md             # 35 Tauchplatz-Seiten + overview.md
  divesites/elba/index.json       # mit scripts/sync_sites.py erzeugt
  apply.py                        # Übernahme ins Repo nach Freigabe
```

Stand der Recherche: 2026-09-29. Die Recherche lief über Websites von Tauchbasen, Infoelba, Elba CED, Taucher.Net, PADI, Wikipedia und islepark.it. Pro Platz wurden 1–16 Quellen tatsächlich gelesen und im Footer jeder Seite verlinkt. Wrack-Historie steht nur im Text, wenn mindestens zwei unabhängige Quellen sie bestätigen. Widersprüche zwischen Quellen sind im Text benannt.

## Übersicht

| Kennzahl | Wert |
|---|---|
| Tauchplätze | 35 |
| Validiert (≥ 1 platzspezifische Quelle bestätigt Typ und Tiefe) | 32 |
| Nicht validiert | 3 (La Miniera, Capo Stella Nord, Colle d'Orano) |
| Typen | 15 Riff, 8 Steilwand, 8 Secca/Pinnacle, 3 Wrack, 1 Muck |
| Einstieg | 32 Boot, 2 Ufer/Boot, 1 Ufer |
| Schwierigkeit | 25 Advanced, 5 Intermediate, 5 Beginner |

| # | Dein Name | Name im Datensatz | Typ | Tiefe (m) | Einstieg | Stufe | Valid. | Quellen |
|---|---|---|---|---|---|---|---|---|
| 1 | Forbici | **Le Forbici** | Riff | 15–40 | Boot | Advanced | ✅ | 5 |
| 2 | Punta Galera | **Punta Galera** | Riff | 7–50 | Boot | Advanced | ✅ | 7 |
| 3 | Ripalti | **Punta dei Ripalti** | Riff | 5–45 | Boot | Advanced | ✅ | 8 |
| 4 | Scoglio Remaiolo | **Scoglio del Remaiolo** | Steilwand | 0–45 | Boot | Advanced | ✅ | 12 |
| 5 | La Mineria | **La Miniera** | Muck (Sand) | 6–40 | Boot | Advanced | ⚠️ | 1 |
| 6 | Capo Calvo | **Capo Calvo** | Riff | 5–50 | Boot | Advanced | ✅ | 9 |
| 7 | Picchi di Pablo | **Picchi di Pablo** | Steilwand | 5–38 | Boot | Advanced | ✅ | 14 |
| 8 | Gemini West | **Gemini West** | Riff | 0–14 | Boot | Beginner | ✅ | 6 |
| 9 | Gemini East | **Gemini East** | Riff | 0–20 | Boot | Intermediate | ✅ | 5 |
| 10 | Gemini Rock | **Gemini Rock** | Riff | 0–20 | Boot | Beginner | ✅ | 5 |
| 11 | Corbelli | **I Corbelli** | Riff | 0–40 | Boot | Advanced | ✅ | 7 |
| 12 | Punta Morcone | **Punta Morcone** | Steilwand | 3–40 | Boot | Advanced | ✅ | 6 |
| 13 | SCOGLIO CHE BARA | **Scoglio che Bara** | Secca/Pinnacle | 7–35 | Boot | Advanced | ✅ | 5 |
| 14 | Capo Stella Nord | **Capo Stella Nord** | Riff | 0–30 | Boot | Intermediate | ⚠️ | 4 |
| 15 | Coralline Interne | **Coralline Interne** | Riff | 3–42 | Boot | Advanced | ✅ | 7 |
| 16 | Capo Fonza | **Secca di Capo Fonza** | Secca/Pinnacle | 3–45 | Boot | Advanced | ✅ | 5 |
| 17 | Scoglio della Triglia | **Scoglio della Triglia** | Riff | 0–30 | Boot | Intermediate | ✅ | 7 |
| 18 | Capo Poro | **Secca di Capo Poro** | Secca/Pinnacle | 30–50 | Boot | Advanced | ✅ | 4 |
| 19 | Secca di Fetovaia | **Secca di Fetovaia** | Secca/Pinnacle | 12–40 | Boot | Advanced | ✅ | 4 |
| 20 | Punta Fetovaia | **Punta di Fetovaia** | Riff | 12–40 | Boot | Advanced | ✅ | 4 |
| 21 | RELITTO POMONTE | **Relitto di Pomonte** (Elviscot) | Wrack | 2–12 | Ufer/Boot | Beginner | ✅ | 15 |
| 22 | Collo d'Orano | **Colle d'Orano** | Riff | 2–16 | Ufer/Boot | Beginner | ⚠️ | 4 |
| 23 | SAN´ ANDREA | **Sant'Andrea** | Riff | 0–40 | Ufer | Advanced | ✅ | 6 |
| 24 | Punta della Madonna | **Punta della Madonna** | Steilwand | 0–42 | Boot | Advanced | ✅ | 4 |
| 25 | Secca di Semoforo | **Secca del Semaforo** | Secca/Pinnacle | 38–52 | Boot | Advanced | ✅ | 7 |
| 26 | Scoglio della Nave | **Scoglio della Nave** | Steilwand | 0–40 | Boot | Advanced | ✅ | 7 |
| 27 | Secca di Santa Lucia | **Secca di Santa Lucia** | Secca/Pinnacle | 6–22 | Boot | Intermediate | ✅ | 6 |
| 28 | Lo Scoglietto | **Scoglietto di Portoferraio** | Riff | 5–40 | Boot | Advanced | ✅ | 16 |
| 29 | Lo Junker 52 | **Junker 52** | Wrack (Flugzeug) | 35–37 | Boot | Advanced | ✅ | 4 |
| 30 | Secca di Capo Vita | **Secca di Capo Vita** | Secca/Pinnacle | 6–24 | Boot | Intermediate | ✅ | 4 |
| 31 | L'Ancorone | **L'Ancorone** | Steilwand | 27–45 | Boot | Advanced | ✅ | 4 |
| 32 | Secca del Frate | **Secca del Frate** | Secca/Pinnacle | 3–30 | Boot | Advanced | ✅ | 7 |
| 33 | Cerboli | **Isola di Cerboli** | Steilwand | 10–45 | Boot | Advanced | ✅ | 5 |
| 34 | Punta delle Canelle | **Punta delle Cannelle** | Steilwand | 10–45 | Boot | Advanced | ✅ | 4 |
| 35 | Relitto Aereo | **Relitto Aereo (Islander)** | Wrack (Flugzeug) | 12–16 | Boot | Beginner | ✅ | 5 |

Die Tiefe im Datensatz (`depth` / `maxDepth`) ist jeweils der zweite Wert. Der erste Wert steht in `tags.depth_min`.

## Bitte vor der Freigabe entscheiden

### 1. Herkunft der Koordinaten (wichtig)
Alle 35 Koordinaten sind identisch mit den Markern der öffentlichen Tauchplatzkarte von **Aquanautic Elba** (Tauchbasis in Morcone, Capoliveri): <https://aquanautic-elba.de/tauchen/elbas-tauchplaetze/>. Einzige Ausnahme ist Scoglio che Bara, der rund 97 m daneben liegt. Die Karte enthält 36 Punkte, nur „La Corbella“ fehlt in deiner Liste.

- Das ist im Datensatz offen vermerkt: `tags.coordinates_source = "Aquanautic Elba dive-site map (aquanautic-elba.de); contributor-supplied"`.
- Aquanautic ist außerdem als Quelle im Footer der Seiten verlinkt, deren Beschreibung Angaben aus den Karten-Popups nutzt (Tiefe, Besonderheit, Strömung).
- **Empfehlung:** Einzelne GPS-Punkte sind Fakten. Die Übernahme fast der ganzen Karte kann in der EU aber das Datenbank-Herstellerrecht berühren. Wenn du nicht ohnehin mit der Basis in Kontakt bist, hol kurz deren Einverständnis ein, oder nenne sie zusätzlich in `ATTRIBUTION.md`.

### 2. Drei Koordinaten habe ich korrigiert (Original bleibt in `tags.coordinates_original`)

| Platz | Original (Karte) | Neu | Grund |
|---|---|---|---|
| Scoglietto di Portoferraio | 42.818888, 10.330925 | 42.8284, 10.3316 | Der Originalpunkt liegt ca. 1,1 km südlich der Insel, rund 145 m vor dem Ufer von Portoferraio. Der neue Punkt liegt an der Ostseite der Insel (Franata delle Cernie), Umriss laut OSM. |
| Secca del Frate | 42.854575, 10.443363 | 42.8684, 10.4753 | Quellen verorten die Secca 100–250 m N/NO von Palmaiola beim Felsen „Il Frate“. Der Originalpunkt liegt ca. 2,8 km WSW davon. Neuer Punkt: Felsen „Il Frate“ laut OSM. |
| Isola di Cerboli | 42.845765, 10.459843 | 42.8553, 10.5465 | Der Originalpunkt liegt ca. 7,3 km westlich der Insel im offenen Kanal. Neuer Punkt: Ankerbucht an der Südseite (OSM-Punkt „Cerboli Anchor“), dort legen die Boote laut Quellen an. |

Wenn du lieber die Originale willst: `lat`/`lon` in `data/osm_clean/elba.json` zurücksetzen und `python3 scripts/sync_sites.py elba` laufen lassen, nach der Übernahme.

### 3. Unsichere Koordinaten, die ich unverändert gelassen habe (`tags.position` = "uncertain…")
- **Junker 52:** Quellen nennen „ca. 300 m vor dem Ufer unter dem Leuchtturm von Portoferraio“. Taucher.Net warnt, dass veröffentlichte GPS-Daten absichtlich falsch waren. Außerdem hat der Marker exakt dieselbe Breite (42.813411) wie „Punta della Madonna“, möglicherweise ein Copy-Fehler auf der Karte.
- **Secca del Semaforo:** Der Marker liegt ca. 280 m vor der Küste, Quellen nennen etwa 0,5 sm vor Capo d'Enfola.
- **Secca di Capo Vita:** Der Marker liegt nah an der Küste, eine Quelle nennt „ca. 1 Meile vor Capo Vita“.
- **L'Ancorone:** Laut Quellen 200–300 m von der Secca di Capo Vita entfernt.
- **Relitto Aereo:** Quellen nennen Punta Nera bzw. Straccoligno (Capoliveri), der Marker liegt ca. 1,4 km NW der OSM-Punta-Nera.

Alle 35 Punkte liegen laut OSM-Küstenlinie im Wasser. Keiner liegt an Land.

### 4. Namen
Ich habe Tippfehler korrigiert und die lokal gebräuchlichen Namen verwendet. Deine Schreibweise bleibt jeweils in `tags.alt_name`.
- La Mineria → **La Miniera**
- Collo d'Orano → **Colle d'Orano**
- Secca di Semoforo → **Secca del Semaforo**
- SAN´ ANDREA → **Sant'Andrea**
- Forbici → **Le Forbici**
- Ripalti → **Punta dei Ripalti**
- Scoglio Remaiolo → **Scoglio del Remaiolo**
- Corbelli → **I Corbelli**
- Capo Fonza → **Secca di Capo Fonza**
- Capo Poro → **Secca di Capo Poro**
- Punta Fetovaia → **Punta di Fetovaia**
- Punta delle Canelle → **Punta delle Cannelle**
- Cerboli → **Isola di Cerboli**
- Lo Junker 52 → **Junker 52**
- RELITTO POMONTE → **Relitto di Pomonte** (Elviscot)
- Relitto Aereo → **Relitto Aereo (Islander)**: eindeutiger, weil manche Basen auch das Junker-Wrack „Relitto dell'aereo“ nennen.
- Lo Scoglietto → **Scoglietto di Portoferraio**: Lokal wird auch das Scoglio della Triglia „lo scoglietto“ genannt.

### 5. Schwierigkeitsgrade
Ich habe die Repo-Regel konsequent angewendet: über 30 m = Advanced, 18–30 m = Intermediate, unter 18 m = Beginner. Bis 20 m ist Beginner erlaubt, wenn eine Quelle „für alle Taucher“ sagt. Ausnahme: Secca del Frate (30 m) ist wegen starker Strömung Advanced.

Folge: **25 von 35 sind Advanced.** Darunter sind Plätze, die Basen als „für alle Level“ mit flacher Route beschreiben, etwa Scoglietto (Franata Nord 0–17 m), Sant'Andrea (Uferplatz), Picchi di Pablo, Punta della Madonna, Scoglio della Nave und I Corbelli. Die flachen Varianten sind jeweils im Text beschrieben. Wenn du für solche Multilevel-Plätze lieber Intermediate willst, sag Bescheid, dann passe ich das an.

### 6. Nicht validiert (⚠️)
- **La Miniera:** Einzige Quelle ist das Aquanautic-Popup (schwarzer Sand, Seespinnen, 6–40 m). Typ „muck“ und Bootseinstieg sind Platzhalter.
- **Capo Stella Nord:** Nur Aquanautic nennt Details (Tunnel, 0–30 m). Die übrigen Quellen beschreiben Capo Stella allgemein.
- **Colle d'Orano:** Nur eine Hotel-/Tourismusseite beschreibt einen Tauchgang (2–16 m, Einstieg über die Bucht Le Buche). Der Typ ist nicht belegt.

### 7. Weitere Hinweise
- **Gemini West/East** liegen nur ca. 130 m auseinander. Aquanautic führt sie aber getrennt mit unterschiedlichen Tiefen, deshalb habe ich sie getrennt gelassen. **Gemini Rock** ist vermutlich identisch mit „La Focacciola“ (Elba CED), das ist aber nicht belegt.
- **I Corbelli ≠ La Corbella/Isola Corbella** (bei Capo Stella). Das sind zwei verschiedene Plätze.
- **Elviscot:** Name, Datum (10.01.1972), Ogliera-Felsen, Baujahr 1960 (Niederlande) und ca. 62 m Länge sind mehrfach belegt. Widersprüchlich sind der Abfahrtshafen (Taranto vs. Neapel), die Ursache (Unwetter vs. Wassereinbruch) und die Seitenlage. Das ist im Text offen benannt.
- **Junker 52:** Datum und Umstände des Absturzes sind nicht belegt und deshalb nicht im Text.
- **Relitto Aereo:** Die Geschichte der Notwasserung (1980) stammt aus nur einer Quelle und ist im Text so gekennzeichnet.
- **Schutzstatus:** Laut Nationalpark (islepark.it, Stand 08/2025) gehören die **Gewässer um Elba nicht zum Parkgebiet**. Das Scoglietto liegt in einer Schutzzone von 1971 mit Fischereiverbot, verwaltet von der Comune di Portoferraio.
- **Attribution im Datensatz:** `tags.source = "community_contribution"`, `tags.addedBy = "gismo1337"`. Das kannst du ändern, falls du anders genannt werden willst.

## Übernahme nach Freigabe

Vom Repo-Root aus:

```bash
python3 staging/elba/apply.py --cleanup   # fügt Elba in destinations.json ein (nach czech-republic),
                                          # kopiert JSON + Markdown, führt sync_sites.py aus,
                                          # löscht danach staging/elba
```

In einer Kopie des Repos getestet: Das Skript fügt nur den neuen Eintrag ein, `sync_sites.py elba` meldet danach 0 Änderungen, und `scripts/validate_coordinates.py` meldet für Elba keine Probleme.
