import psycopg2
import requests
import datetime
from dotenv import load_dotenv
import os

conn= None
cur = None
start_date=  datetime.date.today() - datetime.timedelta(days=1)
end_date = datetime.date.today()

try:
    # Connecting to PostgreSQL
    load_dotenv()
    conn = psycopg2.connect( user = os.getenv('DB_USER'),
    password = os.getenv('DB_PASSWORD'),
    host = os.getenv('DB_HOST'),
    port = int(os.getenv('DB_PORT')),
    dbname  = os.getenv('DB_NAME'))
    
    cur = conn.cursor()
    

    # Fetching earthquake data
    url = f"https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime={start_date.strftime('%Y-%m-%d')}&endtime={end_date.strftime('%Y-%m-%d')}"
    response = requests.get(url)
    # Checking response status
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data. Status code: {response.status_code}")
    
    data = response.json()
    timestamp = data['features'][0]['properties']['time'] / 1000
    date = datetime.datetime.fromtimestamp(timestamp, datetime.timezone.utc).date()
    #count = len(data['features'])
    count = data['metadata']['count']

    # Inserting data into the database
    sql_query = f'''INSERT INTO {os.getenv('DB_TABLE')} (date, earthquakes) VALUES (%s, %s)'''
    cur.execute(sql_query, (start_date, count))
    conn.commit()

    print("Data inserted successfully.")
    
except psycopg2.Error as e:
    print("Error occurred during database operation:", e)
    
except requests.RequestException as e:
    print("Error occurred during API request:", e)
    
except Exception as e:
    print("An unexpected error occurred:", e)

finally:
    # Closing database connection
    if cur is not None:
        cur.close()
    if conn is not None:
        conn.close()

