import pandas as pd


def separate_cancellations(data: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    cancelled = data[data['InvoiceNo'].str.startswith('C')].copy()
    normal = data[~data['InvoiceNo'].str.startswith('C')].copy()

    print(f"Normal transactions: {len(normal):,}")
    print(f"Cancellations: {len(cancelled):,}")
    
    return normal, cancelled

def remove_invalid_rows(data: pd.DataFrame) -> pd.DataFrame:
    before = len(data)

    data = data[data['Quantity'] > 0]
    data = data[data['UnitPrice'] > 0]
    data = data.dropna(subset = ['CustomerID'])
    data = data.drop_duplicates()

    after = len(data)
    print(f"Removed {before - after:,} invalid rows ({before:,} -> {after:,})")
    return data

def fix_dtypes(data: pd.DataFrame) -> pd.DataFrame:
    data['InvoiceDate'] = pd.to_datetime(data['InvoiceDate'])
    data['CustomerID'] = data['CustomerID'].astype(str).str.strip()
    data['InvoiceNo'] = data['InvoiceNo'].astype(str).str.strip()
    data['StockCode'] = data['StockCode'].astype(str).str.strip()
    data['Country'] = data['Country'].str.strip()

    return data

def aggregate_daily_sales(data: pd.DataFrame) -> pd.DataFrame:
    daily = data.groupby('Date').agg(
        total_revenue   =('Revenue',    'sum'),
        total_orders    =('InvoiceNo',  'nunique'),
        total_customers =('CustomerID', 'nunique'),
        total_items     =('Quantity',   'sum')
    ).reset_index()

    daily['avg_order_value'] = daily['total_revenue'] / daily['total_orders']
    print(f"  Daily sales aggregated: {len(daily):,} days")
    return daily

def add_revenue(data: pd.DataFrame) -> pd.DataFrame:
    data['Revenue'] = data['Quantity'] * data['UnitPrice']
    return data

def add_date_parts(data: pd.DataFrame) -> pd.DataFrame:
    data['Date'] = data['InvoiceDate'].dt.date
    data['Year'] = data['InvoiceDate'].dt.year
    data['Month'] = data['InvoiceDate'].dt.month
    data['DayOfWeek'] = data['InvoiceDate'].dt.day_name()
    data['Hour'] = data['InvoiceDate'].dt.hour

    return data

def add_window_features(data: pd.DataFrame) -> pd.DataFrame:
    data = data.sort_values(['CustomerID', 'InvoiceDate'])

    data['CumulativeRevenue'] = (
        data.groupby('CustomerID')['Revenue'].cumsum()
    )
    data['PurchaseRank'] = (
        data.groupby('CustomerID')['InvoiceDate']
        .rank(method = 'dense')
        .astype(int)
    )

    data['TotalCustomerRevenue'] = (
        data.groupby('CustomerID')['Revenue'].transform('sum')
    )

    return data

def add_customer_segment(data: pd.DataFrame) -> pd.DataFrame:
    data['CustomerSegment'] = pd.cut(
        data['TotalCustomerRevenue'],
        bins = [0, 500, 2000, float('inf')],
        labels = ['Low', 'Mid', 'High']    
    )
    return data

def aggregate_customer_summary(data: pd.DataFrame) -> pd.DataFrame:
    """RFM-подобная таблица по клиентам"""
    last_date = data['InvoiceDate'].max()

    summary = data.groupby('CustomerID').agg(
        total_revenue   =('Revenue',     'sum'),
        total_orders    =('InvoiceNo',   'nunique'),
        total_items     =('Quantity',    'sum'),
        first_purchase  =('InvoiceDate', 'min'),
        last_purchase   =('InvoiceDate', 'max'),
        country         =('Country',     'first')
    ).reset_index()

    summary['days_since_last_purchase'] = (
        last_date - summary['last_purchase']
    ).dt.days

    summary['avg_order_value'] = (
        summary['total_revenue'] / summary['total_orders']
    )

    print(f"  Customer summary: {len(summary):,} customers")
    return summary

def run_transformations(data: pd.DataFrame):
    print("\n--- Running Transformations ---")

    # Cleanse
    print("\n[1] Separating cancellations...")
    data_normal, data_cancelled = separate_cancellations(data)

    print("\n[2] Removing invalid rows...")
    data_clean = remove_invalid_rows(data_normal)
    data_clean = fix_dtypes(data_clean)

    print("\n[3] Enriching data...")
    data_clean = add_revenue(data_clean)
    data_clean = add_date_parts(data_clean)
    data_clean = add_window_features(data_clean)
    data_clean = add_customer_segment(data_clean)


    print("\n[4] Aggregating...")
    daily_sales      = aggregate_daily_sales(data_clean)
    customer_summary = aggregate_customer_summary(data_clean)

  
    data_clean.to_csv('data/processed/transactions_clean.csv', index=False)
    data_cancelled.to_csv('data/processed/cancellations.csv', index=False)
    daily_sales.to_csv('data/processed/daily_sales.csv', index=False)
    customer_summary.to_csv('data/processed/customer_summary.csv', index=False)
    print("\nTransformed files saved to data/processed/")

    return data_clean, data_cancelled, daily_sales, customer_summary


if __name__ == '__main__':
    from extract import extract_from_csv
    data = extract_from_csv('data/raw/online_retail.csv')
    run_transformations(data)
