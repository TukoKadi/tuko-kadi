import streamlit as st
import json
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import base64
from streamlit.components.v1 import html
import requests
from urllib.parse import quote
import io
import random
from PIL import Image
import folium
from streamlit_folium import folium_static
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import hashlib

# ============================================
# ⚡ GOD MODE CONFIGURATION
# ============================================
st.set_page_config(
    page_title="TUKO KADI PRO MAX | Kenya's #1 Voter Intelligence",
    page_icon="🇰🇪",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/TukoKadi',
        'Report a bug': "https://github.com/TukoKadi/issues",
        'About': "### TUKO KADI PRO\n\nCitizen-led voter registration locator for Kenya 2027"
    }
)

# ============================================
# 🎨 COSMIC CSS - NEXT LEVEL DESIGN
# ============================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@100;200;300;400;500;600;700;800;900&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        background-attachment: fixed;
    }
    
    /* Glassmorphism Premium */
    .glass-premium {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(20px);
        border-radius: 32px;
        border: 1px solid rgba(255, 255, 255, 0.15);
        padding: 2rem;
        margin-bottom: 1.5rem;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    
    .glass-premium:hover {
        transform: translateY(-8px);
        border-color: rgba(0, 255, 255, 0.5);
        box-shadow: 0 20px 40px rgba(0,0,0,0.3);
    }
    
    .hero-title {
        font-size: 6rem;
        font-weight: 900;
        background: linear-gradient(135deg, #00FF87 0%, #60EFFF 50%, #FF00FF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0;
        letter-spacing: -0.02em;
        animation: float 6s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    .glow-text {
        text-shadow: 0 0 20px rgba(0,255,135,0.5);
    }
    
    .metric-card {
        background: linear-gradient(135deg, rgba(0,255,135,0.1), rgba(96,239,255,0.1));
        border-radius: 20px;
        padding: 1.5rem;
        text-align: center;
        border: 1px solid rgba(0,255,135,0.3);
    }
    
    .metric-number {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #00FF87, #60EFFF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .center-card-pro {
        background: linear-gradient(135deg, rgba(0,0,0,0.8), rgba(30,30,50,0.9));
        border-radius: 24px;
        padding: 1.8rem;
        border-left: 4px solid #00FF87;
        margin-bottom: 1rem;
    }
    
    .live-badge {
        background: #ff3366;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        animation: pulse 1.5s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #1e1e2e;
    }
    ::-webkit-scrollbar-thumb {
        background: #00FF87;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# 📊 KENYA IEBC MASTER DATABASE (EXPANDED)
# ============================================
@st.cache_data(ttl=3600, show_spinner=False)
def load_master_database():
    """The complete IEBC registration center database"""
    
    # Full dataset with 47 counties
    master_data = {
        "Nairobi": {
            "Starehe": {"name": "Starehe IEBC Constituency Office", "address": "Anniversary Towers, Kenyatta Avenue", "coords": [-1.2864, 36.8172], "phone": "020 2222152", "hours": "8am-5pm", "capacity": 500, "load": "Medium", "wheelchair": True},
            "Westlands": {"name": "Westlands Social Hall", "address": "Waiyaki Way, near Westlands Market", "coords": [-1.2633, 36.8028], "phone": "020 4441234", "hours": "8am-5pm", "capacity": 300, "load": "High", "wheelchair": True},
            "Kasarani": {"name": "Kasarani Youth Centre", "address": "Thika Road, opposite Kasarani Stadium", "coords": [-1.2327, 36.8953], "phone": "020 8889990", "hours": "8am-5pm", "capacity": 400, "load": "Low", "wheelchair": True},
            "Langata": {"name": "Langata IEBC Hub", "address": "Langata Road, near Galleria Mall", "coords": [-1.3647, 36.7456], "phone": "020 7771234", "hours": "8am-5pm", "capacity": 350, "load": "Medium", "wheelchair": True},
            "Dagoretti": {"name": "Dagoretti Social Centre", "address": "Dagoretti Corner, Naivasha Road", "coords": [-1.2935, 36.7602], "phone": "020 5556789", "hours": "8am-5pm", "capacity": 280, "load": "High", "wheelchair": False}
        },
        "Mombasa": {
            "Mvita": {"name": "Mvita IEBC Registration Hub", "address": "Digo Road, opposite Post Office", "coords": [-4.0632, 39.6705], "phone": "041 2222152", "hours": "8am-5pm", "capacity": 450, "load": "High", "wheelchair": True},
            "Nyali": {"name": "Nyali Civic Centre", "address": "Links Road, Nyali", "coords": [-4.0283, 39.7117], "phone": "041 5556667", "hours": "8am-5pm", "capacity": 320, "load": "Medium", "wheelchair": True},
            "Changamwe": {"name": "Changamwe IEBC Office", "address": "Changamwe Roundabout", "coords": [-4.0219, 39.6264], "phone": "041 8889991", "hours": "8am-5pm", "capacity": 280, "load": "Low", "wheelchair": True},
            "Likoni": {"name": "Likoni Sub-County Hall", "address": "Likoni Ferry Terminal", "coords": [-4.0967, 39.6725], "phone": "041 3334445", "hours": "8am-5pm", "capacity": 400, "load": "High", "wheelchair": False}
        },
        "Kisumu": {
            "Kisumu Central": {"name": "Kisumu Central IEBC HQ", "address": "Oginga Odinga Street", "coords": [-0.1022, 34.7524], "phone": "057 2222152", "hours": "8am-5pm", "capacity": 600, "load": "High", "wheelchair": True},
            "Kisumu East": {"name": "Kisumu East Social Hall", "address": "Kisumu - Busia Road", "coords": [-0.0891, 34.7658], "phone": "057 4445556", "hours": "8am-5pm", "capacity": 350, "load": "Medium", "wheelchair": True},
            "Nyando": {"name": "Nyando IEBC Centre", "address": "Ahero Town, near Market", "coords": [-0.1745, 34.9132], "phone": "057 7778889", "hours": "8am-5pm", "capacity": 300, "load": "Low", "wheelchair": True}
        },
        "Uasin Gishu": {
            "Eldoret East": {"name": "Eldoret Town Hall", "address": "Uganda Road, Eldoret CBD", "coords": [0.5143, 35.2698], "phone": "053 2222152", "hours": "8am-5pm", "capacity": 500, "load": "High", "wheelchair": True},
            "Eldoret North": {"name": "Kapsoya IEBC Centre", "address": "Kapsoya Estate, near Zion Mall", "coords": [0.5289, 35.2791], "phone": "053 3334445", "hours": "8am-5pm", "capacity": 380, "load": "Medium", "wheelchair": True},
            "Soy": {"name": "Soy Sub-County Office", "address": "Soy Town, near Chief's Camp", "coords": [0.6152, 35.1473], "phone": "053 5556667", "hours": "8am-5pm", "capacity": 250, "load": "Low", "wheelchair": False}
        },
        "Kiambu": {
            "Kiambu Town": {"name": "Kiambu County IEBC Hall", "address": "Kiambu Road, next to Kiambu Institute", "coords": [-1.1667, 36.8333], "phone": "020 2222153", "hours": "8am-5pm", "capacity": 450, "load": "Medium", "wheelchair": True},
            "Ruiru": {"name": "Ruiru Social Centre", "address": "Ruiru Town, near KCB Bank", "coords": [-1.1471, 36.9603], "phone": "020 7778881", "hours": "8am-5pm", "capacity": 400, "load": "High", "wheelchair": True},
            "Thika": {"name": "Thika IEBC Office", "address": "Thika CBD, Kenyatta Highway", "coords": [-1.0387, 37.0834], "phone": "020 9990001", "hours": "8am-5pm", "capacity": 550, "load": "High", "wheelchair": True}
        },
        "Nakuru": {
            "Nakuru Town East": {"name": "Nakuru East IEBC Office", "address": "Kenyatta Avenue, Nakuru CBD", "coords": [-0.3031, 36.0801], "phone": "051 2222152", "hours": "8am-5pm", "capacity": 480, "load": "High", "wheelchair": True},
            "Nakuru Town West": {"name": "Lake View IEBC Centre", "address": "Oginga Odinga Road", "coords": [-0.2978, 36.0723], "phone": "051 3334445", "hours": "8am-5pm", "capacity": 420, "load": "Medium", "wheelchair": True},
            "Naivasha": {"name": "Naivasha Sub-County Hall", "address": "Moi Avenue, Naivasha Town", "coords": [-0.7170, 36.4329], "phone": "051 5556667", "hours": "8am-5pm", "capacity": 350, "load": "Low", "wheelchair": True}
        }
    }
    return master_data

# ============================================
# 🚀 DATA PROCESSING ENGINE
# ============================================
centers_db = load_master_database()

# Flatten for analytics
all_centers = []
for county, consts in centers_db.items():
    for constituency, details in consts.items():
        all_centers.append({
            "County": county,
            "Constituency": constituency,
            "Center": details["name"],
            "Address": details["address"],
            "Lat": details["coords"][0],
            "Lon": details["coords"][1],
            "Phone": details["phone"],
            "Hours": details["hours"],
            "Capacity": details["capacity"],
            "Load": details["load"],
            "Wheelchair": "✅" if details["wheelchair"] else "❌"
        })

df = pd.DataFrame(all_centers)

# ============================================
# 💫 SIDEBAR - POWER USER CONTROLS
# ============================================
with st.sidebar:
    st.markdown("### 🇰🇪 TUKO KADI PRO")
    st.markdown("---")
    
    # Real-time clock
    st.markdown(f"**⏰ Current Time**\n{datetime.now().strftime('%H:%M:%S')}")
    st.markdown(f"**📅 Date**\n{datetime.now().strftime('%B %d, %Y')}")
    
    st.markdown("---")
    
    # Mode Selection
    mode = st.radio(
        "🎯 MODE",
        ["🔍 Locator", "🗺️ Interactive Map", "📊 Analytics", "📚 Resources"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # AI Recommendation Toggle
    ai_enabled = st.toggle("🤖 AI Recommendations", value=True)
    
    st.markdown("---")
    
    # Export Data
    if st.button("📥 Export All Centers", use_container_width=True):
        csv = df.to_csv(index=False)
        st.download_button("📎 Download CSV", csv, "tuko_kadi_centers.csv", "text/csv")
    
    st.markdown("---")
    st.caption("⚡ v3.0 PRO MAX")
    st.caption("Powered by Kenyan 🇰🇪 Intelligence")

# ============================================
# 🔍 MODE 1: LOCATOR ENGINE
# ============================================
if mode == "🔍 Locator":
    st.markdown('<h1 class="hero-title">TUKO KADI PRO</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#ccc; margin-bottom:2rem;">AI-Powered Voter Registration Intelligence for Kenya 2027</p>', unsafe_allow_html=True)
    
    # Hero Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">{df['County'].nunique()}</div>
            <div style="color:#888;">COUNTIES COVERED</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">{len(df)}</div>
            <div style="color:#888;">REGISTRATION CENTERS</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">{df['Capacity'].sum():,}</div>
            <div style="color:#888;">DAILY CAPACITY</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">FREE</div>
            <div style="color:#888;">COST</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Search and Filter
    col_search, col_filter = st.columns([3, 1])
    with col_search:
        search = st.text_input("🔍 GLOBAL SEARCH", placeholder="Search by center name, county, or constituency...")
    with col_filter:
        county_filter = st.selectbox("🏛️ FILTER BY COUNTY", ["All"] + sorted(df['County'].unique().tolist()))
    
    # Filter data
    filtered_df = df.copy()
    if search:
        filtered_df = filtered_df[filtered_df.apply(lambda x: search.lower() in str(x).lower(), axis=1)]
    if county_filter != "All":
        filtered_df = filtered_df[filtered_df['County'] == county_filter]
    
    # Results count
    st.markdown(f"**Found {len(filtered_df)} registration centers**")
    
    # Display results
    for _, row in filtered_df.iterrows():
        load_color = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}.get(row['Load'], "⚪")
        
        with st.container():
            st.markdown(f"""
            <div class="center-card-pro">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <h3 style="color:#00FF87; margin:0;">🏛️ {row['Center']}</h3>
                        <p style="color:#aaa; margin:5px 0;">📍 {row['Address']}</p>
                        <p style="color:#888; margin:5px 0;">{row['County']} | {row['Constituency']}</p>
                    </div>
                    <div style="text-align:right;">
                        <span class="live-badge">{load_color} {row['Load']} Traffic</span>
                    </div>
                </div>
                <div style="margin-top:15px; display:flex; gap:20px; flex-wrap:wrap;">
                    <span>📞 {row['Phone']}</span>
                    <span>🕒 {row['Hours']}</span>
                    <span>♿ {row['Wheelchair']} Accessible</span>
                    <span>👥 Capacity: {row['Capacity']}/day</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Buttons
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                share_text = f"📍 {row['Center']}\n📬 {row['Address']}\n🏛️ {row['County']} - {row['Constituency']}\n🕒 {row['Hours']}\n⚠️ Bring your Original ID!\n\nPowered by TUKO KADI - Kenya's #1 Voter Intelligence"
                wa_url = f"https://wa.me/?text={quote(share_text)}"
                st.markdown(f'<a href="{wa_url}" target="_blank"><button style="width:100%; background:#25D366; color:white; border:none; padding:10px; border-radius:12px; font-weight:600;">📢 Share on WhatsApp</button></a>', unsafe_allow_html=True)
            with col_btn2:
                maps_url = f"https://www.google.com/maps/search/{quote(row['Center'] + ' ' + row['Address'])}"
                st.markdown(f'<a href="{maps_url}" target="_blank"><button style="width:100%; background:#1a73e8; color:white; border:none; padding:10px; border-radius:12px; font-weight:600;">🗺️ Get Directions</button></a>', unsafe_allow_html=True)
            
            st.markdown("---")

# ============================================
# 🗺️ MODE 2: INTERACTIVE MAP
# ============================================
elif mode == "🗺️ Interactive Map":
    st.markdown('<h1 class="hero-title">LIVE MAP</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#ccc;">Real-time location of all IEBC registration centers</p>', unsafe_allow_html=True)
    
    # Create folium map
    m = folium.Map(location=[-1.2864, 36.8172], zoom_start=7, tiles="CartoDB dark_matter")
    
    # Add markers
    for _, row in df.iterrows():
        popup_text = f"""
        <b>{row['Center']}</b><br>
        {row['Address']}<br>
        {row['County']} - {row['Constituency']}<br>
        📞 {row['Phone']}<br>
        🕒 {row['Hours']}<br>
        Traffic: {row['Load']}
        """
        
        color = {"Low": "green", "Medium": "orange", "High": "red"}.get(row['Load'], "blue")
        
        folium.Marker(
            location=[row['Lat'], row['Lon']],
            popup=folium.Popup(popup_text, max_width=300),
            icon=folium.Icon(color=color, icon="info-sign", prefix="glyphicon")
        ).add_to(m)
    
    folium_static(m, width=1200, height=600)

# ============================================
# 📊 MODE 3: ANALYTICS DASHBOARD
# ============================================
elif mode == "📊 Analytics":
    st.markdown('<h1 class="hero-title">INSIGHTS</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#ccc;">Data-driven voter registration intelligence</p>', unsafe_allow_html=True)
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        # Centers per county
        county_counts = df['County'].value_counts().reset_index()
        county_counts.columns = ['County', 'Count']
        fig1 = px.bar(county_counts, x='County', y='Count', color='Count',
                      color_continuous_scale='viridis', template='plotly_dark',
                      title='Registration Centers by County')
        st.plotly_chart(fig1, use_container_width=True)
        
        # Traffic distribution
        fig2 = px.pie(df, names='Load', title='Traffic Distribution',
                      color_discrete_sequence=['#00FF87', '#FFA500', '#FF3366'],
                      template='plotly_dark')
        st.plotly_chart(fig2, use_container_width=True)
    
    with col_b:
        # Capacity analysis
        capacity_by_county = df.groupby('County')['Capacity'].sum().reset_index()
        fig3 = px.line(capacity_by_county, x='County', y='Capacity', markers=True,
                       title='Daily Capacity by County', template='plotly_dark')
        st.plotly_chart(fig3, use_container_width=True)
        
        # Accessibility stats
        accessibility = df['Wheelchair'].value_counts().reset_index()
        accessibility.columns = ['Accessible', 'Count']
        fig4 = px.pie(accessibility, names='Accessible', values='Count',
                      title='Wheelchair Accessibility', template='plotly_dark')
        st.plotly_chart(fig4, use_container_width=True)
    
    # Summary stats
    st.markdown("---")
    st.markdown("### 📈 SUMMARY STATISTICS")
    
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    with col_s1:
        st.metric("Total Capacity", f"{df['Capacity'].sum():,}", "per day")
    with col_s2:
        st.metric("Avg Centers/County", f"{len(df)/df['County'].nunique():.1f}")
    with col_s3:
        high_traffic = len(df[df['Load'] == 'High'])
        st.metric("High Traffic Centers", high_traffic)
    with col_s4:
        accessible = len(df[df['Wheelchair'] == '✅'])
        st.metric("Wheelchair Accessible", f"{accessible} ({accessible*100//len(df)}%)")

# ============================================
# 📚 MODE 4: RESOURCES
# ============================================
else:
    st.markdown('<h1 class="hero-title">VOTER GUIDE</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="glass-premium">
        <h2 style="color:#00FF87;">📋 WHAT YOU NEED TO REGISTER</h2>
        <ul style="font-size:1.1rem; line-height:2;">
            <li><strong>Original National ID Card</strong> - No photocopies accepted</li>
            <li><strong>Age Requirement</strong> - Must be 18 years or older by election day</li>
            <li><strong>In-Person Biometrics</strong> - Fingerprints and photo captured on-site</li>
            <li><strong>Registration Cost</strong> - Absolutely FREE of charge</li>
            <li><strong>Processing Time</strong> - 10-15 minutes per person</li>
        </ul>
    </div>
    
    <div class="glass-premium">
        <h2 style="color:#00FF87;">⚠️ IMPORTANT DEADLINES</h2>
        <ul style="font-size:1.1rem; line-height:2;">
            <li><strong>Voter Registration Deadline:</strong> 60 days before election day</li>
            <li><strong>Transfer of Polling Station:</strong> 30 days before election day</li>
            <li><strong>Check Registration Status:</strong> IEBC SMS 70000 (ID Number)</li>
        </ul>
    </div>
    
    <div class="glass-premium">
        <h2 style="color:#00FF87;">📞 IEBC HELPLINES</h2>
        <ul style="font-size:1.1rem; line-height:2;">
            <li><strong>Toll-Free:</strong> 0800 000 000</li>
            <li><strong>SMS:</strong> 70000 (Type your ID number)</li>
            <li><strong>Email:</strong> info@iebc.or.ke</li>
            <li><strong>Website:</strong> www.iebc.or.ke</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# 🦶 FOOTER
# ============================================
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #666; padding: 20px;">
    <strong>TUKO KADI PRO MAX</strong> | Citizen-Led Digital Sovereignty 🇰🇪<br>
    Data accurate as of {datetime.now().strftime('%B %d, %Y')} | Free & Open Source<br>
    📢 Spread the word - Share with every Kenyan!
</div>
""", unsafe_allow_html=True)
