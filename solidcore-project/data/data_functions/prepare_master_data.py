# data/data_functions/prepare_master_data.py

import pandas as pd
from pathlib import Path
import numpy as np
# <<< FIX: Removed unused 'sys' import

def prepare_master_data():
    print("🚀 Starting the master data preparation pipeline...")

    # <<< FIX: Define a robust project root based on this script's location
    PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
    
    # <<< FIX: Define all paths relative to the project root
    unprocessed_dir = PROJECT_ROOT / 'data' / 'unprocessed_data'
    processed_dir = PROJECT_ROOT / 'data' / 'processed_data'

    file_paths = {
        'sales':  'Store_Sales.xlsx',
        'stores': 'Store_Type.xlsx',
        'macro':  'Macro_Factors.xlsx'
    }
    output_path = processed_dir / 'master_data.csv'

    try:
        print("\n[Step 1/5] Loading raw Excel files...")
        # <<< FIX: Join the directory path with the filename for loading
        dfs = {name: pd.read_excel(unprocessed_dir / path) for name, path in file_paths.items()}
        print("   - Success: All raw files loaded.")
    except FileNotFoundError as e:
        print(f"❌ ERROR: Raw data file not found. Please check your paths. Details: {e}")
        return

    # Merge dataframes, left joining to the sales dataset. We do not need to join Holiday because data is represented elsewhere.
    print("\n[Step 2/5] Merging dataframes...")
    df = pd.merge(dfs['sales'], dfs['stores'], on='Store', how='left')
    df = pd.merge(df, dfs['macro'], on=['Store', 'Date', 'IsHoliday'], how='left')
    print("   - Success: Sales, store, and macro data merged.")

    # Cleaning data - making sure dates are dates and not strings
    print("\n[Step 3/5] Cleaning and preprocessing data...")
    df['Date'] = pd.to_datetime(df['Date'])
    df.sort_values(by=['Store', 'Date'], inplace=True)

    # Since CPI and Unemployment come out monthly, fill in missing data by performing a forward fill, then a backward fill to have a better time series
    df['CPI'] = df.groupby('Store')['CPI'].transform(lambda x: x.ffill().bfill())
    df['Unemployment'] = df.groupby('Store')['Unemployment'].transform(lambda x: x.ffill().bfill())

    initial_rows = len(df)
    df.dropna(inplace=True)
    if len(df) < initial_rows:
        print(f"   - Dropped {initial_rows - len(df)} rows with remaining NaN values.")
    print("   - Success: Data types converted and missing values handled.")


    print("\n[Step 4/5] Engineering analytical features...")
    # Create new features for year, month, and ISO Week of Year
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    df['WeekOfYear'] = df['Date'].dt.isocalendar().week.astype(int)

    # Create a new feature in the dataframe to show sales per square foot (Assuming size is square feet)
    df['Sales_per_sq_ft'] = df['Weekly_Sales'] / df['Size']
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df['Sales_per_sq_ft'].fillna(0, inplace=True)

    # Create a new feature in the dataframe that indicates whether next week is a holiday
    holiday_shift = df.groupby('Store')['IsHoliday'].shift(-1)
    df['Is_Week_Before_Holiday'] = holiday_shift.fillna(False).astype(bool)
    print("   - Success: Time-based, performance, and holiday-proximity features created.")

    # Save final dataset
    print(f"\n[Step 5/5] Saving final dataset to '{output_path}'...")
    processed_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

    print("\n✅ Pipeline complete! `master_data.csv` is now ready for the application.")
    print(f"   - Final dataset has {len(df)} rows and {len(df.columns)} columns.")


if __name__ == "__main__":
    prepare_master_data()