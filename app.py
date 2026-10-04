import streamlit as st
import math
from PIL import Image
from google import genai
import json

# Configurazione della pagina
st.set_page_config(page_title="Scanner Fotovoltaico Automatico", layout="wide")

# ==============================================================================
# DATI E CONFIGURAZIONE HARDCODED
# ==============================================================================
API_KEY = "AQ.Ab8RN6J3B7QlzePrfr_P2B5D9UdyhawhjhoB239zV_69Kqi60A"  # Sostituisci con la tua chiave reale

# Parametri standard componenti
P_POTENZA_WP = 455            # Potenza del pannello ZS.455W in Watt
P_LARGHEZZA_M = 1.13          # Larghezza pannello (113 cm -> 1.13 m)
P_ALTEZZA_M = 1.76            # Altezza pannello (176 cm -> 1.76 m)
PROFILO_LUNGHEZZA_M = 3.0     # Lunghezza profilato in alluminio (3 metri)
VITONI_PER_PROFILO = 3        # 3 vitoni con staffa per ogni barra da 3 metri
# ==============================================================================

st.title("⚡ Scanner Automatico Disegni Fotovoltaici")
st.write("Carica il disegno dell'architetto per calcolare automaticamente il materiale necessario.")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("🖼️ Disegno Tetto")
    uploaded_file = st.file_uploader("Carica immagine (JPG / PNG)", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Disegno Tetto Caricato", use_container_width=True)
        analizza_btn = st.button("🔍 Scannerizza e Calcola Materiali", type="primary")

with col2:
    st.subheader("📊 Analisi Automatica e Distinta Materiali")
    
    if uploaded_file is not None and 'analizza_btn' in locals() and analizza_btn:
        if API_KEY == "INSERISCI_QUI_LA_TUA_API_KEY" or not API_KEY:
            st.error("⚠️ Sostituisci 'INSERISCI_QUI_LA_TUA_API_KEY' nel codice 'app.py' con la tua chiave reale di Google Gemini.")
        else:
            with st.spinner("Scannerizzazione e analisi dell'immagine in corso..."):
                try:
                    # Inizializzazione del client Google GenAI
                    client = genai.Client(api_key=API_KEY)

                    prompt = """
                    Analizza questa immagine di un layout di impianto fotovoltaico su tetto.
                    Rispondi ESCLUSIVAMENTE con un oggetto JSON valido, senza blocchi di testo o formattazione markdown, con questa struttura esatta:
                    {
                        "totale_pannelli": 18,
                        "file": [
                            {"numero_fila": 1, "pannelli_in_questa_fila": 6},
                            {"numero_fila": 2, "pannelli_in_questa_fila": 6},
                            {"numero_fila": 3, "pannelli_in_questa_fila": 6}
                        ]
                    }
                    Conta con precisione tutti i pannelli visibili nell'immagine e individua la suddivisione per ciascuna fila o gruppo continuo.
                    """

                    # Chiamata corretta tramite client.models.generate_content
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=[image, prompt]
                    )
                    
                    testo_risposta = response.text.strip()
                    
                    # Pulizia da eventuale markdown residuo
                    clean_json = testo_risposta.replace("```json", "").replace("```", "").strip()
                    dati = json.loads(clean_json)

                    totale_pannelli = dati["totale_pannelli"]
                    file_dettaglio = dati["file"]

                    # Calcoli dimensionali e materiali
                    metri_binario_totali = 0
                    morsetti_finali = 0
                    morsetti_centrali = 0

                    for fila in file_dettaglio:
                        n_p = fila["pannelli_in_questa_fila"]
                        lungh_fila = n_p * P_LARGHEZZA_M
                        metri_binario_totali += (lungh_fila * 2)  # 2 profili paralleli per ogni fila
                        
                        morsetti_finali += 4
                        morsetti_centrali += max(0, (n_p - 1) * 2)

                    num_profili_3m = math.ceil(metri_binario_totali / PROFILO_LUNGHEZZA_M)
                    totale_vitoni = num_profili_3m * VITONI_PER_PROFILO
                    potenza_totale_kwp = (totale_pannelli * P_POTENZA_WP) / 1000.0

                    # Visualizzazione Risultati
                    st.success("✅ Scannerizzazione completata con successo!")
                    
                    c1, c2 = st.columns(2)
                    c1.metric("Pannelli Rilevati", f"{totale_pannelli} pcs")
                    c2.metric("Potenza Impianto", f"{potenza_totale_kwp:.2f} kWp")

                    st.markdown("---")
                    st.markdown("### 🛠️ Lista Materiali da Ordinare / Portare sul Tetto")
                    st.write(f"- **Pannelli (ZS.455W - 113x176 cm):** {totale_pannelli} pezzi")
                    st.write(f"- **Sviluppo binari totale:** {metri_binario_totali:.2f} metri lineari")
                    st.write(f"- **Profili in alluminio (barre da 3m):** **{num_profili_3m} barre**")
                    st.write(f"- **Vitoni con staffe per profilo:** **{totale_vitoni} pezzi** (3 ogni barra da 3m)")
                    st.write(f"- **Morsetti Finali (End Clamps):** **{morsetti_finali} pezzi**")
                    st.write(f"- **Morsetti Centrali (Mid Clamps):** **{morsetti_centrali} pezzi**")

                except Exception as e:
                    st.error(f"Errore durante l'analisi dell'immagine: {e}")
