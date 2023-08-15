import requests
import mysql.connector
from datetime import date

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