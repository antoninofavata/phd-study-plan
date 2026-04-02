import streamlit as st
import yaml

# ======================
# CARICAMENTO DATI
# ======================

with open("courses.yaml", "r") as f:
    courses = yaml.safe_load(f)["courses"]

# ======================
# TITOLO
# ======================

st.title("PhD Study Plan")

# ======================
# INFORMAZIONI INIZIALI
# ======================

st.header("Informazioni sui corsi")

st.markdown("""
### Fase A
- Scientific Computing and Python Programming  
- Probability Theory and Statistics  
- Time Series Analysis and Data-driven Modeling  
- Experimental Methods: Laboratory and In-situ Testing  
- Numerical Analysis for Engineering Models  
- Functional Analysis and Variational Methods for Engineering Applications  

### Fase B

#### Mechanics of Solids and Structures
- Variational methods for solid mechanics  
- Linear and nonlinear structural dynamics  
- Continuum Mechanics and Thermodynamics  
- Advanced Finite Element Methods  

#### Structural Engineering
- Integrated seismic and energy rehabilitation of reinforced concrete buildings  
- Seismic Safety and Sustainability  
- Masonry structures  

#### Geotechnical Engineering
- Constitutive Modelling of Geomaterials  
- Numerical Modelling in Geomechanics  
- Soil Structure Interaction  
- Special Topics in Geotechnical Engineering  
""")

st.divider()

# ======================
# DATI UTENTE
# ======================

st.subheader("Dati studente")

name = st.text_input("Nome e Cognome")
email = st.text_input("Email")

st.divider()

# ======================
# SELEZIONE CORSI
# ======================

st.header("Selezione corsi")

selected_courses = []

# --- FASE A ---
st.subheader("Fase A")

for c in courses:
    if c["phase"] == "A":
        years_str = ", ".join(f"{y}/{y+1}" for y in c["years"])
        label = f"{c['name']} ({years_str})"
        
        if st.checkbox(label):
            selected_courses.append(c["name"])

st.divider()

# --- FASE B ---
st.subheader("Fase B")

sectors = [
    "Mechanics of Solids and Structures",
    "Structural Engineering",
    "Geotechnical Engineering"
]

for sector in sectors:
    st.markdown(f"### {sector}")
    
    for c in courses:
        if c["phase"] == "B" and c["sector"] == sector:
            years_str = ", ".join(f"{y}/{y+1}" for y in c["years"])
            label = f"{c['name']} ({years_str})"
            
            if st.checkbox(label):
                selected_courses.append(c["name"])

    st.divider()

# ======================
# RIEPILOGO
# ======================

st.header("Riepilogo")

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
        st.error("Inserisci nome ed email.")
    
    elif not selected_courses:
        st.error("Seleziona almeno un corso.")
    
    else:
        st.success("Piano inviato correttamente!")

        st.write("## Dati inviati")
        st.write(f"**Nome:** {name}")
        st.write(f"**Email:** {email}")
        
        st.write("**Corsi selezionati:**")
        for course in selected_courses:
            st.write(f"- {course}")
