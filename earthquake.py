
import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
from datetime import datetime, timedelta 
import pydeck as pdk                                            

st.title('Global Earthquake Activity Map')
# Date input
start_date = datetime.now() - timedelta(days=1)
end_date = datetime.now()


# Function to make API call and get data
def get_data(start_date, end_date):
        # Function to make API call and get data
def get_data(start_date, end_date):
    try:
        url = f"https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime={start_date}&endtime={end_date}"
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for 4XX or 5XX status codes
        data = response.json()
        if data is None:
            st.error("No earthquake data available. Please try again later.")
            st.write(":(")  # Show a sad face
        return data
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching earthquake data: {e}")
        st.write(":(")  # Show a sad face
        return None
# Function to extract places, coordinates, and magnitudes
def extract_data(data):
    earthquakes = []
    for feature in data['features']:
        place = feature['properties']['place']
        longitude, latitude = feature['geometry']['coordinates'][0:2]
        magnitude = feature['properties']['mag']
        earthquakes.append({
            'place': place,
            'magnitude': magnitude,
            'longitude': longitude,
            'latitude': latitude
        })
    return earthquakes

# Function to render the map
def render_map(df):
    if df.empty:
        st.pydeck_chart( pdk.Deck(map_style='mapbox://styles/mapbox/outdoors-v11'))
        st.warning('No earthquake data available for the selected date range.')
        return
    # Define the pydeck layer
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position='[longitude, latitude]',
        get_radius='magnitude * 50000',  # Adjust the size based on magnitude
        get_color='[180, 0, 200, 140]',  # RGBA color
        pickable=True,
        auto_highlight=True,
    )
    # Define the initial view state for pydeck
    view_state = pdk.ViewState(
        latitude=df['latitude'].mean(),
        longitude=df['longitude'].mean(),
        zoom=1,
        pitch=0,
    )
    r = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        map_style= 'mapbox://styles/mapbox/outdoors-v11',
        tooltip= {
        "html": "<b>Place:</b> {place} <br/> <b>Magnitude:</b> {magnitude}",
        "style": {
            "backgroundColor": "steelblue",
            "color": "white"
        } }                                      
    )

    # Display the map in Streamlit
    st.pydeck_chart(r)
    
    
start_date = st.date_input('Start date', value=datetime.now() - timedelta(days=1), min_value=datetime(2020, 1, 1),  max_value=datetime.now()) 
end_date = st.date_input('End date', value=datetime.now(), min_value=datetime(2020, 1, 1),  max_value=datetime.now())

if (end_date - start_date).days > 50:
    st.error('The date range must not exceed 50 days.')
    st.pydeck_chart( pdk.Deck(map_style='mapbox://styles/mapbox/outdoors-v11')) #added
if end_date<start_date:
    st.warning("No data available. Please check the dates") 
else:
    # Fetch data and prepare the map
    data = get_data(start_date, end_date)
    earthquakes = extract_data(data)
    df = pd.DataFrame(earthquakes)
    render_map(df)             

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


