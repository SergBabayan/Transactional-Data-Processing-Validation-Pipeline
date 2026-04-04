import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

data = pd.read_csv('data/raw/online_retail.csv')

print(data)
print('-' * 50)

print(data.head())
print('-' * 50)

print(data.isnull().sum())
print('-' * 50)

print(data.describe())
print('-' * 50)

print(data.info())
print('-' * 50)


plt.figure(figsize=(12, 8))
sns.heatmap(data.isnull(), cbar=False, cmap='viridis', yticklabels=False)
plt.xlabel('Columns')
plt.ylabel('Deadlines')
plt.tight_layout()
plt.show()

numeric_cols = data.select_dtypes(include=['int64', 'float64']).columns
def find_outliers_iqr(data, column):
    Q1 = data[column].quantile(0.25)
    Q3 = data[column].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    outliers = data[(data[column] < lower) | (data[column] > upper)]
    return len(outliers), lower, upper

for col in numeric_cols:
    count, low, up = find_outliers_iqr(data, col)
    print(f"{col}: {count} outliers (lower threshold={low:.2f}, upper={up:.2f})")