import json
import requests
import time
import os
from paho.mqtt import client as mqtt
from mqtt_sender import MqttSender as mqtt_sender

DATA_FOLDER = "data"
api_key = "71b03d5fa7a6f146e4afa78cb4aa1495949f655d28f8c1d0440b2779634c7ffd"

# Ustawienie lokalizacji na stałą wartość na potrzeby debugowania
location = os.environ["location"]#="10566"
broker = os.environ["broker"]  #='167.172.164.168'
port  = int(os.environ["port"]) #= 1883
username = os.environ["username"] = "261293"
password = os.environ["password"] = "sys.wbud"


class WeatherRequester:
    def __init__(self, city, mqtt_sender, nr_indeksu):
        self.location = city
        self.mqtt = mqtt_sender
        self.nr_indeksu = nr_indeksu  

    def loop(self):
        while True:
            params = {"limit": 1}
            headers = {"X-API-Key": api_key}

            # Zapytanie do API
            response = requests.get(f"https://api.openaq.org/v2/locations/{self.location}", headers=headers, params=params)

            if response.status_code == 200:
                data = response.json()
                print(json.dumps(data, indent=4))  # Cała odpowiedź API

                results = data.get("results", [])
                
                if results:
                    location_name = results[0].get("name", "Brak nazwy")
                    location_time = results[0].get("lastUpdated", "Brak wskazania")
                    pm25_data = next((param for param in data["results"][0]["parameters"] if param["parameter"] == "pm25"), {})
                    pm25_last_value = pm25_data.get('lastValue', 'Brak wartości')
                    pm25_units = pm25_data.get('unit', 'Brak wartości')
                    
            
                    message = json.dumps({
                        "nr_indeksu": self.nr_indeksu,
                        "location": location_name,
                        "timestamp": location_time,
                        "pm25": {
                            "value": pm25_last_value,
                            "units": pm25_units
                        }
                    })
                    
                    print(f"location: {location_name}\ntimestamp: {location_time}\npm25: {message}\n")
                    self.mqtt.publish(f"{self.nr_indeksu}/location", message)
                else:
                    print("Brak wyników dla podanej lokalizacji.")
            else:
                print(f"Błąd! Status HTTP: {response.status_code}")
                print(response.text)

            time.sleep(30)  # Czekanie 30 sekund przed kolejnym zapytaniem
            #exit()

def save_to_file(nr_indeksu, location, data):
    os.makedirs(DATA_FOLDER, exist_ok=True)
    filename = os.path.join(DATA_FOLDER, f"{nr_indeksu}-{location}.txt")
    try:
        with open(filename, 'a') as file:
            file.write(f"{data}\n")
        print(f"Dane zapisane w pliku: {filename}")
    except Exception as e:
        print(f"Błąd zapisu do pliku {filename}: {e}")


def on_message(client, userdata, msg):
    topic_parts = msg.topic.split('/')
    if len(topic_parts) == 2:
        nr_indeksu = topic_parts[0]
        locat = topic_parts[1]
        if not (nr_indeksu.isdigit() and len(nr_indeksu) ==6):
            return
        message = msg.payload.decode()
        save_to_file(nr_indeksu, locat, message)


mqtt_client = mqtt_sender(broker, port, username, password)
mqtt_client.connect()

mqtt_client.subscribe("+/location", on_message)
mqtt_client.sub_loop()

# Inicjalizacja klasy WeatherRequester z lokalizacją
requester = WeatherRequester(location, mqtt_client, nr_indeksu="261293")
requester.loop()
