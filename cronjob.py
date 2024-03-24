import psycopg2
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv
import os


try:
    # Connecting to PostgreSQL
    load_dotenv()
    conn = psycopg2.connect( db_user = os.getenv('DB_USER'),
    db_password = os.getenv('DB_PASSWORD'),
    db_host = os.getenv('DB_HOST'),
    db_port = os.getenv('DB_PORT'),
    db_name = os.getenv('DB_NAME'),
    db_table = os.getenv('DB_TABLE')
    )
    
    cur = conn.cursor()
    

    # Fetching earthquake data
    url = f"https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime=2024-03-22&endtime=2024-03-23"
    response = requests.get(url)
    
    # Checking response status
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data. Status code: {response.status_code}")

    data = response.json()
    timestamp = data['features'][0]['properties']['time'] / 1000
    date = datetime.fromtimestamp(timestamp, timezone.utc).date()
    count = len(data['features'])

    # Insert into the database
    sql_query = '''INSERT INTO evsa_earthquakes (date, earthquakes) VALUES (%s, %s)'''
    cur.execute(sql_query, (date, count))
    conn.commit()

    print("Data inserted successfully.")
    
except psycopg2.Error as e:
    print("Error occurred during database operation:", e)
    
except requests.RequestException as e:
    print("Error occurred during API request:", e)
    
except Exception as e:
    print("An unexpected error occurred:", e)
    
finally:
    # Close database connection
    if conn:
        conn.close()