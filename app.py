import streamlit as st
import pandas as pd
import plotly.express as px

# Load and preprocess data
# Ensure you've replaced the path with the correct path to your dataset
df = pd.read_csv('events v2.csv')

# Preprocess if necessary (e.g., parsing dates)
# This example assumes the DataFrame is ready for visualization

# Streamlit app layout
st.title('Seattle Events Dashboard')

# Widget for category filtering - displays all event categories allowing the user to select one
category = st.selectbox('Select Event Category', df['Type'].unique())

# Filtering the dataset based on the selected category
# This filter is applied to show detailed data or other visualizations specific to the selected category
filtered_data = df[df['Type'] == category]

# Plotly chart for the overall distribution of event categories (ignoring the category filter to show all categories)
# We first calculate the count of each category, reset the index to make it a DataFrame, and then plot
category_counts = df['Type'].value_counts().reset_index()
category_counts.columns = ['Type', 'Count']  # Renaming columns to use in Plotly Express

fig = px.bar(category_counts, x='Type', y='Count', title='Distribution of Event Categories')

# Display the Plotly chart in Streamlit
st.plotly_chart(fig)

# Optional: Display filtered data in a table to provide more details about the selected category
st.subheader(f"Events in the '{category}' category")
st.dataframe(filtered_data)
