import streamlit as st
import math
from PIL import Image

# Configurazione pagina
st.set_page_config(page_title="Calcolatore Fotovoltaico", layout="wide")

# --- GESTIONE PASSWORD ---
# Puoi cambiare questa password in qualsiasi momento modificando la stringa sotto
PASSWORD_CORRETTA = "fotovoltaico2024"

if "autenticato" not in st.session_state:
    st.session_state["autenticato"] = False

if not st.session_state["autenticato"]:
    st.title("🔒 Accesso Riservato")
    password_inserita = st.text_input("Inserisci la password di accesso:", type="password")
    if st.button("Accedi"):
        if password_inserita == PASSWORD_CORRETTA:
            st.session_state["autenticato"] = True
            st.rerun()
        else:
            st.error("Password errata!")
    st.stop()

# --- APP PRINCIPALE ---
st.title("⚡ Calcolatore Impianti Fotovoltaici su Tetto")

# Sidebar - Parametri Standard
st.sidebar.header("⚙️ Dati Componenti Standard")
p_modello = st.sidebar.text_input("Modello Pannello", "ZS.455W")
p_potenza = st.sidebar.number_input("Potenza Pannello (Wp)", value=455)
p_larghezza_cm = st.sidebar.number_input("Larghezza Pannello (cm)", value=113.0)
p_altezza_cm = st.sidebar.number_input("Altezza Pannello (cm)", value=176.0)
profilo_lunghezza_m = st.sidebar.number_input("Lunghezza Profilo (m)", value=3.0)
vitoni_per_profilo = st.sidebar.number_input("Vitoni per profilo da 3m", value=3)

# Layout principale a colonne
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📐 Disposizione e Disegno")
    
    uploaded_file = st.file_uploader("Carica disegno/schema dell'architetto", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Schema Tetto Caricato", use_container_width=True)

    st.markdown("---")
    st.subheader("🔢 Configurazione Campo Fotovoltaico")
    num_file = st.number_input("Numero di File (righe)", min_value=1, value=3, step=1)
    pannelli_per_fila = st.number_input("Pannelli per ciascuna Fila", min_value=1, value=6, step=1)
    orientamento = st.selectbox("Orientamento Pannelli", ["Verticale (Ritratto)", "Orizzontale (Paesaggio)"])

with col2:
    st.subheader("📊 Risultati e Distinta Materiali")
    
    totale_pannelli = num_file * pannelli_per_fila
    potenza_totale_kwp = (totale_pannelli * p_potenza) / 1000.0

    # Calcolo ingombri
    if orientamento == "Verticale (Ritratto)":
        larghezza_fila_m = (pannelli_per_fila * p_larghezza_cm) / 100.0
        altezza_campo_m = (num_file * p_altezza_cm) / 100.0
    else:
        larghezza_fila_m = (pannelli_per_fila * p_altezza_cm) / 100.0
        altezza_campo_m = (num_file * p_larghezza_cm) / 100.0

    # Calcolo profili e ancoraggi
    # Si assumono 2 binari paralleli per ogni fila di pannelli
    metri_binario_necessari = larghezza_fila_m * 2 * num_file
    num_profili_3m = math.ceil(metri_binario_necessari / profilo_lunghezza_m)
    totale_vitoni = num_profili_3m * vitoni_per_profilo
    
    # Calcolo morsetti (clamps)
    morsetti_finali = num_file * 4
    morsetti_centrali = num_file * (pannelli_per_fila - 1) * 2

    # Visualizzazione Schede Metriche
    st.metric("Pannelli Totali", f"{totale_pannelli} pcs")
    st.metric("Potenza Totale Impianto", f"{potenza_totale_kwp:.2f} kWp")
    st.metric("Dimensioni Occupate Campo", f"{larghezza_fila_m:.2f} m × {altezza_campo_m:.2f} m")

    st.markdown("### 🛠️ Lista Materiali Necessaria")
    st.write(f"- **Pannelli ({p_modello}):** {totale_pannelli} pezzi")
    st.write(f"- **Profili in alluminio (3m):** {num_profili_3m} barre ({metri_binario_necessari:.2f} m totali)")
    st.write(f"- **Vitoni con staffe:** {totale_vitoni} pezzi")
    st.write(f"- **Morsetti Finali (End Clamps):** {morsetti_finali} pezzi")
    st.write(f"- **Morsetti Centrali (Mid Clamps):** {morsetti_centrali} pezzi")

    # Tasto Logout
    st.markdown("---")
    if st.button("Esci / Bloca App"):
        st.session_state["autenticato"] = False
        st.rerun()