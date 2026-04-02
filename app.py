import streamlit as st
import yaml

# ======================
# CARICAMENTO DATI
# ======================

with open("courses.yaml", "r") as f:
    courses = yaml.safe_load(f)["courses"]

# ======================
# INTERFACCIA
# ======================

st.title("PhD Study Plan")

st.subheader("Seleziona i corsi")

name = st.text_input("Nome e Cognome")
email = st.text_input("Email")

# ======================
# SELEZIONE CORSI
# ======================

selected_courses = []

for c in courses:
    years_str = ", ".join(f"{y}/{y+1}" for y in c["years"])
    
    label = f"{c['name']} ({years_str})"
    
    if st.checkbox(label):
        selected_courses.append(c["name"])

# ======================
# OUTPUT
# ======================

st.write("### Corsi selezionati:")

if selected_courses:
    for course in selected_courses:
        st.write(f"- {course}")
else:
    st.write("Nessun corso selezionato")

# ======================
# INVIO
# ======================

if st.button("Invia piano di studio"):
    
    if not name or not email:
        st.error("Inserisci nome ed email prima di inviare.")
    elif not selected_courses:
        st.error("Seleziona almeno un corso.")
    else:
        st.success("Piano inviato correttamente!")

        # Mostra riepilogo
        st.write("## Riepilogo")
        st.write(f"**Nome:** {name}")
        st.write(f"**Email:** {email}")
        st.write("**Corsi scelti:**")

        for course in selected_courses:
            st.write(f"- {course}")
