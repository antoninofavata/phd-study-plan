import streamlit as st

st.set_page_config(
    page_title="PhD Program in Structural and Geotechnical Engineering",
    layout="wide",
    initial_sidebar_state="collapsed"
)

import yaml
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

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
# LOAD DATA
# ======================

with open("courses.yaml", "r") as f:
    courses = yaml.safe_load(f)["courses"]

# ======================
# GOOGLE SHEETS
# ======================

client = connect()
sheet = client.open_by_key(
    "1BTHZsKMHjSBDO6hC2eZwOmV_2WlLYY_Unujhco-zdwM"
).sheet1

# ======================
# TITLE
# ======================

st.title("PhD Program in Structural and Geotechnical Engineering")

# ======================
# ADMIN LOGIN
# ======================

admin_password = st.secrets["app"]["ADMIN_PASSWORD"]

password = st.sidebar.text_input("Password", type="password")

if "admin_mode" not in st.session_state:
    st.session_state.admin_mode = False

if password:
    st.session_state.admin_mode = (password == admin_password)

admin_mode = st.session_state.admin_mode

# ======================
# COURSE CATALOGUE
# ======================

st.header("Course Catalogue")

# ----------------------
# PHASE A
# ----------------------

st.subheader("Phase A")

for c in courses:
    if c["phase"] == "A":
        years_str = ", ".join(f"{y}/{y+1}" for y in c["years"])

        with st.expander(c["name"]):
            st.markdown(f"**Available in:** {years_str}")

            if "professor" in c:
                st.markdown(f"**Professor:** {c['professor']}")

            if "description" in c:
                st.markdown("**Description**")
                st.write(c["description"])

            if "program" in c:
                st.markdown("**Program**")
                st.markdown(c["program"])

          #  st.markdown("---")

# ----------------------
# PHASE B
# ----------------------

st.subheader("Phase B")

sectors = sorted(
    set(c.get("sector", "") for c in courses if c["phase"] == "B")
)

for s in sectors:
    st.markdown(f"### {s}")

    for c in courses:
        if c["phase"] == "B" and c.get("sector") == s:

            years_str = ", ".join(f"{y}/{y+1}" for y in c["years"])

            with st.expander(c["name"]):
                st.markdown(f"**Available in:** {years_str}")

                if "description" in c:
                    st.markdown("**Description**")
                    st.write(c["description"])

                st.markdown("---")

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

# ======================
# COURSE SELECTION
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
        for course in selected_courses:
            sheet.append_row([
                name,
                cycle,
                course
            ])

        st.success("Study plan submitted successfully!")

# ======================
# ADMIN DASHBOARD
# ======================

if admin_mode:

    st.sidebar.success("Admin mode ON")

    data = sheet.get_all_records()
    df = pd.DataFrame(data)

    st.header("📊 Admin Dashboard")

    if not df.empty:

        # ======================
        # STUDENTS → COURSES
        # ======================
        st.subheader("Students and their courses")

        if "name" in df.columns and "course" in df.columns:

            student_courses = {}

            for _, row in df.iterrows():

                student = row.get("name")
                courses_raw = row.get("course")

                if pd.isna(student) or pd.isna(courses_raw):
                    continue

                courses_list = [
                    c.strip() for c in str(courses_raw).split(",") if c.strip()
                ]

                student_courses.setdefault(student, []).extend(courses_list)

            for student in sorted(student_courses):

                courses = sorted(set(student_courses[student]))

                with st.expander(student):
                    for c in courses:
                        st.write(f"- {c}")

        # ======================
        # COURSE COUNTS
        # ======================
# ======================
# COURSE COUNTS
# ======================

            st.subheader("Students per course")
            
            course_counts = {}
            
            if admin_mode and "course" in df.columns:
            
                for row in df["course"]:
            
                    if pd.isna(row):
                        continue
            
                    courses_list = [
                        c.strip() for c in str(row).split(",") if c.strip()
                    ]
            
                    for c in courses_list:
                        course_counts[c] = course_counts.get(c, 0) + 1
            
                for course, count in sorted(course_counts.items()):
                    st.write(f"- {course}: {count}")
