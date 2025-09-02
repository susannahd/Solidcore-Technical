# data/data_functions/data_loader.py

import streamlit as st
import pandas as pd
from pathlib import Path


@st.cache_data
def load_processed_data() -> pd.DataFrame:
    # <<< FIX: Correctly navigate to the project root (three levels up) and then to the data file.
    PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
    DATA_PATH = PROJECT_ROOT / "data/processed_data/master_data.csv"
    
    if not DATA_PATH.exists():
        st.error(
            "Fatal Error: The master data file was not found. "
            "Please prepare the data by running this command in your terminal from the project root:"
        )
        # Note: You might want to update this path if your script is actually in data/data_functions
        st.code("python data/data_functions/prepare_master_data.py")
        return pd.DataFrame()
        
    try:
        df = pd.read_csv(DATA_PATH, parse_dates=['Date'])
        return df
    except Exception as e:
        st.error(f"An error occurred while loading the processed data: {e}")
        return pd.DataFrame()
