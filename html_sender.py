import os
import json
from flask import Flask, render_template

app = Flask(__name__)

# Folder, w którym znajdują się dane
DATA_FOLDER = "data"

@app.route("/")
def show():
    # Inicjalizacja pustego słownika na dane
    measurements = {}

    try:
        # Przechodzimy po plikach w folderze "data"
        files = os.listdir(DATA_FOLDER)

        # Sprawdzamy, czy folder jest pusty
        if not files:
            measurements = {"Brak plików w folderze": [{"location": "", "timestamp": "", "pm25": {}}]}

        # Dodajemy zawartość każdego pliku do listy
        for file in files:
            filepath = os.path.join(DATA_FOLDER, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                try:
                    # Wczytujemy zawartość pliku
                    file_contents = f.read()

                    # Próba załadowania wielu obiektów JSON (jeśli plik nie jest pojedynczym obiektem)
                    while file_contents:
                        try:
                            # Próba załadowania pojedynczego obiektu
                            entry, idx = json.JSONDecoder().raw_decode(file_contents)
                            
                            nr_indeksu = entry.get("nr_indeksu", "Brak numeru indeksu")
                            
                            # Sprawdzamy, czy mamy dane o tym numerze indeksu w słowniku
                            if nr_indeksu not in measurements:
                                measurements[nr_indeksu] = []

                            # Dodajemy dane do odpowiedniego numeru indeksu
                            measurements[nr_indeksu].append({
                                "location": entry.get("location", "Brak lokalizacji"),
                                "timestamp": entry.get("timestamp", "Brak daty"),
                                "pm25_value": entry.get("pm25", {}).get("value", "Brak danych"),
                                "pm25_units": entry.get("pm25", {}).get("units", "")  
                            })


                            file_contents = file_contents[idx:].lstrip()

                        except json.JSONDecodeError as e:
                            # Obsługuje błąd w przypadku niepoprawnego formatu
                            print(f"Błąd dekodowania w pliku {file}: {str(e)}")
                            break

                except Exception as e:
                    # Obsługuje inne błędy związane z odczytem pliku
                    print(f"Błąd odczytu pliku {file}: {str(e)}")
                    measurements = {"Błąd odczytu pliku": [{"location": str(e), "timestamp": "", "pm25": {}}]}

    except Exception as e:
        # W przypadku błędu, zapisujemy szczegóły błędu w zmiennej
        measurements = {"Błąd: " + str(e): [{"location": "", "timestamp": "", "pm25": {}}]}

    # Zwracamy szablon, przekazując dane
    return render_template("index.html", measurements=measurements)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
