import pandas as pd
from sqlalchemy import create_engine, text
import os

def get_engine():
    os.makedirs('data', exist_ok=True)
    engine = create_engine('sqlite:///data/sales.db', echo=False)
    return engine


def load_table(data: pd.DataFrame, table_name: str, if_exists='replace'):

    engine = get_engine()
    data.to_sql(
        name=table_name,
        con=engine,
        if_exists=if_exists,
        index=False,
        chunksize=1000
    )
    print(f"  ✅ {table_name}: {len(data):,} rows loaded")


def load_all(df_clean, df_cancelled, daily_sales, customer_summary):
    print("\n--- Loading to Database ---")
    load_table(df_clean,          'transactions')
    load_table(df_cancelled,      'cancellations')
    load_table(daily_sales,       'daily_sales')
    load_table(customer_summary,  'customer_summary')
    print("\n✅ All tables loaded into data/sales.db")

def verify_load():
    engine = get_engine()
    tables = ['transactions', 'cancellations', 'daily_sales', 'customer_summary']

    print("\n--- Verifying Load ---")
    with engine.connect() as conn:
        for table in tables:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = result.scalar()
            print(f"  {table}: {count:,} rows in DB")

def run_analytics():
    engine = get_engine()

    print("\n--- Analytics Queries ---")

    q1 = """
        SELECT
            Date,
            total_revenue,
            ROUND(SUM(total_revenue) OVER (ORDER BY Date), 2) AS cumulative_revenue
        FROM daily_sales
        ORDER BY Date
        LIMIT 10
    """
    df1 = pd.read_sql(q1, engine)
    print("\n[Window Function] Cumulative Revenue:")
    print(df1.to_string(index=False))

    q2 = """
        SELECT
            CustomerID,
            ROUND(total_revenue, 2) AS total_revenue,
            total_orders,
            country,
            RANK() OVER (ORDER BY total_revenue DESC) AS revenue_rank
        FROM customer_summary
        LIMIT 10
    """
    df2 = pd.read_sql(q2, engine)
    print("\n[Window Function] Top 10 Customers by Revenue:")
    print(df2.to_string(index=False))

    q3 = """
        SELECT
            country,
            ROUND(SUM(total_revenue), 2) AS country_revenue,
            COUNT(CustomerID)            AS num_customers
        FROM customer_summary
        GROUP BY country
        ORDER BY country_revenue DESC
        LIMIT 10
    """
    df3 = pd.read_sql(q3, engine)
    print("\n[Aggregation] Revenue by Country:")
    print(df3.to_string(index=False))


if __name__ == '__main__':
    from extract import extract_from_csv
    from validate import run_all_checks
    from transform import run_transformations

    df = extract_from_csv('data/raw/online_retail.csv')
    run_all_checks(df)
    df_clean, df_cancelled, daily_sales, customer_summary = run_transformations(df)

    load_all(df_clean, df_cancelled, daily_sales, customer_summary)
    verify_load()
    run_analytics()