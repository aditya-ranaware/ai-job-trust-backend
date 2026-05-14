# =====================================
# RISK INTELLIGENCE MODULE
# Generates Professional Job Trust Report
# =====================================

# from verification_engine import run_verification_engine

from src.verification_engine import run_verification_engine

def get_risk_level(score):
    """
    Convert numeric risk score into risk level.
    """
    if score >= 70:
        return "High"
    elif score >= 40:
        return "Medium"
    return "Low"


def generate_professional_report(
    ml_score,
    company_score,
    suspicious_score,
    title,
    description,
    company_profile,
    requirements="",
    benefits=""
):
    """
    Generates final professional report using:
    - ML fraud probability
    - Multi-layer verification engine
    - Content risk
    - Company risk
    - Contact risk
    - Source verification risk
    """

    # =====================================
    # 1. RUN MULTI-LAYER VERIFICATION ENGINE
    # =====================================
    verification_result = run_verification_engine(
        title=title,
        description=description,
        company_profile=company_profile,
        requirements=requirements,
        benefits=benefits
    )

    # =====================================
    # 2. EXTRACT SCORES FROM VERIFICATION ENGINE
    # =====================================
    content_score = verification_result["content"]["score"]
    company_risk_score = verification_result["company"]["score"]
    contact_score = verification_result["contact"]["score"]
    source_score = verification_result["source"]["score"]

    # ML score comes as probability like 0.82
    ml_percent = int(ml_score * 100)

    # =====================================
    # 3. FINAL RISK SCORE CALCULATION
    # =====================================
    final_risk_score = int(
        (ml_percent * 0.30) +
        (content_score * 0.20) +
        (company_risk_score * 0.20) +
        (contact_score * 0.20) +
        (source_score * 0.10)
    )

    final_risk_score = max(0, min(100, final_risk_score))

    # Trust score is opposite of risk score
    trust_score = 100 - final_risk_score

    risk_level = get_risk_level(final_risk_score)

    # =====================================
    # 4. FINAL DECISION + RECOMMENDATION
    # =====================================
    if risk_level == "High":
        final_decision = "🚨 High Risk Job"
        recommendation = (
            "Avoid applying until the company and job details are verified through official sources."
        )
        final_advice = (
            "This job post contains multiple risk indicators. Do not share personal documents, "
            "bank details, OTP, or money until the opportunity is confirmed from the official "
            "company website or verified HR contact."
        )

    elif risk_level == "Medium":
        final_decision = "⚠️ Medium Risk Job"
        recommendation = (
            "Proceed carefully and verify company details before applying."
        )
        final_advice = (
            "This job post has some risk signals. Verify the company website, HR email domain, "
            "application link, and job listing source before sharing personal information."
        )

    else:
        final_decision = "✅ Low Risk Job"
        recommendation = (
            "This job looks mostly safe based on available details, but basic verification is still recommended."
        )
        final_advice = (
            "The job post does not show major risk signals. Still, verify the company identity, "
            "official application link, and avoid sharing sensitive documents before an official interview process."
        )

    # =====================================
    # 5. COLLECT RED FLAGS
    # =====================================
    red_flags = (
        verification_result["content"]["red_flags"] +
        verification_result["company"]["red_flags"] +
        verification_result["contact"]["red_flags"] +
        verification_result["source"]["red_flags"]
    )

    # If ML model confidence is high, add ML red flag
    if ml_percent >= 70:
        red_flags.append("Machine learning model detected high fraud probability")

    # If suspicious_score is high, add fraud-pattern flag
    if suspicious_score >= 3:
        red_flags.append("Multiple suspicious keyword patterns detected")

    # =====================================
    # 6. COLLECT POSITIVE SIGNALS
    # =====================================
    positive_signals = list(set(
        verification_result["content"]["positive_signals"] +
        verification_result["company"]["positive_signals"] +
        verification_result["contact"]["positive_signals"] +
        verification_result["source"]["positive_signals"]
    ))

    if ml_percent < 40:
        positive_signals.append("Machine learning model detected low fraud probability")

    # =====================================
    # 7. VERIFICATION CHECKLIST
    # =====================================
    verification_checklist = [
        "Check the company's official website",
        "Verify whether the HR email domain matches the company domain",
        "Search for the job on the official company career page",
        "Check if the same job is listed on trusted platforms like LinkedIn, Naukri, or Indeed",
        "Avoid paying any registration, training, processing, or security fee",
        "Do not share Aadhaar, PAN, bank details, OTP, or sensitive documents before verification",
        "Confirm the interview process and official application link"
    ]

    # =====================================
    # 8. FINAL REPORT RESPONSE
    # =====================================
    report = {
        "final_decision": final_decision,
        "trust_score": trust_score,
        "risk_score": final_risk_score,
        "risk_level": risk_level,
        "recommendation": recommendation,

        "risk_breakdown": {
            "content_risk": verification_result["content"]["risk_level"],
            "company_risk": verification_result["company"]["risk_level"],
            "contact_risk": verification_result["contact"]["risk_level"],
            "source_risk": verification_result["source"]["risk_level"],
            "ml_risk": get_risk_level(ml_percent)
        },

        "risk_scores": {
            "content_score": content_score,
            "company_score": company_risk_score,
            "contact_score": contact_score,
            "source_score": source_score,
            "ml_score": ml_percent
        },

        "red_flags": red_flags,
        "positive_signals": positive_signals,
        "verification_checklist": verification_checklist,
        "final_advice": final_advice
    }

    return report