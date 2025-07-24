# 📁 multi_page_app.py
import streamlit as st
from streamlit_option_menu import option_menu

# Set page config
st.set_page_config(page_title="TNEA Multi Page App", layout="wide")

# --- SIDEBAR MENU ---
with st.sidebar:
    selected = option_menu(
        menu_title="TNEA Navigation",
        options=["Home", "Create TNEA Choice List", "TNEA Vacancy Seat Matrix"],
        icons=["house", "list-check", "table"],
        menu_icon="cast",
        default_index=0
    )

# --- PAGE 1: HOME / INTRO PAGE ---
if selected == "Home":
    st.title("📘 Welcome to TNEA Info App")
    st.markdown("""
    ### Choose a Feature
    1. **Create TNEA Choice List** - View and filter colleges by cutoff, department, and community
    2. **TNEA Vacancy Seat Matrix** - Analyze current vacant seats by branch, college, and community

    Use the **left sidebar** to navigate between pages.

    ---

    📞 Contact: +91-8248696926  
    📧 Email: rajumurugannp@gmail.com  
    👨‍💻 Developed by Dr. Raju Murugan

    &copy; 2025 TNEA Info App. All rights reserved.
    """)

# --- PAGE 2: CREATE TNEA CHOICE LIST ---
elif selected == "Create TNEA Choice List":
    exec(open("app.py").read())

# --- PAGE 3: TNEA VACANCY SEAT MATRIX ---
elif selected == "TNEA Vacancy Seat Matrix":
    exec(open("tnea_vacancy_matrix.py").read())
