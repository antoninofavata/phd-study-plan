import streamlit as st

# ======================
# CONFIG (DEVE STARE SUBITO QUI)
# ======================

st.set_page_config(
    page_title="PhD Study Plan",
    initial_sidebar_state="collapsed"
)

import yaml
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# ======================
# CONFIG ADMIN
# ======================

ADMIN_PASSWORD = "cambia_questa_password"

SHEET_ID = "1BTHZsKMHjSBDO6hC2eZwOmV_2WlLYY_Unujhco-zdwM"

# ======================
# CONNECT GOOGLE SHEETS
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

    return gspread.authorize(creds)

# ======================
# LOAD & SAVE DATA
# ======================

def load_data():
    client = connect()
    sheet = client.open_by_key(SHEET_ID).sheet1
    return sheet.get_all_records()

def save_data(name, cycle, courses):
    client = connect()
    sheet = client.open_by_key(SHEET_ID).sheet1

    courses_str = ", ".join(courses)

    sheet.append_row([name, cycle, courses_str])

# ======================
# LOAD COURSES
# ======================

with open("courses.yaml", "r") as f:
    courses = yaml.safe_load(f)["courses"]

# ======================
# TITLE
# ======================

st.title("PhD Study Plan")

# ======================
# ADMIN LOGIN
# ======================

password = st.sidebar.text_input("Admin password", type="password")

# ======================
# COURSE CATALOGUE
# ======================

st.header("Course Catalogue")

st.subheader("Phase A")

for c in courses:
    if c["phase"] == "A":
        years_str = ", ".join(f"{y}/{y+1}" for y in c["years"])
        with st.expander(f"{c['name']} ({years_str})"):
            st.write("Methodological course")
            st.write(f"Available in: {years_str}")

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
# STUDENT FORM
# ======================

st.header("Create your Study Plan")

name = st.text_input("Name")
cycle = st.text_input("Cycle")

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
        save_data(name, cycle, selected_courses)
        st.success("Study plan submitted successfully!")

# ======================
# ADMIN DASHBOARD
# ======================

if password == ADMIN_PASSWORD:

    st.header("📊 Admin Dashboard")

    data = load_data()

    if data:
        df = pd.DataFrame(data)

        st.write("### All submissions")
        st.dataframe(df)

        st.write("### Students per course")

        all_courses = []

        if "course" in df.columns or "Courses" in df.columns:

            col_name = "course" if "course" in df.columns else "Courses"

            for row in df[col_name]:
                all_courses.extend([c.strip() for c in row.split(",")])

            counts = pd.Series(all_courses).value_counts()

            df_counts = counts.reset_index()
            df_counts.columns = ["Course", "Number of students"]

            df_counts = df_counts.sort_values(
                by="Number of students",
                ascending=False
            )

            st.table(df_counts)

        else:
            st.error("Column 'course' not found")

    else:
        st.write("No data yet")

elif password:
    st.warning("Wrong password")
