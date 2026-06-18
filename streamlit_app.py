import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# 1. Dashboard Page Configuration
st.set_page_config(
    page_title="Netflix Global Analytics",
    layout="wide",
    page_icon="🎬"
)

# Custom Styling for a Dark, Professional Look
st.markdown("""
    <style>
    .main { background-color: #141414; color: white; }
    .stMetric { background-color: #2b2b2b; padding: 15px; border-radius: 10px; }
    </style>
    """, unsafe_allow_stdio=True)

st.title("🎬 Netflix Global Content Analytics")
st.markdown("---")

# 2. Database Connection Engine
@st.cache_data
def fetch_database_records():
    try:
        conn = sqlite3.connect("data/netflix_analysis.db")
        # Querying everything from the table you built
        df = pd.read_sql_query("SELECT * FROM netflix_titles", conn)
        conn.close()
        
        # Logic to clean countries for mapping
        df['first_country'] = df['country'].apply(lambda x: x.split(',')[0].strip() if pd.notnull(x) else "Unknown")
        return df
    except Exception as e:
        st.error(f"Error connecting to database: {e}")
        return pd.DataFrame()

df = fetch_database_records()

if not df.empty:
    # 3. Sidebar Filtering Logic
    st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/0/08/Netflix_2015_logo.svg", width=150)
    st.sidebar.header("Filter Analytics")
    
    # Filter A: Content Type
    m_type = ["All"] + list(df['type'].unique())
    selected_type = st.sidebar.selectbox("Select Content Type", m_type)
    
    # Filter B: Year Range
    min_y, max_y = int(df['release_year'].min()), int(df['release_year'].max())
    selected_years = st.sidebar.slider("Release Year Range", min_y, max_y, (2010, max_y))
    
    # Applying Filters
    filtered_df = df[(df['release_year'] >= selected_years[0]) & (df['release_year'] <= selected_years[1])]
    if selected_type != "All":
        filtered_df = filtered_df[filtered_df['type'] == selected_type]

    # 4. Summary Metrics Row
    m1, m2, m3 = st.columns(3)
    with m1: st.metric("Total Catalog Items", f"{len(filtered_df):,}")
    with m2: st.metric("Movies", f"{len(filtered_df[filtered_df['type']=='Movie']):,}")
    with m3: st.metric("TV Shows", f"{len(filtered_df[filtered_df['type']=='TV Show']):,}")

    # 5. Interactive Charts Section
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("📊 Genre Distribution (Top 10)")
        top_genres = filtered_df['listed_in'].str.split(', ').explode().value_counts().head(10).reset_index()
        fig_gen = px.bar(top_genres, x='count', y='listed_in', orientation='h', 
                         color='count', color_continuous_scale='Reds')
        st.plotly_chart(fig_gen, use_container_width=True)

    with col_right:
        st.subheader("🌎 Top Producing Countries")
        top_countries = filtered_df[filtered_df['first_country'] != 'Unknown']['first_country'].value_counts().head(10).reset_index()
        fig_country = px.pie(top_countries, values='count', names='first_country', hole=0.5,
                             color_discrete_sequence=px.colors.sequential.Reds_r)
        st.plotly_chart(fig_country, use_container_width=True)

    # 6. Trend Timeline
    st.subheader("📈 Content Production Over Time")
    timeline = filtered_df.groupby(['release_year', 'type']).size().reset_index(name='count')
    fig_time = px.line(timeline, x='release_year', y='count', color='type', 
                       color_discrete_map={'Movie': '#E50914', 'TV Show': '#FFFFFF'})
    st.plotly_chart(fig_time, use_container_width=True)

    # 7. Raw Data Explorer
    with st.expander("🔍 View Raw Database Records"):
        st.dataframe(filtered_df[['show_id', 'type', 'title', 'release_year', 'first_country', 'rating']], use_container_width=True)
else:
    st.warning("No data found. Please run your build_db.py script first!")
