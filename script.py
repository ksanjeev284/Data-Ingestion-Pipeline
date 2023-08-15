import webbrowser
import requests
import mysql.connector
from datetime import date
import time
from flask import Flask, render_template
import pymysql

app = Flask(__name__)
app.template_folder = 'templates'

def fetch_weather_data():
    while True:
        # API endpoint and parameters
        API_KEY = '3ce109e5535b3bb9f44a2de1aa849ea1'
        CITY = 'Hyderabad'
        URL = f'http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}'

        # Fetch weather data from the API
        response = requests.get(URL)
        weather_data = response.json()

        # Extract relevant data from the response
        temperature = weather_data['main']['temp']
        humidity = weather_data['main']['humidity']
        description = weather_data['weather'][0]['description']

        # Connect to the MySQL database
        db_connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='weather_app'
        )

        # Create a cursor object to execute SQL queries
        cursor = db_connection.cursor()

        # Insert weather data into the database
        insert_query = "INSERT INTO weather_forecast (date, temperature, humidity, description) VALUES (%s, %s, %s, %s)"
        current_date = date.today()
        weather_values = (current_date, temperature, humidity, description)

        cursor.execute(insert_query, weather_values)
        db_connection.commit()

        # Close the cursor and the database connection
        cursor.close()
        db_connection.close()

        print("Weather data inserted successfully.")
        print(weather_data)

        # Wait for 5 minutes before fetching data again
        time.sleep(300)  # 5 minutes in seconds

# Define the Flask route and function to serve the data
def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='root',
        database='weather_app',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/')
def index():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM weather_forecast")
    data = cursor.fetchall()
    connection.close()
    return render_template('index.html', data=data)

if __name__ == '__main__':
    app.debug = True
    # Start a new thread to fetch weather data every 5 minutes
    import threading
    threading.Thread(target=fetch_weather_data).start()
    webbrowser.open('http://127.0.0.1:5000/')
    app.run()

