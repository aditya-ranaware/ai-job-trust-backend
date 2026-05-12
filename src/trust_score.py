# =====================================
# TRUST SCORE ENGINE
# =====================================

def calculate_trust_score(ml_score, company_score, suspicious_score):
    """
    Combine all signals into final trust score
    Higher score = more fake
    """

    # Normalize suspicious score (0–1)
    suspicious_normalized = min(suspicious_score / 5, 1)

    # Weighted combination
    final_score = (
        (ml_score * 0.5) +
        (company_score * 0.3) +
        (suspicious_normalized * 0.2)
    )

    return round(final_score, 2)


def classify_job(final_score):
    """
    Convert score into label
    """

    if final_score > 0.7:
        return "High Risk (Fake)"
    elif final_score > 0.4:
        return "Medium Risk"
    else:
        return "Low Risk (Safe)"