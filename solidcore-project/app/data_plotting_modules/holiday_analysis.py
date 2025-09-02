# plotting_modules/holiday_impact.py

import streamlit as st
import pandas as pd
import altair as alt

# --- Chart Theming and Configuration (Consistent with our other plots) ---
# Note: In a real multi-page app, you would define this in a central
# utility file (e.g., `style_utils.py`) and import it to avoid repetition.
def chart_theme():
    """Creates a custom Altair theme for a professional and consistent look."""
    font = "Arial"
    primary_color = "#1f77b4" # Muted blue
    secondary_color = "#ff7f0e" # Safety orange
    
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
            "point": {"filled": True, "size": 60},
            "circle": {"filled": True, "size": 60},
            "line": {"color": primary_color, "strokeWidth": 2.5}, # Use primary for base lines
            "rule": {"color": secondary_color} # Use secondary for annotations
        }
    }

# Register and enable the custom theme
alt.themes.register("custom_theme", chart_theme) # pyright: ignore[reportArgumentType]
alt.themes.enable("custom_theme")


def display_holiday_impact(df: pd.DataFrame):
    """
    Renders an enhanced analysis of holiday week sales impact.

    Args:
        df (pd.DataFrame): Input dataframe. Must include 'IsHoliday', 
                           'Weekly_Sales', and 'Date' columns.
    """
    st.subheader("Holiday Sales Performance")
    st.markdown(
        "Holidays drive 7.13% higher sales on average, even before factoring in pre-Christmas shopping behavior - for forecasting, we'd need to engineer a feature for the weeks leading up to Christmas since people tend to shop beforehand."
    )

    col1, col2 = st.columns([1, 2]) # Keep the layout ratio
    with col1:
        st.markdown("##### Average Sales Comparison")

        # --- Data Preparation ---
        holiday_impact_df = df.groupby('IsHoliday')['Weekly_Sales'].mean().reset_index()
        holiday_impact_df['Week Type'] = holiday_impact_df['IsHoliday'].apply(
            lambda x: 'Holiday Week' if x else 'Non-Holiday Week'
        )
        
        # --- Chart Enhancement 1: Add Data Labels and Improve Aesthetics ---
        bar_chart = alt.Chart(holiday_impact_df).mark_bar(cornerRadius=5).encode(
            x=alt.X('Week Type', title=None, sort=['Non-Holiday Week', 'Holiday Week']),
            y=alt.Y('Weekly_Sales', title='Average Weekly Sales', axis=alt.Axis(format='$,s')),
            color=alt.Color(
                'Week Type', 
                legend=None,
                # Use our theme's secondary color to highlight the holiday bar
                scale=alt.Scale(domain=['Non-Holiday Week', 'Holiday Week'], range=['#1f77b4', '#ff7f0e'])
            ),
            tooltip=[
                'Week Type', 
                alt.Tooltip('Weekly_Sales', title='Avg. Sales', format='$,.0f')
            ]
        ).properties(height=300)

        # Add text labels on top of the bars for immediate clarity
        text_labels = bar_chart.mark_text(
            align='center',
            baseline='bottom',
            dy=-5, # Nudge text up
            fontSize=14,
            fontWeight='bold'
        ).encode(
            text=alt.Text('Weekly_Sales:Q', format='$,.0f'),
            color=alt.value("#333333") # Explicitly set text color
        )
        
        st.altair_chart(bar_chart + text_labels, use_container_width=True)

        # --- UX Enhancement: Use st.metric for a clear KPI callout ---
        try:
            non_holiday_avg = holiday_impact_df.loc[holiday_impact_df['Week Type'] == 'Non-Holiday Week', 'Weekly_Sales'].iloc[0]
            holiday_avg = holiday_impact_df.loc[holiday_impact_df['Week Type'] == 'Holiday Week', 'Weekly_Sales'].iloc[0]
            delta = ((holiday_avg - non_holiday_avg) / non_holiday_avg) * 100
            st.metric(
                label="Holiday Week Uplift",
                value=f"${holiday_avg:,.0f}",
                delta=f"{delta:.2f}% vs. Non-Holiday Avg."
            )
        except IndexError:
            st.info("Data for both holiday and non-holiday weeks is needed to calculate uplift.")


    with col2:
        st.markdown("##### Sales Timeline with Holiday Markers")
        
        # --- Data Preparation ---
        sales_over_time = df.groupby('Date')['Weekly_Sales'].sum().reset_index()
        holiday_data = sales_over_time[sales_over_time['Date'].isin(df[df['IsHoliday']]['Date'])]

        # --- Chart Enhancement 2: More Informative Holiday Markers ---
        # Base line chart
        base_line = alt.Chart(sales_over_time).mark_line(strokeWidth=2).encode(
            x=alt.X('Date:T', title='Date'),
            y=alt.Y('Weekly_Sales:Q', title='Total Weekly Sales', axis=alt.Axis(format='$,s')),
            tooltip=[
                alt.Tooltip('Date:T'), 
                alt.Tooltip('Weekly_Sales:Q', title='Total Sales', format='$,.0f')
            ]
        ).properties(height=300).interactive()

        # Checkbox with a more intuitive label
        show_holidays = st.checkbox("Highlight holidays on the timeline", value=True, key='holiday_marker_checkbox')
        
        if show_holidays and not holiday_data.empty:
            # Create points for holidays instead of rules for better tooltips
            holiday_points = alt.Chart(holiday_data).mark_point(
                size=100,
                color="#e45756", # A distinct red for attention
                filled=True,
                opacity=1.0
            ).encode(
                x='Date:T',
                y='Weekly_Sales:Q',
                tooltip=[
                    alt.Tooltip('Date:T', title='Holiday Date'),
                    alt.Tooltip('Weekly_Sales:Q', title='Sales on Holiday Week', format='$,.0f')
                ]
            )
            # Layer the points on top of the line
            final_chart = base_line + holiday_points
            st.altair_chart(final_chart, use_container_width=True)
            st.caption("Hover over the red markers to see sales data for specific holiday weeks.")
        else:
            # Just show the base line chart
            st.altair_chart(base_line, use_container_width=True)
            if show_holidays and holiday_data.empty:
                st.caption("No holiday weeks found in the current data selection.")
