# =====================================
# FEATURE ENGINEERING MODULE
# =====================================

import pandas as pd

# -------------------------------
# 1. Suspicious Keywords Feature
# -------------------------------

SUSPICIOUS_WORDS = [
    "earn", "quick", "money", "no experience",
    "work from home", "easy job", "instant",
    "limited time", "apply now", "urgent hiring"
]

def get_suspicious_score(text):
    score = 0
    text = str(text).lower()

    for word in SUSPICIOUS_WORDS:
        if word in text:
            score += 1

    return score


# -------------------------------
# 2. Missing Company Profile
# -------------------------------

def missing_company_profile(company_profile):
    if company_profile == '' or pd.isnull(company_profile):
        return 1
    return 0


# -------------------------------
# 3. Title Length
# -------------------------------

def get_title_length(title):
    return len(str(title))


# -------------------------------
# 4. Description Length
# -------------------------------

def get_desc_length(description):
    return len(str(description))


# -------------------------------
# 5. Capital Ratio
# -------------------------------

def get_capital_ratio(text):
    text = str(text)

    if len(text) == 0:
        return 0

    capital_count = sum(1 for c in text if c.isupper())
    return capital_count / len(text)


# -------------------------------
# 6. MAIN FUNCTION (IMPORTANT 🔥)
# -------------------------------

def create_features(df):
    """
    Takes dataframe and returns dataframe with new features
    """

    df = df.copy()

    # Suspicious score
    df['suspicious_score'] = df['description'].apply(get_suspicious_score)

    # Missing company profile
    df['missing_company_profile'] = df['company_profile'].apply(
        missing_company_profile
    )

    # Title length
    df['title_length'] = df['title'].apply(get_title_length)

    # Description length
    df['desc_length'] = df['description'].apply(get_desc_length)

    # Capital ratio
    df['capital_ratio'] = df['description'].apply(get_capital_ratio)

    return df


# -------------------------------
# 7. GET FEATURE MATRIX
# -------------------------------

def get_feature_matrix(df):
    feature_cols = [
        'suspicious_score',
        'missing_company_profile',
        'title_length',
        'desc_length',
        'capital_ratio'
    ]

    return df[feature_cols]