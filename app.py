import streamlit as st
import math
import os
from PIL import Image
from google import genai
import json

# Configurazione pagina
st.set_page_config(page_title="Scanner Fotovoltaico Automatico", layout="wide")

# --- CHIAVE API NASCOSTA ---
# Puoi inserire la tua API key direttamente qui fra le virgolette
API_KEY_DI_DEFAULT = "AQ.Ab8RN6J3B7QlzePrfr_P2B5D9UdyhawhjhoB239zV_69Kqi60A" 

# Recupera la chiave dai secret di Streamlit, dalle variabili di ambiente o dalla riga sopra
API_KEY = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", API_KEY_DI_DEFAULT))

# --- APP PRINCIPALE ---
st.title("⚡ Scanner Automatico Disegni Fotovoltaici")

# Parametri Standard nella sidebar
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
        if not API_KEY or API_KEY == "LA_TUA_API_KEY_QUI":
            st.error("⚠️ Chiave API non configurata! Inserisci la tua API Key nel file app.py o nei Secrets di Streamlit.")
        else:
            with st.spinner("Scannerizzazione dell'immagine in corso con l'IA (Gemini 3.8 Flash)..."):
                try:
                    # Inizializzazione del client GenAI con la chiave nascosta
                    client = genai.Client(api_key=API_KEY)

                    prompt = """
                    Analizza questa immagine di un layout di impianto fotovoltaico su tetto.
                    Rispondi ESCLUSIVAMENTE con un oggetto JSON valido, senza blocchi di codice markdown, con questa struttura esatta:
                    {
                        "totale_pannelli": 18,
                        "file": [
                            {"numero_fila": 1, "pannelli_in_questa_fila": 6},
                            {"numero_fila": 2, "pannelli_in_questa_fila": 6},
                            {"numero_fila": 3, "pannelli_in_questa_fila": 6}
                        ]
                    }
                    Conta accuratamente il numero totale di pannelli e individua come sono divisi nelle varie file/gruppi continui orientati.
                    """

                    # Utilizzo della nuova Interactions API e del modello gemini-3.8-flash
                    interaction = client.interactions.create(
                        model='gemini-3.8-flash',
                        input=[image, prompt]
                    )
                    
                    testo_risposta = interaction.output_text
                    
                    # Pulizia da eventuale formattazione markdown
                    clean_json = testo_risposta.replace("```json", "").replace("```", "").strip()
                    dati = json.loads(clean_json)

                    totale_pannelli = dati["totale_pannelli"]
                    file_dettaglio = dati["file"]

                    st.success(f"✅ Rilevati **{totale_pannelli} pannelli** nell'immagine!")

                    # Calcolo profili e componenti per ogni fila identificata
                    metri_binario_totali = 0
                    morsetti_finali = 0
                    morsetti_centrali = 0

                    for fila in file_dettaglio:
                        n_p = fila["pannelli_in_questa_fila"]
                        lungh_fila = n_p * p_larg_m
                        metri_binario_totali += (lungh_fila * 2) # 2 binari paralleli per fila
                        
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
