import streamlit as st

def header_home():

    logo_url = "https://i.ibb.co/YTYGn5qV/logo.png"

    st.markdown(f"""
    <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; margin-bottom:30px; margin-top:30px">
        <img src="{logo_url}" style="width:400px; height:200px; object-fit:contain;">
        <h1 style="text-align:center; color:#E0E3FF;">
            SNAP CLASS
        </h1>
    </div>
    """, unsafe_allow_html=True)

def header_dashboard():

    logo_url = "https://i.ibb.co/YTYGn5qV/logo.png"

    st.markdown(f"""
    <div style="display:flex; align-items:center; justify-content:center; gap:10px; margin-top:30px">
        <img src="{logo_url}" style="width:400px; height:85px; object-fit:contain;">
        <h2 style="color:#5865F2;font-size:45px;font-weight:bold;white-space:nowrap;margin:0;">SNAP CLASS</h2>
       
    </div>
    """, unsafe_allow_html=True)