import streamlit as st

st.sidebar.header("Admin Login")

password = st.sidebar.text_input("Password", type="password")

ADMIN_PASSWORD = "sge_26"
import streamlit as st
import yaml
import gspread
from google.oauth2.service_account import Credentials

# ======================
# GOOGLE SHEETS CONNECTION
# ======================

def connect():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scope
    )

    client = gspread.authorize(creds)
    return client

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
# PHASE A
# -----------------------

st.subheader("Phase A")

for c in courses:
    if c["phase"] == "A":
        years_str = ", ".join(f"{y}/{y+1}" for y in c["years"])
        
        with st.expander(f"{c['name']} ({years_str})"):
            st.write("Methodological course")
            st.write(f"Available in: {years_str}")

# -----------------------
# PHASE B
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
# COURSE SELECTION
# ======================

st.header("Select your courses")

selected_courses = []

for c in courses:
    years_str = ", ".join(f"{y}/{y+1}" for y in c["years"])
    label = f"{c['name']} ({years_str})"
    
    if st.checkbox(label):
        selected_courses.append(label)

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
        try:
            client = connect()
            sheet = client.open_by_key("1BTHZsKMHjSBDO6hC2eZwOmV_2WlLYY_Unujhco-zdwM").sheet1

            # Scrive una riga per ogni corso
            for course in selected_courses:
                sheet.append_row([
                    name,
                    cycle,
                    course
                ])

            st.success("Study plan submitted and saved!")

        except Exception as e:
            st.error("Error saving data to Google Sheets")
            st.write(e)

        # Mostra riepilogo
        st.write("## Submitted Data")
        st.write(f"**Name:** {name}")
        st.write(f"**Cycle:** {cycle}")

        st.write("**Courses:**")
        for course in selected_courses:
            st.write(f"- {course}")
