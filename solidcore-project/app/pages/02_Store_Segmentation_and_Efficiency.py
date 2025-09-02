# pages/Store_Segmentation_and_Efficiency.py

import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

@st.cache_data
#Perform k-means clustering on selected data
def get_store_clusters(df: pd.DataFrame, k: int):
    if df.empty or 'Store' not in df.columns:
        return pd.DataFrame(), None

    # Group by all relevant descriptive columns to keep them in the output
    store_agg = df.groupby(['Store', 'Type', 'Size']).agg(
        Avg_Weekly_Sales=('Weekly_Sales', 'mean'),
        Sales_per_sq_ft=('Sales_per_sq_ft', 'mean')
    ).reset_index()
    
    if len(store_agg) < k:
        return store_agg, None

    # Features for clustering remain the core numerical ones
    features = store_agg[['Size', 'Avg_Weekly_Sales']]
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)

    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    store_agg['Cluster'] = kmeans.fit_predict(scaled_features)
    
    centroids_scaled = kmeans.cluster_centers_
    centroids = scaler.inverse_transform(centroids_scaled)
    
    return store_agg, centroids

def assign_cluster_labels(centroids: np.ndarray) -> dict:
    """Assigns descriptive labels to clusters based on their centroid values."""
    if centroids is None:
        return {}
        
    median_size = np.median(centroids[:, 0])
    median_sales = np.median(centroids[:, 1])
    
    labels = {}
    for i, (size, sales) in enumerate(centroids):
        size_label = "Large" if size >= median_size else "Small"
        sales_label = "High-Performing" if sales >= median_sales else "Under-Performing"
        
        if size_label == "Large" and sales_label == "High-Performing":
            label = "🏆 Large High-Performers"
        elif size_label == "Small" and sales_label == "High-Performing":
            label = "🚀 Efficient Powerhouses"
        elif size_label == "Large" and sales_label == "Under-Performing":
            label = "⚠️ Flagging Giants"
        else: # Small and Under-Performing
            label = "⚠️ Flagging Small Stores"
        
        labels[i] = f"Segment {i}: {label}"
        
    return labels

def display_segment_details(clustered_df, cluster_summary, overall_metrics):
    st.subheader("Segment Deep Dive")
    st.markdown("Segment the stores based on size, type, and regional characteristics. Analyze sales performance across segments and identify factors that influence sales outcomes.")

    for _, row in cluster_summary.iterrows():
        segment_name = row['Segment']
        
        with st.expander(f"**{segment_name}** ({row['Num_Stores']} stores)"):
            
            delta_sales = (row['Avg_Sales'] - overall_metrics['avg_sales']) / overall_metrics['avg_sales'] if overall_metrics['avg_sales'] else 0
            delta_size = (row['Avg_Size'] - overall_metrics['avg_size']) / overall_metrics['avg_size'] if overall_metrics['avg_size'] else 0
            delta_efficiency = (row['Sales_per_SqFt'] - overall_metrics['avg_efficiency']) / overall_metrics['avg_efficiency'] if overall_metrics['avg_efficiency'] else 0

            col1, col2, col3 = st.columns(3)
            col1.metric(label="Avg. Weekly Sales", value=f"${row['Avg_Sales']:,.0f}", delta=f"{delta_sales:.1%}", help="Compared to the average of all selected stores.")
            col2.metric(label="Avg. Store Size", value=f"{row['Avg_Size']:,.0f} sq.ft.", delta=f"{delta_size:.1%}", help="Compared to the average of all selected stores.")
            col3.metric(label="Sales Efficiency", value=f"${row['Sales_per_SqFt']:.2f} / sq.ft.", delta=f"{delta_efficiency:.1%}", help="Sales per square foot, compared to the average of all selected stores.")
            
            st.divider()

            if "Large High-Performers" in segment_name:
                st.info(f"**Strategic Takeaway:** These stores are your top performers, significantly larger and higher-grossing than average. Focus on maintaining their success and using them as models for training and best practices.")
            elif "Efficient Powerhouses" in segment_name:
                st.success(f"**Strategic Takeaway:** These stores are punching well above their weight, achieving high sales in a smaller footprint. Analyze their operational secrets to replicate their success elsewhere.")
            elif "Flagging Giants" in segment_name:
                st.warning(f"**Strategic Takeaway:** These large stores are not realizing their sales potential. They represent a major opportunity for growth. Investigate operational inefficiencies or local competition.")
            elif "Flagging Small" in segment_name:
                st.write(f"**Strategic Takeaway:** These are standard smaller stores with performance near the average. Focus on optimizing inventory for local demand and ensuring operational costs are low.")

            st.markdown("##### Stores in this Segment:")
            stores_in_segment = clustered_df[clustered_df['Segment'] == segment_name][
                ['Size', 'Avg_Weekly_Sales', 'Sales_per_sq_ft']
            ].sort_values('Avg_Weekly_Sales', ascending=False).reset_index(drop=True)
            
            st.dataframe(stores_in_segment, use_container_width=True)

def display_store_segmentation(df: pd.DataFrame):
    st.title("2. Store Segmentation & Efficiency 🏬")
    st.markdown("""
    This lets us cluster stores into distinct profiles based on their size and average sales to identify patterns. I'd recommend using 3 clusters, but this lets us explore alternative solutions as well.
    """)

    num_unique_stores = df['Store'].nunique()
    if num_unique_stores < 3:
        st.warning("Please select at least 3 stores to perform a meaningful segmentation analysis.")
        st.stop()
        
    max_clusters = min(num_unique_stores - 1, 8)
    num_clusters = st.slider(
        "Select Number of Segments (Clusters)",
        min_value=2,
        max_value=max_clusters,
        value=min(4, max_clusters),
        help="Choose how many distinct groups of stores you want to identify."
    )

    clustered_df, centroids = get_store_clusters(df, num_clusters)

    if clustered_df.empty or centroids is None:
        st.info("Not enough unique stores in the filtered data to create clusters.")
        return

    cluster_labels = assign_cluster_labels(centroids)
    clustered_df['Segment'] = clustered_df['Cluster'].map(cluster_labels)

    st.subheader("Store Segment Scatter Plot")
    scatter_plot = alt.Chart(clustered_df).mark_circle(size=150, opacity=0.8).encode(
        x=alt.X('Size:Q', title='Store Size (Sq. Ft.)', axis=alt.Axis(format=',d')),
        y=alt.Y('Avg_Weekly_Sales:Q', title='Average Weekly Sales', axis=alt.Axis(format='$,s')),
        color=alt.Color('Segment:N', title='Segment'),
        tooltip=[
            alt.Tooltip('Size:Q', title='Size', format=','),
            alt.Tooltip('Avg_Weekly_Sales:Q', title='Avg. Sales', format='$,.0f'),
            alt.Tooltip('Segment:N', title='Segment')
        ]
    ).interactive()

    regression_line = scatter_plot.transform_regression(
        'Size', 'Avg_Weekly_Sales'
    ).mark_line(color='grey', strokeDash=[3,3], opacity=0.7)

    st.altair_chart(scatter_plot + regression_line, use_container_width=True)
    st.caption("Dashed line shows the average expected sales for a given store size. Stores far above the line are highly efficient.")

    st.subheader("Segment Profiles at a Glance")
    
    cluster_summary = clustered_df.groupby('Segment').agg(
        Num_Stores=('Store', 'count'),
        Avg_Size=('Size', 'mean'),
        Avg_Sales=('Avg_Weekly_Sales', 'mean'),
        Sales_per_SqFt=('Sales_per_sq_ft', 'mean')
    ).reset_index().sort_values('Avg_Sales', ascending=False)

    st.dataframe(
        cluster_summary,
        column_config={
            "Segment": "Identified Segment",
            "Num_Stores": "Number of Stores",
            "Avg_Size": st.column_config.NumberColumn("Avg. Size", format="%,d sq.ft."),
            "Avg_Sales": st.column_config.NumberColumn("Avg. Weekly Sales", format="$%.0f"),
            "Sales_per_SqFt": st.column_config.NumberColumn("Avg. Sales/Sq.Ft.", format="$%.2f")
        },
        use_container_width=True, hide_index=True
    )

    overall_metrics = {
        'avg_sales': df['Weekly_Sales'].mean(),
        'avg_size': df[['Store', 'Size']].drop_duplicates()['Size'].mean(),
        'avg_efficiency': df['Sales_per_sq_ft'].mean()
    }
    
    display_segment_details(clustered_df, cluster_summary, overall_metrics)


# --- Main execution block for the page ---
if 'filtered_df' in st.session_state and not st.session_state.filtered_df.empty:
    filtered_stores_df = st.session_state['filtered_df']
    display_store_segmentation(filtered_stores_df)
else:
    st.title("🏬 2. Store Segmentation & Efficiency")
    st.warning("Please apply filters on the main page to see the data for this analysis.")
    st.stop()
