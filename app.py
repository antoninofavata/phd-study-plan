import streamlit as st
import yaml

# ======================
# LOAD DATA
# ======================

with open("courses.yaml", "r") as f:
    courses = yaml.safe_load(f)["courses"]

# ======================
# TITLE
# ======================

st.title("PhD Study Plan")

# ======================
# COURSE CATALOGUE
# ======================

st.header("Course Catalogue")

# -----------------------
# FASE A
# -----------------------

st.subheader("Phase A")

for c in courses:
    if c["phase"] == "A":
        years_str = ", ".join(f"{y}/{y+1}" for y in c["years"])
        
        with st.expander(f"{c['name']} ({years_str})"):
            st.write("Methodological course")
            st.write(f"Available in: {years_str}")

# -----------------------
# FASE B
# -----------------------

st.subheader("Phase B")

sectors = sorted(set(c.get("sector", "") for c in courses if c["phase"] == "B"))

for s in sectors:
    st.markdown(f"### {s}")
    
    for c in courses:
        if c["phase"] == "B" and c.get("sector") == s:
            years_str = ", ".join(f"{y}/{y+1}" for y in c["years"])
            
            with st.expander(f"{c['name']} ({years_str})"):
                st.write(f"Sector: {s}")
                st.write(f"Available in: {years_str}")
                st.write("Detailed description coming soon...")

# ======================
# RULES
# ======================

st.header("Rules")

st.markdown("""
- At least **3 courses from Phase A**  
- At least **3 courses from Phase B**  
- At least **4 courses in Year 1**  
""")

# ======================
# STUDENT INFO
# ======================

st.header("Create your Study Plan")

name = st.text_input("Name")
cycle = st.text_input("Cycle")

# ======================
# SELECTION
# ======================

st.header("Select your courses")

selected_courses = []

for c in courses:
    years_str = ", ".join(f"{y}/{y+1}" for y in c["years"])
    label = f"{c['name']} ({years_str})"
    
    if st.checkbox(label):
        selected_courses.append(c["name"])

# ======================
# SUMMARY
# ======================

st.header("Summary")

if selected_courses:
    for course in selected_courses:
        st.write(f"- {course}")
else:
    st.write("No courses selected")

# ======================
# SUBMIT
# ======================

if st.button("Submit Study Plan"):

    if not name or not cycle:
        st.error("Please fill in all required fields.")
    
    elif not selected_courses:
        st.error("Please select at least one course.")
    
    else:
        st.success("Study plan submitted successfully!")

        st.write("## Submitted Data")
        st.write(f"**Name:** {name}")
        st.write(f"**Cycle:** {cycle}")

        st.write("**Courses:**")
        for course in selected_courses:
            st.write(f"- {course}")

import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

def connect():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )
    client = gspread.authorize(creds)
    return client

st.title("Test Google Sheets")

if st.button("Scrivi test su Sheets"):
    client = connect()
    
    sheet = client.open("PhD Study Plans").sheet1
    
    sheet.append_row(["Test", "Funziona", "OK"])
    
    st.success("Riga scritta con successo!")
