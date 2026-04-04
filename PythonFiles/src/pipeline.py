import sys
import os
sys.path.append(os.path.dirname(__file__))

from extract import extract_from_csv
from validate import run_all_checks
from transform import run_transformations
from load import load_all, verify_load, run_analytics

def run_pipeline():
    print("=" * 50)
    print("   SALES ETL PIPELINE")
    print("=" * 50)

    # 1. Extract
    print("\n[STEP 1] Extracting data...")
    df = extract_from_csv('data/raw/online_retail.csv')

    # 2. Validate
    print("\n[STEP 2] Validating data...")
    passed = run_all_checks(df)
    if not passed:
        print("❌ Pipeline stopped: validation failed")
        return

    # 3. Transform
    print("\n[STEP 3] Transforming data...")
    df_clean, df_cancelled, daily_sales, customer_summary = run_transformations(df)

    # 4. Load
    print("\n[STEP 4] Loading to database...")
    load_all(df_clean, df_cancelled, daily_sales, customer_summary)
    verify_load()

    # 5. Analytics
    print("\n[STEP 5] Running analytics queries...")
    run_analytics()

    print("\n" + "=" * 50)
    print("   ✅ PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 50)

if __name__ == '__main__':
    run_pipeline()