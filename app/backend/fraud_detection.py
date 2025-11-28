import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score

# Load the transaction data
df = pd.read_csv('transactions_10000_realistic_RARE_CYCLES.csv')

# Compute account-level statistics
account_stats = df.groupby('from_account').agg(
    transaction_count=('txn_id', 'count'),
    total_amount=('amount', 'sum')
).reset_index()

# Merge account stats back to df
df = df.merge(account_stats, on='from_account', how='left')

# Compute account amount stats for outlier detection
account_amount_stats = df.groupby('from_account')['amount'].agg(['mean', 'std']).reset_index()
account_amount_stats.rename(columns={'mean': 'avg_amount', 'std': 'std_amount'}, inplace=True)
df = df.merge(account_amount_stats, on='from_account', how='left')
df['std_amount'] = df['std_amount'].fillna(0)  # Handle accounts with single transaction

# Generate fraud labels using existing rules
high_amount = df['amount'] > 250000
high_risk = df['kyc_risk'] > 0.8
suspicious_accounts = account_stats[
    (account_stats['transaction_count'] > 10) | (account_stats['total_amount'] > 500000)
]['from_account']
account_anomaly = df['from_account'].isin(suspicious_accounts)
outlier_amount = df['amount'] > (df['avg_amount'] + 3 * df['std_amount'])
df['is_fraud'] = (high_amount | high_risk | account_anomaly | outlier_amount).astype(int)

# Prepare features
features = ['amount', 'kyc_risk', 'transaction_count', 'total_amount', 'avg_amount', 'std_amount']
categorical_features = ['txn_type', 'channel', 'location', 'company']

# Label encode categorical features
le = LabelEncoder()
for col in categorical_features:
    df[col + '_encoded'] = le.fit_transform(df[col])
    features.append(col + '_encoded')

# Select features and target
X = df[features]
y = df['is_fraud']

# Split into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train Random Forest model
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)

# Evaluate on test set
y_pred = rf_model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Model Accuracy on Test Set: {accuracy:.4f}")

# Predict fraud on the full dataset
df['fraud_probability'] = rf_model.predict_proba(X)[:, 1]
df['predicted_fraud'] = (df['fraud_probability'] > 0.5).astype(int)

# Flag transactions as predicted fraud
flagged = df[df['predicted_fraud'] == 1]

# Save flagged transactions to a new CSV
flagged.to_csv('flagged_transactions.csv', index=False)

print(f"Flagged {len(flagged)} suspicious transactions out of {len(df)} total transactions.")
print("Flagged transactions saved to flagged_transactions.csv")
