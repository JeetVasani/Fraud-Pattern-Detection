import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
import sys

# Redirect stdout to a file
sys.stdout = open('fraud_analysis_output.txt', 'w')

# Load the flagged transactions data
df = pd.read_csv('flagged_transactions.csv')

# Basic summary
print("Summary of Flagged Transactions:")
print(df.describe())

# Convert timestamp to datetime
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Group by txn_type and count
txn_type_counts = df['txn_type'].value_counts()
print("\nFraud Counts by Transaction Type:")
print(txn_type_counts)

# Group by channel
channel_counts = df['channel'].value_counts()
print("\nFraud Counts by Channel:")
print(channel_counts)

# Group by location
location_counts = df['location'].value_counts()
print("\nFraud Counts by Location:")
print(location_counts)

# Group by company
company_counts = df['company'].value_counts()
print("\nFraud Counts by Company:")
print(company_counts)

# High amount frauds
high_amount_frauds = df[df['amount'] > 250000]
print(f"\nNumber of High Amount Frauds (>250k): {len(high_amount_frauds)}")

# High risk KYC
high_risk_frauds = df[df['kyc_risk'] > 0.8]
print(f"Number of High KYC Risk Frauds (>0.8): {len(high_risk_frauds)}")

# Accounts with high transaction counts
high_txn_accounts = df[df['transaction_count'] > 10]['from_account'].unique()
print(f"Accounts with >10 Transactions: {len(high_txn_accounts)}")

# Outlier amounts
outlier_frauds = df[df['amount'] > (df['avg_amount'] + 3 * df['std_amount'])]
print(f"Number of Outlier Amount Frauds: {len(outlier_frauds)}")

# Time-based patterns: hour of day
df['hour'] = df['timestamp'].dt.hour
hour_counts = df['hour'].value_counts().sort_index()
print("\nFraud Counts by Hour of Day:")
print(hour_counts)

# Day of week
df['day_of_week'] = df['timestamp'].dt.day_name()
day_counts = df['day_of_week'].value_counts()
print("\nFraud Counts by Day of Week:")
print(day_counts)

# Look for potential cycles: group by from_account and see if patterns
account_patterns = df.groupby('from_account').agg(
    txn_count=('txn_id', 'count'),
    unique_to_accounts=('to_account', 'nunique'),
    total_amount=('amount', 'sum'),
    avg_amount=('amount', 'mean')
).reset_index()

# Accounts with many unique to_accounts (potential money laundering)
suspicious_accounts = account_patterns[account_patterns['unique_to_accounts'] > 5]
print(f"\nAccounts with >5 Unique To-Accounts: {len(suspicious_accounts)}")
print(suspicious_accounts.head())

# Save analysis to CSV
analysis_summary = {
    'total_flagged': len(df),
    'high_amount_frauds': len(high_amount_frauds),
    'high_risk_frauds': len(high_risk_frauds),
    'high_txn_accounts': len(high_txn_accounts),
    'outlier_frauds': len(outlier_frauds),
    'suspicious_accounts': len(suspicious_accounts)
}
pd.DataFrame([analysis_summary]).to_csv('fraud_analysis_summary.csv', index=False)

print("\nAnalysis complete. Summary saved to fraud_analysis_summary.csv")

# Close the file
sys.stdout.close()
