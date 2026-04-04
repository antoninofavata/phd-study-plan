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

st.title("PhD in Structural and Geotechnical Engineering")

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
                st.markdown(c["description"])

            if "program" in c:
                st.markdown("**Program**")
                st.markdown(c["program"])

# ----------------------
# PHASE B
# ----------------------

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
""")

# ======================
# STUDENT FORM
# ======================

st.header("Create your Study Plan")

name = st.text_input("Name")
cycle = st.text_input("Cycle")
email = st.text_input("Email")

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

    if not name or not cycle or not email:
        st.error("Please fill in all required fields.")

    elif not selected_courses:
        st.error("Please select at least one course.")

    else:
        for course in selected_courses:
            sheet.append_row([
                name,
                cycle,
                email,
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
                course = row.get("course")

                if pd.isna(student) or pd.isna(course):
                    continue

                student_courses.setdefault(student, []).append(course)

            for student in sorted(student_courses):

                courses = sorted(set(student_courses[student]))

                with st.expander(student):
                    for c in courses:
                        st.write(f"- {c}")

        # ======================
        # EXPORT PER COURSE
        # ======================
        st.subheader("Export students per course")

        import io

        if "course" in df.columns and "name" in df.columns and "email" in df.columns:

            courses_list = sorted(df["course"].dropna().unique())

            for course in courses_list:

                df_course = df[df["course"] == course][["name", "email"]]
                df_course = df_course.drop_duplicates()

                buffer = io.BytesIO()
                df_course.to_excel(buffer, index=False)

                file_name = course.replace(" ", "_").replace(",", "") + ".xlsx"

                st.download_button(
                    label=f"Download: {course}",
                    data=buffer.getvalue(),
                    file_name=file_name,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )        
        # ======================
        # COURSE COUNTS
        # ======================
        st.subheader("Students per course")

        if "course" in df.columns:

            course_counts = {}

            for course in df["course"]:
                if pd.isna(course):
                    continue

                course_counts[course] = course_counts.get(course, 0) + 1

            for course, count in sorted(course_counts.items()):
                st.write(f"- {course}: {count}")

        # ======================
        # PIANI DI STUD
        # ======================

        st.subheader("Export: general plans (one course per row)")

        import io
        from collections import defaultdict
        
        if "name" in df.columns and "course" in df.columns and "email" in df.columns and "cycle" in df.columns:
        
            student_data = defaultdict(list)
        
            for _, row in df.iterrows():
        
                name = row.get("name")
                email = row.get("email")
                cycle = row.get("cycle")
                course = row.get("course")
        
                if pd.isna(name) or pd.isna(course):
                    continue
        
                student_data[name].append({
                    "email": email,
                    "cycle": cycle,
                    "course": course
                })
        
            buffer = io.BytesIO()
        
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        
                for student, records in student_data.items():
        
                    email = records[0]["email"]
                    cycle = records[0]["cycle"]
        
                    courses = sorted(set(r["course"] for r in records))
        
                    # una riga per ogni corso
                    df_student = pd.DataFrame([
                        {
                            "name": student,
                            "cycle": cycle,
                            "email": email,
                            "course": c
                        }
                        for c in courses
                    ])
        
                    sheet_name = student[:31]
        
                    df_student.to_excel(writer, sheet_name=sheet_name, index=False)
        
            st.download_button(
                label="Download all students (row per course)",
                data=buffer.getvalue(),
                file_name="students_by_course.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
