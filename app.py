import streamlit as st
import pandas as pd
import altair as alt
import folium
from streamlit_folium import st_folium
from datetime import datetime

csv_file_path = 'enhanced_events.csv'

try:
    df = pd.read_csv(csv_file_path)
    
    df['Date'] = pd.to_datetime(df['Date'].str.split(' | ').str[0], errors='coerce')
    df['Month'] = df['Date'].dt.month
    df['DayOfWeek'] = df['Date'].dt.day_name()
    
    st.title("Seattle Events Dashboard")
    
    category = st.sidebar.selectbox('Category', options=['All'] + list(df['Type'].unique()))
    date_range = st.sidebar.date_input("Date range", [])
    location = st.sidebar.selectbox('Location', options=['All'] + list(df['Location'].unique()))
    
    filtered_df = df
    if category != 'All':
        filtered_df = filtered_df[filtered_df['Type'] == category]
    if date_range:
        start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        filtered_df = filtered_df[(filtered_df['Date'] >= start_date) & (filtered_df['Date'] <= end_date)]
    if location != 'All':
        filtered_df = filtered_df[filtered_df['Location'] == location]

    st.header("Most Common Event Categories")
    category_counts = df['Type'].value_counts().reset_index()
    category_counts.columns = ['Category', 'Count']
    fig1 = alt.Chart(category_counts).mark_bar().encode(
        x=alt.X('Category:N', sort='-y'),
        y='Count:Q'
    )
    st.altair_chart(fig1, use_container_width=True)
    
    st.header("Events Count by Month")
    month_counts = df['Month'].value_counts().reset_index()
    month_counts.columns = ['Month', 'Count']
    fig2 = alt.Chart(month_counts).mark_bar().encode(
        x=alt.X('Month:N', sort=None),
        y='Count:Q'
    )
    st.altair_chart(fig2, use_container_width=True)
    
    st.header("Events Count by Day of the Week")
    day_counts = df['DayOfWeek'].value_counts().reset_index()
    day_counts.columns = ['Day', 'Count']
    fig3 = alt.Chart(day_counts).mark_bar().encode(
        x=alt.X('Day:N', sort=None),
        y='Count:Q'
    )
    st.altair_chart(fig3, use_container_width=True)

    st.header("Events Locations on Map")
    map_df = filtered_df.dropna(subset=['Latitude', 'Longitude'])
    m = folium.Map(location=[47.6062, -122.3321], zoom_start=10)
    for idx, row in map_df.iterrows():
        folium.Marker(
            [float(row['Latitude']), float(row['Longitude'])], 
            popup=row['Name']
        ).add_to(m)
    st_folium(m, width=720, height=600)
    
    st.subheader("Filtered Events Data")
    st.write(filtered_df)
    
except FileNotFoundError:
    st.error("CSV file not found. Please ensure the file path is correct.")
