import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# ======================
# CONFIG PAGE
# ======================
st.set_page_config(
    page_title="PhD Program in Structural and Geotechnical Engineering",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ======================
# SECRETS
# ======================
admin_password = st.secrets["app"]["ADMIN_PASSWORD"]

# ======================
# ADMIN LOGIN
# ======================
password = st.sidebar.text_input("Password", type="password")

if "admin_mode" not in st.session_state:
    st.session_state.admin_mode = False

if password:
    st.session_state.admin_mode = (password == admin_password)

admin_mode = st.session_state.admin_mode

# ======================
# GOOGLE SHEETS CONNECTION
# ======================
@st.cache_resource
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

client = connect()

# 🔴 SOSTITUISCI con il nome del tuo sheet
sheet = client.open("PhD Study Plan").sheet1

# ======================
# LOAD DATA
# ======================
data = sheet.get_all_records()
df = pd.DataFrame(data)

# ======================
# ADMIN DASHBOARD
# ======================
if admin_mode:

    st.sidebar.success("Admin mode ON")

    st.header("📊 Admin Dashboard")

    if df.empty:
        st.write("No data yet")

    else:

        # ======================
        # STUDENTS → COURSES
        # ======================
        st.subheader("👨‍🎓 Students and their courses")

        if "student" in df.columns and "course" in df.columns:

            for _, row in df.iterrows():
                student = row["student"]
                courses_raw = row["course"]

                courses = [c.strip() for c in str(courses_raw).split(",") if c.strip()]

                with st.expander(student):
                    for c in courses:
                        st.write(f"- {c}")

        else:
            st.warning("Columns 'student' and 'course' not found")

        # ======================
        # COURSE COUNTS
        # ======================
        st.subheader("📊 Students per course")

        course_counts = {}

        if "course" in df.columns:

            for row in df["course"]:
                courses_list = [c.strip() for c in str(row).split(",") if c.strip()]

                for c in courses_list:
                    course_counts[c] = course_counts.get(c, 0) + 1

            for course, count in sorted(course_counts.items()):
                st.write(f"- {course}: {count}")

        else:
            st.warning("Column 'course' not found")

else:
    st.info("Enter password in the sidebar to access admin mode")
