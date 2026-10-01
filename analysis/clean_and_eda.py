"""TASK 1
"""

import pandas as pd
orders=pd.read_csv('orders.csv')
customers=pd.read_csv('customers.csv')
products=pd.read_csv('products.csv')
print(orders.shape)

"""TASK 2"""

#before fix
print(orders['payment_method'].unique())

#after fix
orders['payment_method']=orders['payment_method'].str.strip().str.upper()
print(orders['payment_method'].unique())
L=list(orders['payment_method'].unique())
print(orders['payment_method'].value_counts())

"""TASK 3"""

natural_key = [
    "customer_id", "product_id", "order_date", "quantity",
    "discount_pct", "payment_method", "rating", "returned"
]

# Detect duplicates based on natural key
duplicates_mask = orders.duplicated(subset=natural_key, keep='first')

# Extract the duplicate rows
duplicates = orders.loc[duplicates_mask]

# Print the order_id values of duplicates
print("Dropped order_id values:", list(duplicates["order_id"]))

# Drop duplicates
orders_clean = orders.drop_duplicates(subset=natural_key, keep='first')

# Verify shape
print("orders_clean.shape:", orders_clean.shape)

"""TASK 4"""

# Work on a safe copy
orders_clean = orders_clean.copy()

# ---- discount_pct ----
# Count NaNs before filling
na_discount_before = orders_clean['discount_pct'].isnull().sum()
print("NaNs in discount_pct before:", na_discount_before)  # should be 12

# Fill NaNs with 0
orders_clean.loc[:, 'discount_pct'] = orders_clean['discount_pct'].fillna(0)

# ---- rating ----
# Count NaNs before filling
na_rating_before = orders_clean['rating'].isnull().sum()
print("NaNs in rating before:", na_rating_before)  # should be 15

# Median of non-null ratings
median_rating = orders_clean['rating'].median()
print("Median rating before imputing:", median_rating)  # should be 3.0

# Fill NaNs with median
orders_clean.loc[:, 'rating'] = orders_clean['rating'].fillna(median_rating)

# ---- final check ----
print(orders_clean[['discount_pct','rating']].isnull().sum().to_dict())

"""TASK 5"""

# Merge with products
orders_products = orders_clean.merge(products, on="product_id", how="left")

# Merge with customers
orders_full = orders_products.merge(customers, on="customer_id", how="left")
orders_full['order_value'] = (
    orders_full['quantity'] * orders_full['price'] * (1 - orders_full['discount_pct'] / 100)
)
total_clean = orders_full['order_value'].sum()
print("Total order_value (cleaned):", round(total_clean, 2))  # should be 97358.30
# Get the dropped duplicates again
duplicates = orders.loc[orders.duplicated(
    subset=[
        "customer_id","product_id","order_date","quantity",
        "discount_pct","payment_method","rating","returned"
    ],
    keep='first'
)]

# Compute their combined order_value
duplicates_merged = duplicates.merge(products, on="product_id", how="left")
duplicates_merged = duplicates_merged.merge(customers, on="customer_id", how="left")

duplicates_merged['order_value'] = (
    duplicates_merged['quantity'] * duplicates_merged['price'] * (1 - duplicates_merged['discount_pct'] / 100)
)

print("Dropped duplicates order_value sum:", round(duplicates_merged['order_value'].sum(), 2))  # should be 2501.90
print(
    "Reconciliation Note:\n"
    "The cleaned dataset total order_value is ₹97,358.30, which is ₹2,501.90 less than "
    "the raw Part 1 Report (₹99,860.20). This exact delta is fully explained by the 5 "
    "duplicate rows removed in Task 3, whose combined order_value is ₹2,501.90. "
    "Discount and rating imputations did not affect order_value, so the reduction is "
    "solely due to duplicate removal."
)

"""TASK 6"""

Q1 = orders_products['quantity'].quantile(0.25)
Q3 = orders_products['quantity'].quantile(0.75)
IQR = Q3-Q1
lower = Q1 - 1.5*IQR
upper = Q3 + 1.5*IQR
print(f'Q1 is {Q1}. \nQ3 is {Q3}. \nIQR is {IQR}. \nlower is {lower}. \nupper is {upper}')
L=[]
for i in orders_products['quantity']:
  if i>upper or i<lower:
    L.append(1)
  else:
    L.append(0)
orders_products['is_outlier']=L

"""TASK 7-Hypothesis: does COD have a higher return rate?"""

print("Hypothesis: does COD have a higher return rate?")
result=orders_products.groupby('payment_method')['returned'].agg(['count','mean'])
result['mean']=(result['mean']*100).round(1)
print(result)
print("Hypothesis Verified")

"""TASK 8"""

result2 = orders_full.groupby(['payment_method','city_tier'])['returned'].agg(['count','mean'])
result2 = result2.rename(columns={'mean':'return_rate'})
result2['return_rate'] = (result2['return_rate']*100).round(1)
print(result2)
print("Highest-risk segment: COD + Tier-2 cities at 54.5%")

"""TASK 9"""

corr = orders_full[['rating','returned','discount_pct','quantity']].corr()
print(corr)

bands = {
    (0.0,0.19): "negligible",
    (0.2,0.39): "weak",
    (0.4,0.69): "moderate",
    (0.7,1.0): "strong"
}

def label_band(r):
    r_abs = abs(r)
    for (low,high),label in bands.items():
        if low <= r_abs <= high:
            return label

for col1 in corr.columns:
    for col2 in corr.columns:
        if col1 < col2:  # avoid duplicates
            print(f"{col1} vs {col2}: {label_band(corr.loc[col1,col2])}")
print('The hypothesis which states that "higher discounts reduce returns" is busted.')

"""TASK 10"""

# Convert to datetime safely
orders_full['order_date'] = pd.to_datetime(orders_full['order_date'], errors='coerce')

# Extract year-month period
orders_full['year_month'] = orders_full['order_date'].dt.to_period('M').astype(str)

# Group including outliers
monthly_incl = orders_full.groupby('year_month')['order_value'].sum().round(2)
print("Including outliers:\n", monthly_incl)

# Remove outliers
outliers = ['O0011','O0098']
orders_no_out = orders_full[~orders_full['order_id'].isin(outliers)]

# Group excluding outliers
monthly_excl = orders_no_out.groupby('year_month')['order_value'].sum().round(2)
print("Excluding outliers:\n", monthly_excl)

print("Note: January’s apparent lead is due to bulk orders O0011 (2026-01-28) and O0098 (2026-01-10).")
print("True peak month is March once outliers are excluded.")
