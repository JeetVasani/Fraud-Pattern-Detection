# Fraud Detection Pattern 

A machine-learning–driven system designed to identify abnormal behavioral patterns and flag potentially fraudulent activity.  
The project focuses on data preprocessing, feature engineering, model training, evaluation, and real-time prediction capability.


---
**Highlights**
- **95.34% accuracy** on a labelled dataset of **10,000 transactions** (test split).  
- Graph visualization of transaction networks (Neo4j + Neovis.js) to explore suspicious clusters and entity relationships.  

---

## Features

- Transaction graph visualization using **Neo4j** for relationship-aware investigation
- Preprocessing pipeline for cleaning, encoding, and transforming raw data
- Feature engineering to extract fraud indicators (behavioral & network features)
- Model training with multiple algorithms (e.g., Random Forest, XGBoost, Isolation Forest)
- Evaluation using precision, recall, F1-score, ROC-AUC, plus overall accuracy
- Exportable model for batch and realtime inference
- Modular structure for easy experimentation and extension

---

## How It Works

1. Load and clean the input dataset  
2. Engineer features that capture transactional behavior  
3. Train fraud-detection models  
4. Evaluate model performance with fraud-sensitive metrics  
5. Deploy the model for prediction on new data  

---

