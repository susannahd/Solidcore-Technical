# plotting_modules/economic_analysis.py

import streamlit as st
import pandas as pd
import altair as alt

# --- Chart Theming and Configuration) ---
def chart_theme():
    font = "Arial"
    primary_color = "#1f77b4" # Muted blue
    secondary_color = "#ff7f0e" # Safety orange
    
    return {
        "config": {
            "title": {
                "fontSize": 18,
                "font": font,
                "anchor": "start", # Left-align titles
                "color": "#333333"
            },
            "axis": {
                "labelFont": font,
                "labelFontSize": 12,
                "titleFont": font,
                "titleFontSize": 14,
                "titlePadding": 10,
                "gridColor": "#e6e6e6"
            },
            "legend": {
                "labelFont": font,
                "labelFontSize": 12,
                "titleFont": font,
                "titleFontSize": 14,
            },
            "view": {
                "stroke": "transparent", # No border around the chart
            },
            "mark": {
                "color": primary_color,
                "tooltip": True # Enable tooltips by default
            },
            "point": {
                "filled": True,
                "size": 60 # Slightly larger points
            },
            "circle": {
                "filled": True,
                "size": 60
            },
            "line": {
                "color": secondary_color,
                "strokeWidth": 2.5
            }
        }
    }

# Register the custom theme so all charts use it
alt.themes.register("custom_theme", chart_theme) # pyright: ignore[reportArgumentType]
alt.themes.enable("custom_theme")


def display_economic_drivers(df: pd.DataFrame):
    st.subheader("Economic Driver Analysis")
    st.markdown(
        "We can use the controls below to investigate trends between weekly sales and other numeric data, such as temperature and economic indicators. We see that there's not a strong aggregate correlation between weekly sales and any variables, aside from size of the store. In a deeper analysis, we could break this down to explore whether correlation exists at a regional level, by getting additional regional data such as zip, city, state, or store type. In the meantime, there's a multi-select dropdown, if someone with more intimate knowledge of the data knew that for example, stores 1-10 were in the Midwest, stores 11-20 in the Southeast, etc."
    )

    # --- Define Constants for Clarity ---
    ECONOMIC_FACTORS = ['Temperature', 'Fuel_Price', 'CPI', 'Unemployment']
    NUMERIC_COLS_FOR_CORR = ['Weekly_Sales', 'Temperature', 'Fuel_Price', 'CPI', 'Unemployment', 'Size']

    col1, col2 = st.columns([2, 1]) # Give more space to the primary scatter plot

    with col2:
        st.markdown("##### Sales vs. Selected Economic Factor")
        
        # --- UI Improvement: Place selectbox in a more logical flow ---
        selected_factor = st.selectbox(
            "Choose an economic factor to plot against sales:",
            options=ECONOMIC_FACTORS,
            index=1 # Default to Fuel_Price, often a good starting point
        )

        # --- Chart Enhancement 1: Add a Regression Line for Interpretability ---
        base = alt.Chart(df.sample(n=1000, replace=True) if len(df) > 1000 else df).encode(
            x=alt.X(f'{selected_factor}:Q', title=selected_factor, scale=alt.Scale(zero=False)),
            y=alt.Y('Weekly_Sales:Q', title='Weekly Sales', axis=alt.Axis(format='$,s'), scale=alt.Scale(zero=False))
        ).properties(
            title=f"Weekly Sales vs. {selected_factor}"
        )
        
        # Create the scatter plot layer
        scatter_points = base.mark_point(opacity=0.4, filled=True).encode(
            tooltip=['Date', 'Store', 'Weekly_Sales', selected_factor]
        ).interactive() # Make the points interactive (zoom/pan)

        # Create the regression line layer
        regression_line = base.transform_regression(
            on=selected_factor,
            regression='Weekly_Sales'
        ).mark_line(strokeDash=[5,5]) # Dashed line for visual distinction

        # Layer the charts together
        layered_chart = scatter_points + regression_line
        
        st.altair_chart(layered_chart, use_container_width=True)
        st.info(
            f"**Analysis Tip:** The dashed line shows the overall trend. "
            f"A steep line indicates a stronger relationship between **{selected_factor}** and sales. "
            "A flat line suggests little to no relationship."
        )

    with col1:
        st.markdown("##### Correlation Matrix")
        
        corr_df = df[NUMERIC_COLS_FOR_CORR].corr().stack().reset_index().rename(
            columns={0: 'correlation', 'level_0': 'variable', 'level_1': 'variable2'}
        )
        
        # --- Chart Enhancement 2: Add Correlation Values to the Heatmap ---
        base_heatmap = alt.Chart(corr_df).encode(
            x=alt.X('variable:O', title=None, sort=NUMERIC_COLS_FOR_CORR),
            y=alt.Y('variable2:O', title=None, sort=NUMERIC_COLS_FOR_CORR),
            tooltip=[
                alt.Tooltip('variable:N', title='Variable 1'),
                alt.Tooltip('variable2:N', title='Variable 2'),
                alt.Tooltip('correlation:Q', title='Correlation', format='.2f')
            ]
        ).properties(
            title="Key Variable Correlations"
        )
        
        # The colored rectangles
        heatmap_rects = base_heatmap.mark_rect().encode(
            color=alt.Color('correlation:Q',
                scale=alt.Scale(scheme='redblue', domain=(-1, 1)),
                legend=alt.Legend(title="Correlation", orient="top")
            )
        )
        
        # The text labels on top of the rectangles
        heatmap_text = base_heatmap.mark_text(size=10).encode(
            text=alt.Text('correlation:Q', format='.2f'),
            color=alt.condition(
                # Make text white on dark cells for readability
                alt.datum.correlation > 0.5 or alt.datum.correlation < -0.5,
                alt.value('white'),
                alt.value('black')
            )
        )

        # Layer the heatmap and text
        full_heatmap = heatmap_rects + heatmap_text

        st.altair_chart(full_heatmap, use_container_width=True)
        st.caption("A visual guide to how variables move together. Red indicates a positive correlation, blue a negative one.")
