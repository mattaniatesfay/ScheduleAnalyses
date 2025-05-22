
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
from fpdf import FPDF

st.set_page_config(page_title="Rooster Dashboard", layout="wide")

st.info("ℹ️ Voor een correcte werking, zorg dat de dependencies uit 'requirements.txt' zijn geïnstalleerd:\n\n- streamlit\n- pandas\n- matplotlib\n- openpyxl - fpdf - seaborn")

st.title("🗓️ Roosteranalyse Dashboard 2.0")

uploaded_file = st.file_uploader("Upload een roosterbestand (Excel met tabbladen 'Autopilot' en 'All')", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file, sheet_name=None, engine='openpyxl')

    if 'Autopilot' in df and 'All' in df:
        autopilot = df['Autopilot']
        all_data = df['All']

# Kolommen opschonen
        autopilot.columns = autopilot.columns.str.strip()
        all_data.columns = all_data.columns.str.strip()

        # Vul kolom 'Gebouw' met 'Zaal' waar nodig
        if 'Gebouw' in all_data.columns and 'Zaal' in all_data.columns:
            all_data['Gebouw'] = all_data['Gebouw'].fillna(all_data['Zaal'])
        else:
            st.warning("Kolommen 'Gebouw' en/of 'Zaal' ontbreken in tabblad 'All'. Heatmapfunctie werkt mogelijk niet.")

        # DEBUG: Toon beschikbare kolommen en unieke gebouwen
        st.write("📋 Kolommen in 'All':", all_data.columns.tolist())
        if 'Gebouw' in all_data.columns:
            st.write("🏢 Unieke waarden in 'Gebouw':", all_data['Gebouw'].dropna().unique())

        # [ORIGINELE DASHBOARD-INHOUD COMPACT GEHOUDEN]

        # 🔥 Heatmap van activiteiten per gebouw
        st.subheader("🏢 Heatmap: activiteiten per gebouw per weekdag en tijdvak (alleen uit tabblad 'All')")

        if 'Gebouw' in all_data.columns and 'Tijdstip' in all_data.columns and 'Datum' in all_data.columns:

            gebouw_keuze = st.selectbox("Kies een gebouw", sorted(all_data['Gebouw'].dropna().unique()))

            gebouw_df = all_data[all_data['Gebouw'] == gebouw_keuze].copy()

            def tijdvak(tijd):
                if pd.isna(tijd):
                    return 'Overig'
                try:
                    uur, minuut = map(int, str(tijd).split(':'))
                    totaal_min = uur * 60 + minuut
                    if 525 <= totaal_min <= 630:
                        return '08:45-10:30'
                    elif 645 <= totaal_min <= 750:
                        return '10:45-12:30'
                    elif 765 <= totaal_min <= 870:
                        return '12:45-14:30'
                    elif 885 <= totaal_min <= 990:
                        return '14:45-16:30'
                    elif 1005 <= totaal_min <= 1110:
                        return '16:45-18:30'
                    else:
                        return 'Overig'
                except:
                    return 'Overig'

            gebouw_df['Weekdag'] = pd.to_datetime(gebouw_df['Datum'], errors='coerce').dt.day_name()
            gebouw_df['Tijdvak'] = gebouw_df['Tijdstip'].apply(tijdvak)

            heatmap_data = gebouw_df.groupby(['Weekdag', 'Tijdvak']).size().unstack(fill_value=0)

            weekvolgorde = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            heatmap_data = heatmap_data.reindex(weekvolgorde)

            st.subheader(f"📊 Heatmap voor gebouw: {gebouw_keuze}")
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.heatmap(heatmap_data, annot=True, fmt="d", cmap="YlGnBu", linewidths=0.5, ax=ax)
            ax.set_title(f"Aantal activiteiten per dag/tijdvak – {gebouw_keuze}")
            ax.set_ylabel("Weekdag")
            ax.set_xlabel("Tijdvak")
            st.pyplot(fig)

        else:
            st.warning("Zorg dat de kolommen 'Gebouw', 'Datum' en 'Tijdstip' aanwezig zijn in tabblad 'All'.")

    else:
        st.warning("Bestand moet de tabbladen 'Autopilot' en 'All' bevatten.")
