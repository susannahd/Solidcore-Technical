# pages/Executive_Summary.py

import streamlit as st
import pandas as pd
import altair as alt

def display_executive_summary(df: pd.DataFrame):
    st.title("Executive Summary 📊")
    st.markdown("""
    By looking at sales over time for the 45 stores in the file, we can see:

    - We have fairly steady weekly sales, aside from spikes around Black Friday and Christmas.
    - The majority of our stores are Type A, and our top performers by total sales are of Type A. The majority of our bottom performing stores are of Type C. We could further investigate here to normalize for sales by square foot.

    While our sales performance is strong, as a big box retailer we could be leaning more into Memorial and Labor Day, which are also popular shopping holidays by running promotions to improve traffic during these times. To increase sales, we should further examine store performance by type to evaluate which types are underperforming.
    """)
    if df.empty:
        st.warning("No data available for the selected filters. Please adjust the filters in the sidebar.")
        return

    # --- Key Performance Indicators (KPIs) ---
    st.subheader("Top-Line KPIs")
    
    ## NEW: Using st.container with a border for better visual separation
    with st.container(border=True):
        cols = st.columns(4) # NEW: Added a 4th column for efficiency metric
        total_sales = df['Weekly_Sales'].sum()
        num_stores = df['Store'].nunique()
        avg_weekly_sales_per_store = total_sales / num_stores if num_stores > 0 else 0
        
        ## NEW: Added Sales per Sq Ft as a key efficiency metric
        # We need to get the size for the selected stores
        store_sizes = df[['Store', 'Size']].drop_duplicates().set_index('Store')
        total_size = store_sizes.loc[df['Store'].unique()].sum().iloc[0]
        avg_sales_per_sqft = total_sales / total_size if total_size > 0 else 0

        cols[0].metric(label="Total Sales", value=f"${total_sales:,.0f}")
        cols[1].metric(label="Stores Analyzed", value=f"{num_stores}")
        cols[2].metric(label="Avg. Weekly Sales / Store", value=f"${avg_weekly_sales_per_store:,.0f}")
        cols[3].metric(label="Avg. Sales / Sq. Ft.", value=f"${avg_sales_per_sqft:,.2f}")

    st.divider()

    # --- Visualizations ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Overall Sales Trend")
        sales_over_time = df.groupby('Date')['Weekly_Sales'].sum().reset_index()
        line_chart = alt.Chart(sales_over_time, title="Total Weekly Sales Over Time").mark_area().encode(
            x=alt.X('Date:T', title='Date'),
            y=alt.Y('Weekly_Sales:Q', title='Total Weekly Sales', axis=alt.Axis(format='$,s')),
            tooltip=['Date:T', alt.Tooltip('Weekly_Sales:Q', title='Total Sales', format='$,.0f')]
        ).interactive()
        st.altair_chart(line_chart, use_container_width=True)

    with col2:
        st.subheader("Sales by Store Type")
        sales_by_type = df.groupby('Type')['Weekly_Sales'].sum().sort_values(ascending=False).reset_index()
        bar_chart = alt.Chart(sales_by_type, title="Total Sales Contribution by Store Type").mark_bar().encode(
            x=alt.X('Weekly_Sales:Q', title='Total Sales', axis=alt.Axis(format='$,s')),
            y=alt.Y('Type:N', title='Store Type', sort='-x'),
            color=alt.Color('Type:N', legend=None),
            tooltip=['Type', alt.Tooltip('Weekly_Sales', title='Total Sales', format='$,.0f')]
        )
        st.altair_chart(bar_chart, use_container_width=True)

    st.subheader("Store Performance Ranking")
    store_sales = df.groupby(['Store', 'Type'])['Weekly_Sales'].sum().sort_values(ascending=False).reset_index()
    
    performance_choice = st.radio(
        "View Performance:", ["Top 10 Stores", "Bottom 10 Stores"],
        horizontal=True, label_visibility="collapsed"
    )
    data_to_show = store_sales.head(10) if performance_choice == "Top 10 Stores" else store_sales.tail(10)
    sort_order = '-x' if performance_choice == "Top 10 Stores" else 'x'

    store_perf_chart = alt.Chart(data_to_show).mark_bar().encode(
        x=alt.X('Weekly_Sales:Q', title='Total Sales', axis=alt.Axis(format='$,s')),
        y=alt.Y('Store:N', title='Store ID', sort=sort_order),
        color=alt.Color('Type:N', title='Store Type'),
        tooltip=['Store', 'Type', alt.Tooltip('Weekly_Sales', title='Total Sales', format='$,.0f')]
    ).properties(title=f"{performance_choice} by Total Sales")
    st.altair_chart(store_perf_chart, use_container_width=True)
