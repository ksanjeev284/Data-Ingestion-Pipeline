import os
import webbrowser
import requests
import threading
import time
from datetime import date
from flask import Flask, render_template, request
from flask_socketio import SocketIO
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


app = Flask(__name__)
app.template_folder = 'templates'
socketio = SocketIO(app)

API_KEY = '3ce109e5535b3bb9f44a2de1aa849ea1'
CITY = 'Hyderabad'
URL = f'http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}'
DATABASE_URL = 'mysql+pymysql://root:root@localhost/weather_app'

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

class WeatherFetcher(threading.Thread):
    def __init__(self, stop_event, session):
        super().__init__()
        self.stop_event = stop_event
        self.session = session

    def run(self):
        while not self.stop_event.is_set():
            try:
                response = requests.get(URL)
                response.raise_for_status()

                weather_data = response.json()
                self.insert_weather_data(weather_data)

                print("Weather data inserted successfully.")
                print(weather_data)

                # Emit the new weather data to connected clients
                socketio.emit('new_weather_data', weather_data)

            except requests.exceptions.RequestException as req_exc:
                print("Request Exception:", req_exc)
            except Exception as error:
                print("Error:", error)

            time.sleep(300)

    def insert_weather_data(self, weather_data):
        temperature = weather_data['main']['temp']
        humidity = weather_data['main']['humidity']
        description = weather_data['weather'][0]['description']

        current_date = date.today()
        insert_query = text("INSERT INTO weather_forecast (date, temperature, humidity, description) VALUES (:date, :temperature, :humidity, :description)")
        self.session.execute(
            insert_query,
            {"date": current_date, "temperature": temperature, "humidity": humidity, "description": description}
        )
        self.session.commit()

@app.route('/')
def index():
    try:
        with Session() as session:
            select_query = text("SELECT * FROM weather_forecast")
            data = session.execute(select_query).fetchall()
            return render_template('index.html', data=data)
    except Exception as error:
        print("Error:", error)
        return "An error occurred."

@app.route('/get_weather_data')
def get_weather_data():
    try:
        response = requests.get(URL)
        response.raise_for_status()
        weather_data = response.json()
        socketio.emit('new_weather_data', weather_data)  # Emit the new data to connected clients
        return "Weather data fetched and sent to clients."
    except requests.exceptions.RequestException as req_exc:
        return "Request Exception: " + str(req_exc)
    except Exception as error:
        return "Error: " + str(error)

if __name__ == '__main__':
    stop_event = threading.Event()
    session = Session()
    weather_fetcher = WeatherFetcher(stop_event, session)
    
    app.debug = False

    @socketio.on('connect')
    def handle_connect():
        print("Client connected")

    @socketio.on('disconnect')
    def handle_disconnect():
        print("Client disconnected")

    app_thread = threading.Thread(target=socketio.run, args=(app, '0.0.0.0', 5000))
    app_thread.start()

    webbrowser.open('http://127.0.0.1:5000/')

    try:
        weather_fetcher.start()
        app_thread.join()
    except KeyboardInterrupt:
        stop_event.set()
        weather_fetcher.join()
        print("Thread stopped gracefully.")
