import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

# Need to add module section where the latest data is pulled into the database

# Set page config
st.set_page_config(
    page_title="Film Collection Dashboard",
    page_icon="🎬",
    layout="wide"
)

def local_css(file_name):
    """
    Load and apply a local CSS file
    """
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css("styles/style.css")

# Page title
st.title("🎬 My Film Collection Dashboard")

# Load the film collection data
@st.cache_data
def load_data():
    """
    Load the film collection data from a CSV file and convert percentage scores
    """
    data = pd.read_csv('bluray_dvd_collection - Collection.csv')
    df = pd.DataFrame(data)
    # Convert the percentage scores
    df['rt_critic_score'] = df['rt_critic_score']*100
    df['rt_audience_score'] = df['rt_audience_score']*100
    return df

df = load_data()

# Calculate KPIs
total_films = len(df)
avg_rating = df['avg_critical_rating'].mean()
avg_rt_critic = df['rt_critic_score'].mean()
most_common_genre = df['genre'].value_counts().index[0]
most_common_director = df['director'].value_counts().index[0]
highest_rated = df.loc[df['avg_critical_rating'].idxmax()]['film_name']
newest_film = df[df['year'] == df['year'].max()]['film_name'].tolist()
oldest_film = df[df['year'] == df['year'].min()]['film_name'].tolist()

# Display KPI metrics in cards
st.markdown('<div class="section-header"><h2>Collection Stats</h2></div>', unsafe_allow_html=True)

# First row of metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Films", f"{total_films}")
    st.metric("Most Common Genre", f"{most_common_genre}")
with col2:
    st.metric("Average Critical Rating", f"{avg_rating:.1f}/10")
    st.metric("Average Rotten Tomatoes Critic Score", f"{avg_rt_critic:.1f}%")
with col3:
    st.metric("Highest Rated Film", f"{highest_rated}")
    st.metric("Most Common Director", f"{most_common_director}")
with col4:
    st.metric("Newest Film ("+str(df['year'].max())+")", f"{newest_film[0]}")
    st.metric("Oldest Film ("+str(df['year'].min())+")", f"{oldest_film[0]}")

# Add Choropleth Map for Countries Represented
country_counts = df['country'].value_counts().reset_index()
country_counts.columns = ['Country', 'Count']

st.markdown('<div class="section-header"><h2>Film Collection Map</h2></div>', unsafe_allow_html=True)

total_countries = 195
# Create metrics for the map section
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Countries Represented", f"{len(country_counts)}")
with col2:
    st.metric("Most Common Country", f"{country_counts['Country'].iloc[0]} ({country_counts['Count'].iloc[0]})")
with col3:
    st.metric("Percentage of Countries", f"{(len(country_counts)/total_countries)*100:.1f}%")

# Create the choropleth map
fig = px.choropleth(
    country_counts,
    locations='Country',
    locationmode='country names',
    hover_name='Country',
)
fig.update_layout(
    geo=dict(
        showframe=False,
        showcoastlines=True,
        projection_type='equirectangular'
    ),
    height=500
)
st.plotly_chart(fig, use_container_width=True)

# Two columns for charts plus header
st.markdown('<div class="section-header"><h2>Film Collection Analysis</h2></div>', unsafe_allow_html=True)
col_left, col_right = st.columns(2)

# Left column charts
with col_left:
     # Chart 1: Films by Year
    st.markdown('<div class="subheader">Films by Release Year</div>', unsafe_allow_html=True)
    year_counts = df['year'].value_counts().sort_index().reset_index()
    year_counts.columns = ['Year', 'Count']
    fig = px.line(year_counts, x='Year', y='Count', markers=False)
    fig.update_layout(height=350)
    fig.update_layout(xaxis_title="", yaxis_title="")
    st.plotly_chart(fig, use_container_width=True)

    # Chart 2: Genre Distribution
    st.markdown('<div class="subheader">Genre Distribution</div>', unsafe_allow_html=True)
    genre_counts = df['genre'].value_counts().reset_index()
    genre_counts.columns = ['Genre', 'Count']
    genre_counts = genre_counts.sort_values('Count', ascending=True)
    fig = px.bar(genre_counts, x='Count', y='Genre', orientation='h',
                 labels={'value':'Count', 'Category':'Genre'})
    fig.update_layout(height=350)
    fig.update_traces(marker=dict(color='#44546A'),
                  text=genre_counts['Count'])
    fig.update_layout(xaxis_title="", yaxis_title="")
    st.plotly_chart(fig, use_container_width=True)
    
    # Chart 3: Media Types Distribution
    st.markdown('<div class="subheader">Media Type Distribution</div>', unsafe_allow_html=True)
    media_counts = df['media_type'].value_counts().reset_index()
    media_counts.columns = ['Media Type', 'Count']
    custom_colors = {'DVD': '#B3B3B3', 'Blu-ray': '#0095D5', '4k Blu-ray': '#000000'}
    fig = px.pie(media_counts, values='Count', names='Media Type', hole=0.6, color='Media Type', color_discrete_map=custom_colors)
    fig.update_layout(height=350)
    fig.update_layout(xaxis_title="", yaxis_title="")
    fig.update_layout(legend=dict(  # Edit the legend by passing through a dictionary
        title="",  # Title for the legend
        orientation="h",  # Horizontal layout
        x=0.5,  # X position of the legend (centered)
        xanchor="center",  # Anchor the legend to the center
        y=1.15,  # Y position of the legend (move above the plot)
        yanchor="top",  # Anchor the legend to the top of its bounding box
        bgcolor="rgba(255, 255, 255, 0.5)",  # Background color with transparency
        ),)
    st.plotly_chart(fig, use_container_width=True)
    
    # Chart 4: histogram of average critical ratings
    st.markdown('<div class="subheader">Distribution of Critical Ratings</div>', unsafe_allow_html=True)
    fig = px.histogram(df, x='avg_critical_rating', 
                   nbins=30,)
    fig.update_traces(marker=dict(color='#44546A'))
    fig.update_layout(xaxis_title="Average Critical Rating", yaxis_title="Number of Films")
    st.plotly_chart(fig, use_container_width=True)

# Right column charts
with col_right:
    # Chart 1: IMDb vs RT Critics Score Comparison
    st.markdown('<div class="subheader">Rotten Tomatoes Audience Score vs. Critic Score</div>', unsafe_allow_html=True)
    fig = px.scatter(df,
                 x='rt_audience_score',
                 y='rt_critic_score',
                 hover_data=['rt_audience_score', 'rt_critic_score', 'film_name'])
    fig.update_traces(marker=dict(color='#FF0000',
                                opacity=0.5,
                                size=8,
                                line=dict(width=1,
                                color='DarkSlateGrey')))  # Change marker colour to RT red

    # Add lines to divide the quadrants (x=0 and y=0)
    fig.add_hline(y=60, line=dict(color='black', dash='dot'))  # Horizontal line
    fig.add_vline(x=60, line=dict(color='black', dash='dot'))  # Vertical line

    # Add quadrant labels using annotations
    fig.update_layout(
        annotations=[
            dict(x=0.5, y=64, text="Liked by critics, disliked by audiences", showarrow=False, font=dict(size=10, color="black")),
            dict(x=-0.5, y=56, text="Disliked by both", showarrow=False, font=dict(size=10, color="black")),
            dict(x=96, y=64, text="Liked by both", showarrow=False, font=dict(size=10, color="black")),
            dict(x=96, y=56, text="Liked by audiences,\ndisliked by critics", showarrow=False, font=dict(size=10, color="black"))
        ]
    )
    fig.update_layout(
        xaxis_title="Audience Score (%)", 
        yaxis_title="Critic Score (%)",
        plot_bgcolor='White',
        font=dict(size=10, family='Arial'))
    st.plotly_chart(fig, use_container_width=True)
    
    # Chart 3: Director gender ratio
    st.markdown('<div class="subheader">Directors by Gender</div>', unsafe_allow_html=True)
    gender_counts = df['director_gender'].value_counts().reset_index()
    gender_counts.columns = ['Gender', 'Count']
    # Define custom colors for each gender
    custom_colors = {'Male': '#1f77b4', 'Female': '#C90076', 'Non-Binary': '#2ca02c'}
    fig = px.pie(gender_counts, values='Count', names='Gender', hole=0.6, color='Gender', color_discrete_map=custom_colors)
    fig.update_layout(height=350)
    fig.update_layout(legend=dict(  
        title="",  
        orientation="h",  
        x=0.5,  
        xanchor="center",  
        y=1.15, 
        yanchor="top",  
        bgcolor="rgba(255, 255, 255, 0.5)",  
        ))
    st.plotly_chart(fig, use_container_width=True)

    # Chart 4: Top 5 Directors
    st.markdown('<div class="subheader">Top Directors</div>', unsafe_allow_html=True)
    director_counts = df['director'].value_counts().head(5).reset_index()
    director_counts.columns = ['Director', 'Count']
    fig = px.bar(director_counts, x='Count', y='Director', orientation='h')
    fig.update_layout(height=350, yaxis={'categoryorder':'total ascending'})
    fig.update_traces(marker=dict(color='#44546A'),
                  text=director_counts['Count'])
    fig.update_layout(xaxis_title="Total Films", yaxis_title="")
    st.plotly_chart(fig, use_container_width=True)

    # Chart 5: Certificate Distribution Treemap
    st.markdown('<div class="subheader">Certificate Distribution</div>', unsafe_allow_html=True)
    cert_counts = df['certificate'].value_counts().reset_index()
    cert_counts.columns = ['Certificate', 'Count']
    custom_colors = {'U': '#0BC603', 'PG': '#FAAE02', '12': '#FC7D0A', '15': '#F6528F', '18': '#DC0A0B'}
    fig = px.treemap(cert_counts, path=['Certificate'], values='Count', color='Certificate',
                     color_discrete_map=custom_colors)
    fig.update_traces(textinfo="label+value+percent entry")
    fig.update_layout(height=350)
    fig.update_layout(xaxis_title="", yaxis_title="")
    st.plotly_chart(fig, use_container_width=True)

# Add footer
st.markdown("---")
st.markdown("*Film Collection Dashboard built with Streamlit*")
