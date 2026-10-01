#return_rate_by_payment
import matplotlib.pyplot as plt

# Step 1: Aggregate and rename properly
result = (
    orders.groupby('payment_method')['returned']
    .agg(['count','mean'])
    .rename(columns={'mean':'return_rate'})
)

# Step 2: Convert to percentage
result['return_rate'] = (result['return_rate'] * 100).round(1)

# Step 3: Sort by return_rate
result_sorted = result.sort_values('return_rate', ascending=False)

# Step 4: Plot
plt.figure(figsize=(6,4))
bars = plt.bar(result_sorted.index, result_sorted['return_rate'], color='skyblue')

# Label each bar
for bar, pct in zip(bars, result_sorted['return_rate']):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
             f"{pct:.1f}%", ha='center', va='bottom')

plt.title("COD Returns at 44.4% — 3x Card")
plt.ylabel("Return Rate (%)")
plt.xlabel("Payment Method")
plt.tight_layout()
plt.savefig("visualise/return_rate_by_payment.png")
plt.show()
plt.close()


#monthly_revenue_trend
# Assuming monthly_excl Series from Task 10 (outlier-corrected totals)
plt.figure(figsize=(7,4))
monthly_excl.plot(kind='line', marker='o', color='green')

plt.title("Monthly Revenue Trend — Peak in March")
plt.xlabel("Year-Month")
plt.ylabel("Revenue (₹)")
plt.grid(True)
plt.tight_layout()
plt.savefig("visualizations/monthly_revenue_trend.png")
plt.show()
plt.close()


