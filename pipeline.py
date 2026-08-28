import pandas as pd
import sqlite3

def extract(filepath):
    """Lädt die CSV-Datei und gibt sie als Pandas DataFrame zurück."""
    print("Lade Daten...")
    df = pd.read_csv(filepath,sep=',', header=0, encoding='utf-8', low_memory=False)
    print(f"Geladene Daten: {len(df)} Zeilen, {len(df.columns)} Spalten")
    return df

def transform(df):
    """Bereinigt und transformiert die Daten."""
    print("Transformiere Daten...")
    
    # Nur DE-Spalten auswählen
    de_columns = ["utc_timestamp",
                  "DE_load_actual_entsoe_transparency",
                  "DE_load_forecast_entsoe_transparency",
                  "DE_solar_generation_actual",
                  "DE_wind_onshore_generation_actual"]
    
    df = df[de_columns]
    
    # Spalten umbenennen
    df = df.rename(columns={
        "utc_timestamp": "timestamp",
        "DE_load_actual_entsoe_transparency": "load_actual_mw",
        "DE_load_forecast_entsoe_transparency": "load_forecast_mw",
        "DE_solar_generation_actual": "solar_mw",
        "DE_wind_onshore_generation_actual": "wind_mw"
    })
    
    # Fehlende Werte behandeln
    df["solar_mw"] = df["solar_mw"].fillna(0)
    df = df.dropna()
    
    # Neue Spalten berechnen
    df["renewables_mw"] = df["solar_mw"] + df["wind_mw"]
    df["renewables_share_pct"] = (df["renewables_mw"] / df["load_actual_mw"] * 100).round(1)
    df["forecast_error_mw"] = df["load_actual_mw"] - df["load_forecast_mw"]
    
    # Timestamp bereinigen
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["year"] = df["timestamp"].dt.year
    df["month"] = df["timestamp"].dt.month
    df["hour"] = df["timestamp"].dt.hour
    df["weekday"] = df["timestamp"].dt.day_name()
    
    print(f"Transformiert: {len(df)} Zeilen")
    return df

def load(df, db_path):
    """Speichert die Daten in SQLite."""
    print("Speichere in Datenbank...")
    
    conn = sqlite3.connect(db_path)
    
    df.to_sql("energy_de",
              conn,
              if_exists="replace",
              index=False)
    
    # Kurze Kontrolle
    count = conn.execute("SELECT COUNT(*) FROM energy_de").fetchone()[0]
    print(f"Gespeichert: {count} Zeilen in {db_path}")
    
    conn.close()

def export_excel(df, filepath):
    """Exportiert die bereinigten Daten als Excel-Datei."""
    print("Exportiere nach Excel...")
    
    # Zeitzone entfernen für Excel-Kompatibilität
    df = df.copy()
    df["timestamp"] = df["timestamp"].dt.tz_localize(None)
    
    # Zusammenfassung pro Jahr
    yearly_summary = df.groupby("year").agg(
        avg_load_mw=("load_actual_mw", "mean"),
        avg_renewables_pct=("renewables_share_pct", "mean"),
        avg_forecast_error=("forecast_error_mw", "mean")
    ).round(1).reset_index()
    
    # Excel mit zwei Sheets erstellen
    with pd.ExcelWriter(filepath, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Rohdaten", index=False)
        yearly_summary.to_excel(writer, sheet_name="Zusammenfassung", index=False)
    
    print(f"Exportiert: {filepath}")

# main function to run the ETL process
if __name__ == "__main__":
    print("Starting ETL pipeline...")
    
    try:
        # ETL-Prozess ausführen
        df_raw = extract("time_series_60min_singleindex.csv") # Hier den Pfad zur CSV-Datei anpassen
        df_clean = transform(df_raw) # Hier den Pfad zur CSV-Datei anpassen
        load(df_clean, "energy_data.db") # Hier den Pfad zur SQLite-Datenbank anpassen
        export_excel(df_clean, "energy_data.xlsx") # Hier den Pfad zur Excel-Datei anpassen
        print("ETL pipeline completed.")
    except FileNotFoundError:
        print("Fehler: CSV-Datei nicht gefunden!")
    except Exception as e:
        print(f"Unerwarteter Fehler: {e}")
