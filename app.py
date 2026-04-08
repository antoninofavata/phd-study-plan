#This repository contains code developed and maintained by Antonino Favata antonino.favata@uniroma1.it
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
import io
from collections import defaultdict

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

st.title("PhD in Structural and Geotechnical Engineering")

# ======================
# ADMIN LOGIN
# ======================

admin_password = st.secrets["app"]["ADMIN_PASSWORD"]

password = st.sidebar.text_input(
    "Password",
    type="password",
    key="admin_password"
)

if "admin_mode" not in st.session_state:
    st.session_state.admin_mode = False

if password:
    st.session_state.admin_mode = (password == admin_password)

admin_mode = st.session_state.admin_mode

# ======================
# COURSE CATALOGUE
# ======================

st.header("Course Catalogue")

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
                st.markdown(c["description"])

            if "program" in c:
                st.markdown("**Program**")
                st.markdown(c["program"])

st.subheader("Phase B")

sectors = [
    "Mechanics of Solids and Structures",
    "Structural Engineering",
    "Geotechnical Engineering"
]

for s in sectors:
    st.markdown(f"### {s}")

    for c in courses:
        if c["phase"] == "B" and c.get("sector") == s:

            years_str = ", ".join(f"{y}/{y+1}" for y in c["years"])

            with st.expander(c["name"]):
                st.markdown(f"**Available in:** {years_str}")

                if "professor" in c:
                    st.markdown(f"**Professor:** {c['professor']}")

                if "description" in c:
                    st.markdown("**Description**")
                    st.markdown(c["description"])

                if "program" in c:
                    st.markdown("**Program**")
                    st.markdown(c["program"])

# ======================
# RULES
# ======================

st.header("Rules")

st.markdown("""
- At least **3 courses from Phase A**  
- At least **3 courses from Phase B**  
- At least **4 courses in Year 1**
- Students in the current second year (40th cycle) are required to choose at least **3 courses in total** (preferably complementary to those already taken)
""")

# ======================
# STUDENT FORM
# ======================

st.header("Create your Study Plan")

first_name = st.text_input("First Name")
last_name = st.text_input("Last Name")
cycle = st.text_input("Cycle")
email = st.text_input("Email")
st.markdown("### Notes (optional)")

st.caption(
    """
    Please use this field to include:
    - Courses attended last year (for 2nd year PhD students)
    - Planned courses (CISM, other PhD programs, etc.)
    - Special cases or exceptions
    - Any additional relevant information
    """
)

notes = st.text_area("")

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

    if not first_name or not last_name or not cycle or not email:
        st.error("Please fill in all required fields.")

    elif not selected_courses:
        st.error("Please select at least one course.")

    else:
        for course in selected_courses:
            sheet.append_row([
                first_name,
                last_name,
                cycle,
                email,
                course,
                notes
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
        # STUDENTS → COURSES + NOTES
        # ======================

        st.subheader("Students and their courses")

        student_data = {}

        for _, row in df.iterrows():

            first_name = row.get("first_name")
            last_name = row.get("last_name")
            course = row.get("course")
            notes_val = row.get("notes")

            if pd.isna(first_name) or pd.isna(last_name) or pd.isna(course):
                continue

            student = f"{first_name} {last_name}"

            if student not in student_data:
                student_data[student] = {
                    "courses": [],
                    "notes": notes_val
                }

            student_data[student]["courses"].append(course)

        for student in sorted(student_data):

            courses_list = sorted(set(student_data[student]["courses"]))
            notes_val = student_data[student]["notes"]

            with st.expander(student):

                for c in courses_list:
                    st.write(f"- {c}")

                if notes_val and not pd.isna(notes_val):
                    st.markdown("**Notes:**")
                    st.write(notes_val)

        # ======================
        # EXPORT STRUCTURED PLANS
        # ======================

        st.subheader("Export structured plans")

        student_data = defaultdict(list)

        for _, row in df.iterrows():

            first_name = row.get("first_name")
            last_name = row.get("last_name")
            email = row.get("email")
            cycle = row.get("cycle")
            course = row.get("course")
            notes_val = row.get("notes")

            if pd.isna(first_name) or pd.isna(last_name) or pd.isna(course):
                continue

            key = (last_name, first_name)

            student_data[key].append({
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "cycle": cycle,
                "course": course,
                "notes": notes_val
            })

        buffer = io.BytesIO()

        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:

            for (last_name, first_name) in sorted(student_data.keys()):

                records = student_data[(last_name, first_name)]

                email = records[0]["email"]
                cycle = records[0]["cycle"]
                notes_val = records[0].get("notes")

                courses_list = sorted(set(r["course"] for r in records))

                rows = []

                rows.append(["Last name", last_name, "", ""])
                rows.append(["First name", first_name, "", ""])
                rows.append(["Cycle", cycle, "", ""])
                rows.append(["Email", email, "", ""])

                if notes_val and not pd.isna(notes_val):
                    rows.append(["Notes", notes_val, "", ""])

                rows.append(["", "", "", ""])
                rows.append(["Courses", "", "", ""])

                for c in courses_list:
                    rows.append(["", c, "", ""])

                df_student = pd.DataFrame(rows)

                sheet_name = f"{last_name}_{first_name}"[:31]

                df_student.to_excel(
                    writer,
                    sheet_name=sheet_name,
                    index=False,
                    header=False
                )

        st.download_button(
            label="Download structured plans",
            data=buffer.getvalue(),
            file_name="students_structured.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        # ======================
        # COURSE COUNTS
        # ======================
        
        st.subheader("Students per course")
        
        course_counts = {}
        
        for course in df["course"]:
            if pd.isna(course):
                continue
            course_counts[course] = course_counts.get(course, 0) + 1
        
        for course, count in sorted(course_counts.items()):
            st.write(f"- {course}: {count}")

# ======================
# EXPORT PER COURSE 
# ======================

        st.subheader("Export students per course")
        
        import io
        
        required_cols = {"first_name", "last_name", "email", "cycle", "course"}
        
        if required_cols.issubset(df.columns):
        
            courses_list = sorted(df["course"].dropna().unique())
        
            for course in courses_list:
        
                df_course = df[df["course"] == course]
        
                # rimuove duplicati studenti nello stesso corso
                df_course = df_course.drop_duplicates(
                    subset=["first_name", "last_name", "email"]
                )
        
                # seleziona e rinomina colonne
                df_export = df_course[[
                    "last_name",
                    "first_name",
                    "cycle",
                    "email"
                ]].rename(columns={
                    "last_name": "Cognome",
                    "first_name": "Nome",
                    "cycle": "Ciclo",
                    "email": "Email"
                })
        
                buffer = io.BytesIO()
        
                with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                    df_export.to_excel(writer, index=False, sheet_name="Students")
        
                file_name = course.replace(" ", "_").replace(",", "") + ".xlsx"
        
                st.download_button(
                    label=f"Download: {course}",
                    data=buffer.getvalue(),
                    file_name=file_name,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
