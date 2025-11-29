import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
import sys

# Load the training data
df_train = pd.read_csv('app/backend/transactions_10000_realistic_RARE_CYCLES.csv')

# Load the test data from uploaded file
if len(sys.argv) > 1:
    test_file = sys.argv[1]
    df_test = pd.read_csv(test_file)
else:
    df_test = df_train.copy()  # Fallback to training data if no file provided

df = df_train  # Use training data for model building

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

# Now process the test data
# Compute account-level statistics for test data
account_stats_test = df_test.groupby('from_account').agg(
    transaction_count=('txn_id', 'count'),
    total_amount=('amount', 'sum')
).reset_index()

# Merge account stats back to df_test
df_test = df_test.merge(account_stats_test, on='from_account', how='left')

# Compute account amount stats for outlier detection
account_amount_stats_test = df_test.groupby('from_account')['amount'].agg(['mean', 'std']).reset_index()
account_amount_stats_test.rename(columns={'mean': 'avg_amount', 'std': 'std_amount'}, inplace=True)
df_test = df_test.merge(account_amount_stats_test, on='from_account', how='left')
df_test['std_amount'] = df_test['std_amount'].fillna(0)  # Handle accounts with single transaction

# Prepare features for test data
features_test = ['amount', 'kyc_risk', 'transaction_count', 'total_amount', 'avg_amount', 'std_amount']

# Label encode categorical features for test data
for col in categorical_features:
    df_test[col + '_encoded'] = le.fit_transform(df_test[col])
    features_test.append(col + '_encoded')

X_test_data = df_test[features_test]

# Predict fraud on the test dataset
df_test['fraud_probability'] = rf_model.predict_proba(X_test_data)[:, 1]
df_test['predicted_fraud'] = (df_test['fraud_probability'] > 0.5).astype(int)

# Flag transactions as predicted fraud
flagged = df_test[df_test['predicted_fraud'] == 1]

# Save flagged transactions to a new CSV
flagged.to_csv('app/backend/flagged_transactions.csv', index=False)

# Output JSON result (limit flagged data to first 10 for brevity)
flagged_summary = flagged.head(10).to_dict(orient='records')

result = {
    'accuracy': accuracy,
    'total_transactions': len(df_test),
    'flagged_transactions': len(flagged),
    'flagged_data': flagged_summary
}

import json
print(json.dumps(result))
