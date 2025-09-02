# app/Main.py

import streamlit as st
import sys
from pathlib import Path

script_path = Path(__file__).resolve()
project_root = script_path.parent.parent
sys.path.append(str(project_root))

# Now, use absolute imports from the project root
from data.data_functions.data_loader import load_processed_data
from app.utils.data_summarizer import display_executive_summary 
from app.themes import theming

# --- Page Configuration ---
st.set_page_config(
    layout="wide",
    page_title="Big Box Retail Analysis & Exploration",
    page_icon="🛒"
)
theming.altair_theme()

# --- Page Header ---
st.title("🛒 Big Box Retail Analysis & Exploration")
st.markdown("""
This dashboard provides insights into Big Box Sales performance to help us uncover insights that could lead to enhanced sales performance and store optimization. We'll start by looking at high level performance, understanding seasonal trends, and identifying a forecasting model that will help us understand how we're performing against actuals. Last, we'll segment stores, identifying top performers that can indicate how we should be optimizing our operations, and bottom performers that should be either improved or closed.
Use the global filters on the left to slice the data by date, store type, or individual stores. 
The analysis will dynamically update across all pages.
""")

# --- Data Loading ---
master_df = load_processed_data()

if master_df.empty:
    st.stop()

# --- Sidebar & Global Filters ---
st.sidebar.title("Global Filters ⚙️")

# Prepare filter options
min_date = master_df['Date'].min().date()
max_date = master_df['Date'].max().date()
all_store_types = sorted(master_df['Type'].unique())
all_stores = sorted(master_df['Store'].unique())

# Date Filter
st.sidebar.subheader("Date Range")
date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
    label_visibility="collapsed" # Hides the label to avoid redundancy with subheader
)

if len(date_range) != 2:
    st.sidebar.warning("Please select a valid start and end date.")
    st.stop()
start_date, end_date = date_range

# Store Filter using a checkbox
st.sidebar.subheader("Store Selection")
select_all_stores = st.sidebar.checkbox("Select All Stores", value=True)

if select_all_stores:
    selected_stores = all_stores
else:
    selected_stores = st.sidebar.multiselect(
        "Select Stores",
        options=all_stores,
        default=[all_stores[0]] if all_stores else []
    )

if not selected_stores:
    st.sidebar.warning("Please select at least one store.")
    st.stop()

# Store Type Filter using a checkbox
st.sidebar.subheader("Store Format Selection")
select_all_types = st.sidebar.checkbox("Select All Store Formats", value=True)

if select_all_types:
    selected_types = all_store_types
else:
    selected_types = st.sidebar.multiselect(
        "Select Store Format(s)",
        options=all_store_types,
        default=[all_store_types[0]] if all_store_types else []
    )

if not selected_types:
    st.sidebar.warning("Please select at least one store format.")
    st.stop()


# --- Data Filtering ---
query_parts = [
    "@start_date <= Date.dt.date <= @end_date",
    "Store in @selected_stores",
    "Type in @selected_types"
]

query_string = " & ".join(query_parts)
filtered_df = master_df.query(query_string)

# --- Storing Data in Session State for other pages ---
st.session_state['filtered_df'] = filtered_df
st.session_state['master_df'] = master_df

# --- Page Content ---
display_executive_summary(filtered_df)

with st.expander("Filtered Data Preview"):
    st.dataframe(filtered_df.head(100))
    st.info(f"Displaying {len(filtered_df):,} rows based on your filters.")