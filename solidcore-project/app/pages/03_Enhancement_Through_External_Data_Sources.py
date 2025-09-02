# pages/Store_Segmentation_and_Efficiency.py
import streamlit as st
import sys
from pathlib import Path

script_path = Path(__file__).resolve()
project_root = script_path.parent.parent
sys.path.append(str(project_root))

# Now, use absolute imports from the project root
from app.themes import theming


# --- Page Configuration ---
st.set_page_config(
    layout="wide",
    page_title="03. Enhancement Through External Data Sources",
    page_icon="🛒"
)
theming.altair_theme()

# --- Page Header ---
st.title("03. Enhancement Through External Data Sources")
st.markdown("""
#### Our forecasts and segmentation could benefit from additional data sources. The prompt specifically mentioned external data sources, which I interpret as publicly available and not available in our internal, first party data. However, our predictive models could also benefit from additional internal data, such as:
- **Marketing Data** (e.g. promotions, campaigns, etc.) 
    - **What specific data would we want?** When were we running promotions? On which channels? How much did they cost to run? How much traffic did we have on our app and website?
    - **What value does this add?** Successful promotions should result in observable sales increases. This data would also help us identify our top performing marketing channels to optimize our ROI. 
    - **How does this integrate with our existing data?** We could integrate with our existing data by date. If we run hyper-local promotions, we could join by store as well.
- **Customer Segmentation Data** (e.g. loyalty tiers, purchast history, RFM analysis) 
    - **What specific data would we want?**  Customer ID, loyalty tier, date of first purchase, lifetime spend, lifetime purchases. 
    - **What value does this add?** If our big box retailer has a loyalty program, it's helpful to monitor how sales are trending at an overall level as well as with our loyalty members, who tend to be more engaged. If loyalty sales are starting to drop, that can be more detrimental to our overall sales forecast, since we're not staying relevant to our highest value audience.
    **How does this integrate with our existing data?** Customer level data adds a whole new dimension to the store-level data we have right now. We'd need to know the store where a customer made a purchase and have a transaction log, but this would be joinable by the store ID where the user made a transaction, and let us answer questions like which stores are drawing in the most loyalty members. 
- **Product Data** (e.g. product mix, pricing)
    - **What specific data would we want?**  Product ID, name, category, department, price, COGS
    - **What value does this add?** We're a big box retailer, so there's a wide variety of products and prices. It would be helpful to dig deeper into the department level data we have and see where sales are increasing or decreasing. If we increase prices, we'll want to understand whether the hit to number of transactions outweighs the increase in basket price - does this positively or negatively impact our overall revenue?
    **How does this integrate with our existing data?** Product level data also adds a new dimension to our data. We'd need transaction-level data, and then transactions, products, and stores could each be their separate database. We could join products and stores via the transactions database, since we'd know the products purchased on a transaction and the store where products were purchased.

#### Alright, internal data out of the way, the following external data would be useful for supporting our forecast. I've listed in order from most to least accessible, which happens to also align with priority:
- **Additional Region-level Data**
    - **What specific data would we want?** Zip-code level average median income, numerical population
    - **What value does this add?** This would be the most important external dataset to add to our data in terms of boosting forecasting accuracy. Being able to incorporate factors like average median income, whether a store is in a rural, urban, or mixed region would help us create a more accurate forecast by grouping on different store types.
    **How does this integrate with our existing data?** This would be added to our stores table as additional fields. We'd need to add additional fields to our store data in order to map at a regional level, like zip code. 
- **Weather Data**
    - **What specific data would we want?**  Though we have temperature, it's helpful to know if there was rain, snow, or other inclement events e.g. hurricanes on a given day, since these heavily impact foot traffic and we're still in the 2010s with this dataset.
    - **What value does this add?** Since foot traffic is heavily influenced by the ability to get to the store, knowing the weather conditions can help us understand fluctuations in customer visits and sales.
    **How does this integrate with our existing data?** We would integrate at a date level, but we'd need to add additional fields to our store data in order to map at a regional level. Zip code, or city/state should help here. This is easily accessed via APIs e.g. Accuweather, though it sometimes incurs a cost.
- **Competitor Promos/Sales**: 
    - **What specific data would we want?**  Date of competitor promo, discount level
    - **What value does this add?** Knowing when our competitors ran promotions is helpful for forecasting our own sales - do we see decreases during competitor promos? One proxy metric that's available is Google Search Trend data for our competitors, since this tends to increase during promotional periods. It's far more difficult to get competitor sales data, unless you're paying a third party for data e.g. Visa/Circana to do a directional analysis. This is unrealistic to get in real-time.
    **How does this integrate with our existing data?** Promo information would integrate at a date level. 
- **Social Media Sentiment/Analysis**: 
    - **What specific data would we want?** Unstructured data on social media that is scored by sentiment
    - **What value does this add?** Understanding customer sentiment on social media can provide insights into brand perception and potential sales impact. For example, a spike in negative sentiment could precede a drop in sales.
    - **How does this integrate with our existing data?** Social media data could be integrated by date and potentially by store location if we can geotag posts. However, this may lag actual events and is usually best applied later in the evolution of a retailer due to the effort and processing required to get value out of unstructured data in real-time. It also leads us more into data privacy issues, so we'll need to determine our privacy policy and data deletion process first unless this data is anonymized and aggregated.
""")