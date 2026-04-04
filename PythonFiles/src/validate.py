import pandas as pd
from dataclasses import dataclass, field
from typing import List

@dataclass
class ValidationResult:
    check_name: str
    passed: bool
    errors: List[str] = field(default_factory = list)
    warning_count: int = 0

    def summary(self):
        status = "PASSED" if self.passed else "FAILED"
        print(f"{status} | {self.check_name}")
        for e in self.errors:
            print(f"{e}")

def validate_schema(data: pd.DataFrame) -> ValidationResult:
    required = ['InvoiceNo','StockCode','Description', 'Quantity','InvoiceDate','UnitPrice','CustomerID','Country']
    missing = [c for c in required if c not in data.columns]

    return ValidationResult(
        check_name = "Schema Check",
        passed = len(missing) == 0,
        errors = [f"Missing column: {c}" for c in missing]
    ) 

def validate_nulls(data: pd.DataFrame) -> ValidationResult:
    critical = ['InvoiceNo', 'StockCode', 'Quantity', 'UnitPrice']
    errors = []

    for col in critical:
        n = data[col].isnull().sum()
        if n > 0:
            errors.append(f"{col}: {n,} null values")
    null_customers = data['CustomerID'].isnull().sum()
    print(f"||| WARNING |||: {null_customers:,} rows with no CustomerID")

    return ValidationResult(
        check_name = "Null Check",
        passed = len(errors) == 0,
        errors = errors,
        warning_count = null_customers
    )
    
def validate_business_rules(data: pd.DataFrame) -> ValidationResult:
    errors = []
    neg_qty = (data['Quantity'] < 0).sum()

    if neg_qty > 0:
        errors.append(f"{neg_qty:,} rows with negative Quantity (returns or cancell)")

    zero_price = (data['UnitPrice'] <= 0).sum()
    if zero_price > 0:
        errors.append(f"{zero_price:,} rows with zero or negative UnitPrice")

    return ValidationResult(
        check_name = "Business Rules Check",
        passed = True,
        errors = errors
    )

def run_all_checks(data: pd.DataFrame) -> bool:
    print("\n |-| VALIDATION RUNNING... |-|")
    checks = [
        validate_schema(data),
        validate_nulls(data),
        validate_business_rules(data),
    ]
    for check in checks:
        check.summary()
    
    failed = [c for c in checks if not c.passed]
    print(f"Validation complete: {len(checks) - len(failed) / len(checks)} checks passed")
    return len(failed) == 0

if __name__ == '__main__':
    from extract import extract_from_csv
    data = extract_from_csv('data/raw/online_retail.csv')
    run_all_checks(data)