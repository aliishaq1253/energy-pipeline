# Energy Data Pipeline

End-to-end ETL-Pipeline für europäische Stromverbrauchsdaten.
Lädt öffentliche Energiedaten, bereinigt sie und speichert sie in einer SQLite-Datenbank.

## Architektur

CSV (OPSD) → Extract → Transform → Load → SQLite → Power BI

## Daten

Datensatz: [Open Power System Data](https://open-power-system-data.org/time_series)
- Datei: `time_series_60min_singleindex.csv`
- Zeitraum: 2015–2020
- Inhalt: Stromverbrauch, Solar- und Windenergie für 32 europäische Länder

## Setup

```bash
# 1. Repository klonen
git clone https://github.com/aliishaq1253/energy-pipeline.git
cd energy-pipeline

# 2. Virtual Environment erstellen
python3 -m venv venv
source venv/bin/activate

# 3. Pakete installieren
pip install -r requirements.txt

# 4. Datensatz herunterladen
# https://open-power-system-data.org/time_series
# Datei: time_series_60min_singleindex.csv → in diesen Ordner legen

# 5. Pipeline starten
python pipeline.py
```

## Was die Pipeline macht

- **Extract:** CSV-Datei laden (50.401 Zeilen, 300 Spalten)
- **Transform:** 
  - Nur Deutschland-Daten auswählen
  - Fehlende Werte behandeln (Solar → 0, Rest → entfernen)
  - Neue Spalten berechnen (Erneuerbare, Vorhersagefehler)
  - Timestamp aufteilen (Jahr, Monat, Stunde, Wochentag)
- **Load:** Bereinigte Daten in SQLite speichern (50.304 Zeilen)

## Ergebnisse

| Jahr | Ø Verbrauch (MW) | Ø Erneuerbare |
|------|-----------------|---------------|
| 2015 | 54.737 | 21.5% |
| 2016 | 55.400 | 20.3% |
| 2017 | 56.178 | 24.5% |
| 2018 | 56.946 | 25.9% |
| 2019 | 55.990 | 28.8% |
| 2020 | 53.048 | 32.6% |

## Tech Stack

- Python 3.11
- pandas
- SQLite