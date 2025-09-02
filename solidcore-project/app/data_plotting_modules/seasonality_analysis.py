# plotting_modules/seasonality.py

import streamlit as st
import pandas as pd
import altair as alt
import calendar # We'll use this for month names

# --- Chart Theming and Configuration (To be imported from a central utils file) ---
def chart_theme():
    font = "Arial"
    primary_color = "#1f77b4"
    secondary_color = "#ff7f0e"
    
    return {
        "config": {
            "title": {"fontSize": 18, "font": font, "anchor": "start", "color": "#333333"},
            "axis": {
                "labelFont": font, "labelFontSize": 12, "titleFont": font,
                "titleFontSize": 14, "titlePadding": 10, "gridColor": "#e6e6e6"
            },
            "legend": {"labelFont": font, "labelFontSize": 12, "titleFont": font, "titleFontSize": 14},
            "view": {"stroke": "transparent"},
            "mark": {"color": primary_color, "tooltip": True},
            "area": {"color": primary_color, "opacity": 0.4}, # Specific theme for area charts
            "line": {"color": primary_color, "strokeWidth": 2.5},
            "point": {"filled": True, "size": 60}
        }
    }

# Register and enable the custom theme
alt.themes.register("custom_theme", chart_theme) # pyright: ignore[reportArgumentType]
alt.themes.enable("custom_theme")


def display_seasonality(df: pd.DataFrame):
    st.subheader("Annual Sales Patterns")
    st.markdown("Q4 is our peak sales quarter, particularly due to Black Friday and Christmas shopping.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("##### Monthly Sales Trend")

        # --- Data Prep: Add human-readable month names for clarity ---
        monthly_sales = df.groupby('Month')['Weekly_Sales'].mean().reset_index()
        # Create a sorted list of month abbreviations
        month_abbr = [calendar.month_abbr[i] for i in range(1, 13)]
        monthly_sales['MonthName'] = monthly_sales['Month'].apply(lambda m: calendar.month_abbr[m])

        # --- Chart Enhancement 1: Use an Area Chart for a better sense of volume ---
        area_chart = alt.Chart(monthly_sales).mark_area(
            line={'color': '#1f77b4'}, # Provide the raw value directly
            point=alt.OverlayMarkDef(color="#1f77b4", size=50)
        ).encode(
            x=alt.X('MonthName:O', title='Month', sort=month_abbr), # Sort correctly
            y=alt.Y('Weekly_Sales:Q', title='Average Weekly Sales', axis=alt.Axis(format='$,s')),
            tooltip=[
                alt.Tooltip('MonthName', title='Month'),
                alt.Tooltip('Weekly_Sales', title='Avg. Sales', format='$,.0f')
            ]
        ).properties(
            title="Average Sales Volume by Month"
        )
        st.altair_chart(area_chart, use_container_width=True)
        st.caption("The shaded area helps visualize the overall sales volume across the year, highlighting the major end-of-year peak.")


    with col2:
        st.markdown("##### Weekly Sales Hotspots")
        
        # --- Data Prep: Identify the top 3 weeks to highlight them ---
        weekly_sales = df.groupby('WeekOfYear')['Weekly_Sales'].mean().reset_index()
        top_3_weeks = weekly_sales.nlargest(3, 'Weekly_Sales')
        
        # --- Chart Enhancement 2: Highlight Key Weeks for Immediate Insight ---
        base_line = alt.Chart(weekly_sales).mark_line(
            point=False, # We'll add points separately
            color="#a9a9a9" # Mute the base line to make highlights pop
        ).encode(
            x=alt.X('WeekOfYear:Q', title='Week of Year'), # Use Quantitative for a continuous axis
            y=alt.Y('Weekly_Sales:Q', title='Average Weekly Sales', axis=alt.Axis(format='$,s')),
            tooltip=[
                alt.Tooltip('WeekOfYear', title='Week'),
                alt.Tooltip('Weekly_Sales', title='Avg. Sales', format='$,.0f')
            ]
        ).properties(
            title="Top-Performing Weeks of the Year"
        )
        
        # Create highlight points for the top 3 weeks
        highlight_points = alt.Chart(top_3_weeks).mark_point(
            size=150,
            filled=True,
            color='fuchsia' # Use our theme's secondary color
        ).encode(
            x=alt.X('WeekOfYear:Q'),
            y=alt.Y('Weekly_Sales:Q'),
            tooltip=[
                alt.Tooltip('WeekOfYear', title='Peak Week'),
                alt.Tooltip('Weekly_Sales', title='Avg. Sales', format='$,.0f')
            ]
        )
        
        # Layer the charts
        final_chart = (base_line + highlight_points).interactive()
        
        st.altair_chart(final_chart, use_container_width=True)
        st.info(
            f"**Key Insight:** The standout sales weeks are **Week "
            f"{top_3_weeks.iloc[0]['WeekOfYear']}** (likely Christmas), "
            f"**Week {top_3_weeks.iloc[1]['WeekOfYear']}** (likely Thanksgiving), "
            f"and **Week {top_3_weeks.iloc[2]['WeekOfYear']}**. These are critical periods for revenue."
        )
