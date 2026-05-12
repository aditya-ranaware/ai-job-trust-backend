# =====================================
# TRAIN PIPELINE (PHASE 4 FINAL)
# =====================================

import pandas as pd
import re
import joblib

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report

from scipy.sparse import hstack

# XGBoost
from xgboost import XGBClassifier

# SHAP
import shap

# Import your feature engineering
from feature_engineering import create_features, get_feature_matrix


# =====================================
# 1. LOAD DATA
# =====================================
df = pd.read_csv("../data/fake_job_postings.csv")


# =====================================
# 2. HANDLE MISSING VALUES
# =====================================
text_cols = ['title', 'description', 'company_profile', 'requirements', 'benefits']

for col in text_cols:
    df[col] = df[col].fillna('')

cat_cols = ['employment_type', 'required_experience', 'required_education',
            'industry', 'function', 'location']

for col in cat_cols:
    df[col] = df[col].fillna('unknown')

df['salary_range'] = df['salary_range'].fillna('unknown')

if 'department' in df.columns:
    df.drop(columns=['department'], inplace=True)


# =====================================
# 3. CREATE TEXT
# =====================================
df['text'] = df['title'] + " " + df['description'] + " " + \
             df['company_profile'] + " " + df['requirements'] + " " + df['benefits']


# =====================================
# 4. CLEAN TEXT
# =====================================
def clean_text(text):
    text = text.lower()
    text = re.sub(r'\W+', ' ', text)
    text = re.sub(r'\d+', ' ', text)
    return text

df['clean_text'] = df['text'].apply(clean_text)


# =====================================
# 5. FEATURE ENGINEERING
# =====================================
df = create_features(df)
X_extra = get_feature_matrix(df)


# =====================================
# 6. SPLIT DATA
# =====================================
X_text = df['clean_text']
y = df['fraudulent']

X_train_text, X_test_text, y_train, y_test = train_test_split(
    X_text, y, test_size=0.2, random_state=42
)

X_train_extra = X_extra.iloc[X_train_text.index]
X_test_extra = X_extra.iloc[X_test_text.index]


# =====================================
# 7. TF-IDF
# =====================================
vectorizer = TfidfVectorizer(max_features=5000)

X_train_vec = vectorizer.fit_transform(X_train_text)
X_test_vec = vectorizer.transform(X_test_text)


# =====================================
# 8. COMBINE FEATURES
# =====================================
X_train_final = hstack([X_train_vec, X_train_extra.values])
X_test_final = hstack([X_test_vec, X_test_extra.values])


# =====================================
# 9. TRAIN MODEL (XGBOOST 🔥)
# =====================================
model = XGBClassifier(
    n_estimators=200,
    learning_rate=0.1,
    max_depth=6,
    scale_pos_weight=5,   # handles imbalance
    random_state=42,
    use_label_encoder=False,
    eval_metric='logloss'
)

model.fit(X_train_final, y_train)


# =====================================
# 10. EVALUATION
# =====================================
y_pred = model.predict(X_test_final)

print("\n=== MODEL PERFORMANCE ===")
print(classification_report(y_test, y_pred))


# =====================================
# 11. SHAP EXPLAINABILITY 🔥
# =====================================
print("\n=== GENERATING SHAP VALUES ===")

# Convert to CSR format
X_sample = X_train_final.tocsr()[:100]

# Use TreeExplainer (important)
explainer = shap.TreeExplainer(model)

shap_values = explainer.shap_values(X_sample)

# Plot
shap.summary_plot(shap_values, X_sample)


# =====================================
# 12. SAVE MODEL
# =====================================
joblib.dump(model, "../models/xgb_model.pkl")
joblib.dump(vectorizer, "../models/vectorizer.pkl")

print("\n✅ Model and vectorizer saved successfully!")