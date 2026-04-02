import streamlit as st
import yaml
import pandas as pd
from datetime import datetime

# -----------------------
# LOAD DATA
# -----------------------
with open("courses.yaml") as f:
    courses = yaml.safe_load(f)["courses"]

# -----------------------
# TITLE
# -----------------------
st.title("PhD Study Plan")
st.subheader("Structural and Geotechnical Engineering")

# -----------------------
# YEAR SELECTION
# -----------------------
year_label = st.selectbox(
    "Academic Year",
    ["2025/26", "2026/27"]
)

year = 2025 if year_label == "2025/26" else 2026

active = [c for c in courses if year in c["years"]]

# -----------------------
# SHOW COURSES
# -----------------------
st.header("Course Catalogue")

# Fase A
st.subheader("Phase A")
for c in active:
    if c["phase"] == "A":
        with st.expander(c["name"]):
            st.write("Methodological course")

# Fase B per settore
st.subheader("Phase B")

sectors = sorted(set(c.get("sector","") for c in active if c["phase"]=="B"))

for s in sectors:
    st.markdown(f"**{s}**")
    for c in active:
        if c["phase"]=="B" and c.get("sector")==s:
            with st.expander(c["name"]):
                st.write(f"Sector: {s}")

# -----------------------
# RULES
# -----------------------
st.header("Rules")
st.markdown("""
- At least **3 courses from Phase A**  
- At least **3 courses from Phase B**  
- At least **4 courses in Year 1**  
""")

# -----------------------
# STUDENT INFO
# -----------------------
st.header("Create your Study Plan")

name = st.text_input("Name")
cycle = st.text_input("Cycle")

# -----------------------
# SELECTION
# -----------------------
selected = []

st.subheader("Select Courses")

for c in active:
    col1, col2 = st.columns([3,1])

    with col1:
        check = st.checkbox(f"{c['name']} ({c['phase']})", key=c["id"])

    with col2:
        year_choice = st.selectbox(
            "Year",
            ["", "1", "2"],
            key=f"{c['id']}_year"
        )

    if check and year_choice:
        selected.append({
            "course": c["name"],
            "phase": c["phase"],
            "year": int(year_choice)
        })

# -----------------------
# VALIDATION + SAVE
# -----------------------
if st.button("Submit Plan"):

    A = [c for c in selected if c["phase"]=="A"]
    B = [c for c in selected if c["phase"]=="B"]
    Y1 = [c for c in selected if c["year"]==1]

    if len(A) < 3:
        st.error("You must select at least 3 Phase A courses")
    elif len(B) < 3:
        st.error("You must select at least 3 Phase B courses")
    elif len(Y1) < 4:
        st.error("You must select at least 4 courses in Year 1")
    else:
        st.success("Plan submitted successfully!")

        df = pd.DataFrame(selected)
        df["name"] = name
        df["cycle"] = cycle
        df["year_plan"] = year_label
        df["timestamp"] = datetime.now()

        try:
            old = pd.read_csv("plans.csv")
            df = pd.concat([old, df])
        except:
            pass

        df.to_csv("plans.csv", index=False)
