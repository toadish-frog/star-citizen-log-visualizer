import streamlit as st
import pandas as pd
from dataclasses import asdict

# Import parsing and analysis functions from other modules
from log_parser import (
    parse_session_metadata,
    parse_death_events,
    parse_travel_events,
    SessionMetadata
)
from analysis import (
    calculate_total_deaths,
    get_log_session_duration
)

def convert_df_to_csv(df: pd.DataFrame):
    """Utility to convert a DataFrame to a CSV string for download."""
    return df.to_csv(index=False).encode('utf-8')

# --- Streamlit App UI ---

st.set_page_config(page_title="Star Citizen Log Visualizer", page_icon="🥹", layout="wide")

st.title("🚀 Star Citizen Log Visualizer")
st.write(
    "Upload your `Game.log` file to get a summary of your play session, "
    "including KPIs, death events, and quantum travel history."
)

uploaded_file = st.file_uploader("Choose a Game.log file", type="log")

if uploaded_file is not None:
    # Read the content of the uploaded file
    try:
        log_content = uploaded_file.getvalue().decode("utf-8")
    except Exception as e:
        st.error(f"Error reading or decoding file: {e}")
        st.stop()

    with st.spinner('Analyzing log file... This may take a moment.'):
        # --- Parsing and Analysis ---
        session_metadata = parse_session_metadata(log_content)
        death_events = parse_death_events(log_content, session_metadata.user.actor_name)
        travel_events = parse_travel_events(log_content)

        session_duration = get_log_session_duration(log_content)
        total_deaths = calculate_total_deaths(death_events)

    st.success("Analysis complete!")

    # --- Display KPIs (Wow Numbers) ---
    st.header("Session KPIs")
    col1, col2 = st.columns(2)
    col1.metric("Total Session Time", session_duration)
    col2.metric("Total Death Count", total_deaths)
    
    st.markdown("---")

    # --- Display DataFrames and CSV Download ---
    st.header("Detailed Event Logs")

    # Deaths
    if death_events:
        st.subheader("💥 Death Events")
        deaths_df = pd.DataFrame([asdict(e) for e in death_events])
        st.dataframe(deaths_df)
        st.download_button(
            label="Download Death Events as CSV",
            data=convert_df_to_csv(deaths_df),
            file_name="death_events.csv",
            mime="text/csv",
        )
    else:
        st.info("No death events were found in this log.")

    # Travel
    if travel_events:
        st.subheader("🌌 Quantum Travel History")
        travel_df = pd.DataFrame([asdict(e) for e in travel_events])
        st.dataframe(travel_df)
        st.download_button(
            label="Download Travel History as CSV",
            data=convert_df_to_csv(travel_df),
            file_name="travel_history.csv",
            mime="text/csv",
        )
    else:
        st.info("No quantum travel events were found in this log.")

    # --- Display Session Metadata ---
    with st.expander("Show Session & System Metadata"):
        st.json(asdict(session_metadata))
