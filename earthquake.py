
import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
from datetime import datetime   #added

st.title('Global Earthquake Activity Map')
# Date input

current_year = datetime.now().year #added
start_date = st.date_input('Start date', min_value=datetime(2020, 1, 1), max_value=datetime(current_year, 12, 31))
end_date = st.date_input('End date', min_value=datetime(2020, 1, 1), max_value=datetime(current_year, 12, 31))

if (end_date - start_date).days > 50: #added
    st.error('The date range must not exceed 50 days.')

# API call
def get_data(start_date, end_date):
    url = f"https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime={start_date}&endtime={end_date}"
    response = requests.get(url)
    return response.json()

# Function to extract places and coordinates
def extract_places(data):
    places = []
    for item in data['features']:
        place = item['properties']['place']
        longitude, latitude = item['geometry']['coordinates'][0:2]
        places.append({'place': place, 'latitude': latitude, 'longitude': longitude})
    return places

# Display data on a map
if st.button('Show Map'):
    if start_date > end_date:
        st.error('Error: Start date must be before the end date.')
else:
    data = get_data(start_date, end_date)
    places = extract_places(data)

    # Convert to DataFrame for Streamlit map
    df = pd.DataFrame(places)
    st.map(df)

# Set up database connection
db_user = st.secrets['DB_USER']
db_password = st.secrets['DB_PASSWORD']
db_host = st.secrets['DB_HOST']
db_name = st.secrets['DB_NAME']
db_table = st.secrets['DB_TABLE']
db_port = st.secrets['DB_PORT']


st.title('Trends in Earthquake Frequency')

# Function to load data from the database
def load_data():
    engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')
    query = f'SELECT * FROM {db_table}' 
    data = pd.read_sql(query, engine)
    return data

# Load the data
data = load_data()

# Plot the data 
if not data.empty:
 
    fig, ax = plt.subplots()
    ax.plot(data['date'], data['earthquakes'], marker='o')
    ax.set_title('Number of Earthquakes Over Time')
    ax.set_xlabel('Date')
    ax.set_ylabel('Number of Earthquakes')
    ax.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Display the plot in Streamlit
    st.pyplot(fig)
else:
    st.write('No data available to display.')
# Button to refresh data
if st.button('Refresh Data'):
    st.experimental_rerun()  


