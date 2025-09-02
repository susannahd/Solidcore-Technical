# pages/Sales_Analysis_and_Forecasting.py

import streamlit as st
import pandas as pd
import altair as alt

# Import the display functions from our modules
from data_plotting_modules.holiday_analysis import display_holiday_impact
from data_plotting_modules.economic_analysis import display_economic_drivers
from data_plotting_modules.seasonality_analysis import display_seasonality

## NEW: A simple forecasting function
def generate_forecast(df: pd.DataFrame):
    """Generates a simple moving average forecast."""
    st.subheader("Sales Forecast (Illustrative)")
    st.markdown("""
    This chart illustrates a simple forecast using a 4-week moving average. With more time, we'd approach a model to forecast weekly sales using the following methodology: To create a model that forecasts weekly sales, we'd take the following approach:
1. Feature Engineering: Add leading variables to the model to capture the week or two prior to Christmas - for example, two_weeks_from_christmas, one_week_from_christmas . Christmas is our biggest sales time, but since shoppers purchase before, we're not accurately capturing that. We could repeat this process for other holidays, though this is the one that has the most pre-shopping behavior. We can eliminate Christmas from the IsHoliday flag as well. 
2. Training: We'd train on 24 months or about 75% of our existing data, validate which model works best on ~15% of our data, and test on our holdout group of ~15% of our data. 
3. Validation: We'd test different models on our validation set - looking at XGBoost, linear regression, random forest to see which performs best. I lean XGBoost as a default. We'd look at Weighted Mean Average Percent Error (WMAPE) and RMSE (Root Mean Squared Error), looking for which model has the lowest RMSE and a WMAPE between 10-20% (or lower if it's possible without overfitting!)
4. Testing: Once we've selected the best model using WMAPE and RMSE, we'd test on our holdout set and see how it performs using RMSE and WMAPE. If it performs similarly to our validation set, we can be more confident in its performance. If it performs significantly worse, we may have overfit to our validation set and need to revisit our model selection.
    """)
    
    sales_over_time = df.groupby('Date')['Weekly_Sales'].sum().reset_index().set_index('Date')
    
    # Calculate moving average
    sales_over_time['Forecast'] = sales_over_time['Weekly_Sales'].rolling(4, min_periods=1).mean().shift(1)
    
    # Plotting
    base = alt.Chart(sales_over_time.reset_index()).encode(x='Date:T')
    
    actual_line = base.mark_line(opacity=0.8).encode(
        y=alt.Y('Weekly_Sales:Q', title='Weekly Sales'),
        tooltip=[alt.Tooltip('Weekly_Sales', format='$,.0f', title='Actual Sales')]
    ).interactive()
    
    forecast_line = base.mark_line(strokeDash=[5,5], color='orange').encode(
        y=alt.Y('Forecast:Q'),
        tooltip=[alt.Tooltip('Forecast', format='$,.0f', title='Forecasted Sales')]
    )
    
    st.altair_chart((actual_line + forecast_line).properties(title="Actual Sales vs. 4-Week Moving Average Forecast"), use_container_width=True)


st.title("1. Sales Analysis & Forecasting 📈")

if 'filtered_df' not in st.session_state or st.session_state.filtered_df.empty:
    st.warning("Please select filters on the main page to see the data.")
    st.stop()

df = st.session_state.filtered_df

## NEW: Using tabs for better organization
tab1, tab2, tab3, tab4 = st.tabs(["1a) Seasonality", "1a) Holiday Impact", "1a) Economic Drivers", "1b) Forecasting"])


with tab1:
    display_seasonality(df)

with tab2:
    display_holiday_impact(df)

with tab3:
    display_economic_drivers(df)

with tab4:
    generate_forecast(df)
