import streamlit as st
import math
from PIL import Image
import google.generativeai as genai
import json

# Configurazione pagina
st.set_page_config(page_title="Scanner Fotovoltaico Automatico", layout="wide")

# --- GESTIONE PASSWORD ---
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
st.title("⚡ Scanner Automatico Disegni Fotovoltaici")

# Configurazione API Key (Inserisci la tua chiave gratuita di Google AI Studio)
API_KEY = st.sidebar.text_input("Chiave API Google Gemini (Gratuita)", type="password")

# Parametri Standard
st.sidebar.header("⚙️ Dati Componenti")
p_potenza = st.sidebar.number_input("Potenza Pannello (Wp)", value=455)
p_larg_m = st.sidebar.number_input("Larghezza Pannello (m)", value=1.13)
p_alt_m = st.sidebar.number_input("Altezza Pannello (m)", value=1.76)
profilo_lunghezza_m = 3.0
vitoni_per_profilo = 3

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("🖼️ Carica Disegno Architetto")
    uploaded_file = st.file_uploader("Scegli un'immagine del tetto (JPG/PNG)", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Disegno Caricato", use_container_width=True)
        
        analizza_btn = st.button("🔍 Scannerizza e Calcola Materiali")

with col2:
    st.subheader("📊 Analisi Automatica e Materiali")
    
    if uploaded_file is not None and 'analizza_btn' in locals() and analizza_btn:
        if not API_KEY:
            st.warning("⚠️ Per la scannerizzazione automatica inserisci la tua API Key nella barra a sinistra.")
        else:
            with st.spinner("Scannerizzazione dell'immagine in corso con l'IA..."):
                try:
                    genai.configure(api_key=API_KEY)
                    model = genai.GenerativeModel('gemini-1.5-flash')

                    prompt = """
                    Analizza questa immagine di un layout di impianto fotovoltaico su tetto.
                    Rispondi ESCLUSIVAMENTE in formato JSON con la seguente struttura:
                    {
                        "totale_pannelli": int,
                        "file": [
                            {"numero_fila": 1, "pannelli_in_questa_fila": int},
                            {"numero_fila": 2, "pannelli_in_questa_fila": int}
                        ]
                    }
                    Conta accuratamente il numero totale di pannelli e come sono divisi nelle varie file/righe continuous.
                    """

                    response = model.generate_content([prompt, image])
                    
                    # Pulizia risposta JSON
                    clean_json = response.text.replace("```json", "").replace("```", "").strip()
                    dati = json.loads(clean_json)

                    totale_pannelli = dati["totale_pannelli"]
                    file_dettaglio = dati["file"]

                    st.success(f"✅ Rilevati **{totale_pannelli} pannelli** nell'immagine!")

                    # Calcolo profili e componenti per ogni fila identificata dall'IA
                    metri_binario_totali = 0
                    morsetti_finali = 0
                    morsetti_centrali = 0

                    for fila in file_dettaglio:
                        n_p = fila["pannelli_in_questa_fila"]
                        # Lunghezza della singola fila (assumendo pannelli affiancati sul lato corto)
                        lungh_fila = n_p * p_larg_m
                        metri_binario_totali += (lungh_fila * 2) # 2 binari per fila
                        
                        morsetti_finali += 4
                        morsetti_centrali += max(0, (n_p - 1) * 2)

                    num_profili_3m = math.ceil(metri_binario_totali / profilo_lunghezza_m)
                    totale_vitoni = num_profili_3m * vitoni_per_profilo
                    potenza_totale_kwp = (totale_pannelli * p_potenza) / 1000.0

                    # Output Risultati
                    st.metric("Pannelli Rilevati", f"{totale_pannelli} pcs")
                    st.metric("Potenza Totale", f"{potenza_totale_kwp:.2f} kWp")

                    st.markdown("### 🛠️ Lista Materiali Calcolata")
                    st.write(f"- **Pannelli (ZS.455W):** {totale_pannelli} pezzi")
                    st.write(f"- **Metri lineari binari necessari:** {metri_binario_totali:.2f} m")
                    st.write(f"- **Profili in alluminio (3m):** {num_profili_3m} barre")
                    st.write(f"- **Vitoni con staffa:** {totale_vitoni} pezzi")
                    st.write(f"- **Morsetti Finali:** {morsetti_finali} pezzi")
                    st.write(f"- **Morsetti Centrali:** {morsetti_centrali} pezzi")

                except Exception as e:
                    st.error(f"Errore durante l'analisi dell'immagine: {e}")
