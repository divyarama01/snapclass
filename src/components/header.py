import streamlit as st

def header_home():

    logo_url = "https://i.ibb.co/YTYGn5qV/logo.png"

    st.markdown(f"""
    <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; margin-bottom:30px; margin-top:30px">
        <img src="{logo_url}" style="width:400px; height:200px; object-fit:contain;">
        <h1 style="text-align:center; color:#E0E3FF;">
            SNAP<br/>CLASS
        </h1>
    </div>
    """, unsafe_allow_html=True)