from flask import Flask, render_template
import pymysql

app = Flask(__name__)
app.template_folder = 'templates'
if __name__ == '__main__':
    app.debug = True
    app.run()

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


