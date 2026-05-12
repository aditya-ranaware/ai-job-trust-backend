# =====================================
# COMPANY VALIDATION MODULE
# =====================================

import re

# Common free email domains (suspicious for jobs)
FREE_EMAIL_DOMAINS = [
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com"
]

def extract_email_domain(text):
    """
    Extract email domain from text
    """
    emails = re.findall(r'[\w\.-]+@([\w\.-]+)', text)
    return emails[0] if emails else None


def check_email_domain(text):
    """
    Check if email domain is suspicious
    """
    domain = extract_email_domain(text)

    if domain is None:
        return 0.5   # unknown

    if domain.lower() in FREE_EMAIL_DOMAINS:
        return 1.0   # high risk

    return 0.0   # safe


def check_company_profile(company_profile):
    """
    Check if company profile exists
    """
    if not company_profile or company_profile.strip() == "":
        return 1.0   # suspicious

    return 0.0


def get_company_score(description, company_profile):
    """
    Final company trust score
    (higher = more suspicious)
    """

    email_score = check_email_domain(description)
    profile_score = check_company_profile(company_profile)

    # weighted average
    final_score = (email_score * 0.6) + (profile_score * 0.4)

    return round(final_score, 2)