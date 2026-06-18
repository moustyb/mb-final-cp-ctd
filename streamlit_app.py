import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# 1. Premium Page Configuration
st.set_page_config(
    page_title="Netflix Content Intelligence",
    layout="wide",
    page_icon="🎬"
)

# Advanced CSS to force a flawless Netflix Dark Theme (FIXED HTML ARGUMENT)
st.markdown("""
    <style>
    .stApp { background-color: #141414; color: #FFFFFF; }
    h1, h2, h3, h4 { color: #FFFFFF !important; font-weight: 700; }
    div[data-testid="stMetric"] { 
        background-color: #1F1F1F; 
        padding: 20px; 
        border-radius: 10px; 
        border: 1px solid #333333; 
    }
    div[data-testid="stMetricValue"] { color: #E50914 !important; font-weight: bold; }
    div[data-testid="stMetricLabel"] { color: #AAAAAA !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎬 Netflix Global Content Analytics")
st.markdown("A premium executive dashboard monitoring live streaming catalog metrics.")
st.markdown("---")

# 2. Cached Database Connection Engine
@st.cache_data
def fetch_database_records():
    try:
        conn = sqlite3.connect("data/netflix_analysis.db")
        df = pd.read_sql_query("SELECT * FROM netflix_titles", conn)
        conn.close()
        df['first_country'] = df['country'].apply(lambda x: x.split(',')[0].strip() if pd.notnull(x) else "Unknown")
        return df
    except Exception as e:
        st.error(f"Database Error: {e}")
        return pd.DataFrame()

df = fetch_database_records()

if not df.empty:
    # 3. Dynamic Sidebar Navigation & Filters
    st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/0/08/Netflix_2015_logo.svg", width=160)
    st.sidebar.markdown("### **Filter Engine**")
    
    selected_type = st.sidebar.selectbox("Catalog Type", ["All Dimensions"] + list(df['type'].unique()))
    
    min_y, max_y = int(df['release_year'].min()), int(df['release_year'].max())
    selected_years = st.sidebar.slider("Release Window", min_y, max_y, (2012, max_y))
    
    # Apply Filtering Logic
    filtered_df = df[(df['release_year'] >= selected_years[0]) & (df['release_year'] <= selected_years[1])]
    if selected_type != "All Dimensions":
        filtered_df = filtered_df[filtered_df['type'] == selected_type]

    # 4. Modern KPI Summary Scorecards
    m1, m2, m3 = st.columns(3)
    with m1: st.metric("Total Catalog Footprint", f"{len(filtered_df):,}")
    with m2: st.metric("Feature Films", f"{len(filtered_df[filtered_df['type']=='Movie']):,}")
    with m3: st.metric("TV/Docu-Series", f"{len(filtered_df[filtered_df['type']=='TV Show']):,}")

    st.markdown("<br>", unsafe_allow_html=True)

    # 5. High-Impact Charts Visual Grid
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("#### 📊 Top 10 High-Volume Content Genres")
        top_genres = filtered_df['listed_in'].str.split(', ').explode().value_counts().head(10).reset_index()
        fig_gen = px.bar(top_genres, x='count', y='listed_in', orientation='h', 
                         color='count', color_continuous_scale=['#330000', '#B20710', '#E50914'])
        fig_gen.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font_color='white', showlegend=False, coloraxis_showscale=False,
            yaxis={'categoryorder':'total ascending'}, margin=dict(l=10, r=10, t=10, b=10)
        )
        st.plotly_chart(fig_gen, use_container_width=True)

    with col_right:
        st.markdown("#### 🌎 Global Distribution Share (Top 10 Nations)")
        top_countries = filtered_df[filtered_df['first_country'] != 'Unknown']['first_country'].value_counts().head(10).reset_index()
        fig_country = px.pie(top_countries, values='count', names='first_country', hole=0.6,
                             color_discrete_sequence=['#E50914', '#B20710', '#7F0000', '#550000', '#222222'])
        fig_country.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font_color='white', margin=dict(l=10, r=10, t=10, b=10)
        )
        st.plotly_chart(fig_country, use_container_width=True)

    # 6. Streamline Performance Timeline Chart
    st.markdown("#### 📈 Network Production Acceleration Vector")
    timeline = filtered_df.groupby(['release_year', 'type']).size().reset_index(name='count')
    fig_time = px.line(timeline, x='release_year', y='count', color='type', 
                       color_discrete_map={'Movie': '#E50914', 'TV Show': '#FFFFFF'})
    fig_time.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font_color='white', xaxis_showgrid=False, yaxis_showgrid=True, yaxis_gridcolor='#222222'
    )
    st.plotly_chart(fig_time, use_container_width=True)

    # 7. Relational Database Row Explorer
    with st.expander("🔍 Audit Live Relational Database Records"):
        st.dataframe(filtered_df[['show_id', 'type', 'title', 'release_year', 'first_country', 'rating']], use_container_width=True)
else:
    st.warning("No data found. Ensure your database pipeline script has executed successfully.")
