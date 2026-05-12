import re


FREE_EMAIL_DOMAINS = [
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "rediffmail.com"
]

PAYMENT_KEYWORDS = [
    "registration fee", "processing fee", "security deposit", "joining fee",
    "pay fee", "pay money", "refundable fee", "training fee"
]

SENSITIVE_INFO_KEYWORDS = [
    "aadhaar", "pan card", "bank details", "account number",
    "otp", "upi", "passport", "documents before interview"
]

URGENCY_KEYWORDS = [
    "urgent hiring", "limited seats", "apply now", "immediate joining",
    "last chance", "selected immediately", "instant selection"
]

UNREALISTIC_PROMISE_KEYWORDS = [
    "no interview", "no experience needed", "easy money", "quick money",
    "guaranteed income", "earn from home", "work 1 hour"
]

RESPONSIBILITY_KEYWORDS = [
    "responsibilities", "duties", "role", "tasks", "work closely",
    "manage", "analyze", "develop", "support"
]

REQUIREMENT_KEYWORDS = [
    "requirements", "qualification", "skills", "experience",
    "knowledge", "degree", "preferred"
]

TRUSTED_SOURCE_KEYWORDS = [
    "official website", "career page", "careers page",
    "linkedin", "naukri", "indeed", "glassdoor", "company website"
]


def get_risk_level(score):
    if score >= 70:
        return "High"
    elif score >= 40:
        return "Medium"
    return "Low"


def extract_email_domains(text):
    emails = re.findall(r'[\w\.-]+@([\w\.-]+)', str(text))
    return [domain.lower() for domain in emails]


def has_url(text):
    text = str(text).lower()
    return "http://" in text or "https://" in text or "www." in text or ".com" in text


def analyze_content_quality(title, description, requirements, benefits):
    text = f"{title} {description} {requirements} {benefits}".lower()

    score = 0
    red_flags = []
    positive_signals = []

    word_count = len(text.split())

    if word_count < 60:
        score += 25
        red_flags.append("Job post has limited details and may be too generic")
    else:
        positive_signals.append("Job post contains enough descriptive information")

    if not any(word in text for word in RESPONSIBILITY_KEYWORDS):
        score += 20
        red_flags.append("Clear job responsibilities are not properly mentioned")
    else:
        positive_signals.append("Job responsibilities are mentioned")

    if not any(word in text for word in REQUIREMENT_KEYWORDS):
        score += 20
        red_flags.append("Requirements or qualifications are not clearly mentioned")
    else:
        positive_signals.append("Requirements or qualifications are mentioned")

    if any(word in text for word in URGENCY_KEYWORDS):
        score += 20
        red_flags.append("Urgency or pressure-based hiring language detected")

    if any(word in text for word in UNREALISTIC_PROMISE_KEYWORDS):
        score += 25
        red_flags.append("Unrealistic promises or easy income claims detected")

    if benefits.strip() != "":
        positive_signals.append("Benefits or compensation details are provided")

    score = max(0, min(100, score))

    return {
        "score": score,
        "risk_level": get_risk_level(score),
        "red_flags": red_flags,
        "positive_signals": positive_signals
    }


def analyze_company_identity(company_profile, description):
    text = f"{company_profile} {description}".lower()

    score = 0
    red_flags = []
    positive_signals = []

    if company_profile.strip() == "":
        score += 35
        red_flags.append("Company profile is missing")
    else:
        positive_signals.append("Company profile is provided")

    domains = extract_email_domains(text)

    if domains:
        for domain in domains:
            if domain in FREE_EMAIL_DOMAINS:
                score += 35
                red_flags.append(f"Free email domain detected: {domain}")
            else:
                positive_signals.append(f"Official-looking email domain detected: {domain}")
    else:
        score += 15
        red_flags.append("No contact email domain found for verification")

    if has_url(text):
        positive_signals.append("Website or URL is mentioned")
    else:
        score += 15
        red_flags.append("No website or official URL mentioned")

    if "pvt" in text or "ltd" in text or "private limited" in text or "inc" in text:
        positive_signals.append("Company legal identity keywords are present")

    score = max(0, min(100, score))

    return {
        "score": score,
        "risk_level": get_risk_level(score),
        "red_flags": red_flags,
        "positive_signals": positive_signals
    }


def analyze_contact_risk(description):
    text = str(description).lower()

    score = 0
    red_flags = []
    positive_signals = []

    if "whatsapp" in text:
        score += 25
        red_flags.append("WhatsApp-based application process detected")

    if any(word in text for word in PAYMENT_KEYWORDS):
        score += 40
        red_flags.append("Payment or fee request detected")

    if any(word in text for word in SENSITIVE_INFO_KEYWORDS):
        score += 35
        red_flags.append("Sensitive personal or financial information requested")

    if "interview" in text:
        positive_signals.append("Interview process is mentioned")
    else:
        score += 15
        red_flags.append("Interview process is not clearly mentioned")

    if "apply through" in text or "official website" in text or "career page" in text:
        positive_signals.append("Official application process is mentioned")
    else:
        score += 15
        red_flags.append("Official application process is unclear")

    score = max(0, min(100, score))

    return {
        "score": score,
        "risk_level": get_risk_level(score),
        "red_flags": red_flags,
        "positive_signals": positive_signals
    }


def analyze_source_verification(description):
    text = str(description).lower()

    score = 0
    red_flags = []
    positive_signals = []

    if any(source in text for source in TRUSTED_SOURCE_KEYWORDS):
        positive_signals.append("Trusted source or official career page is mentioned")
    else:
        score += 35
        red_flags.append("No trusted job source or official career page mentioned")

    if has_url(text):
        positive_signals.append("Job post includes a link for verification")
    else:
        score += 20
        red_flags.append("No verification link found in the job post")

    if "linkedin" in text or "naukri" in text or "indeed" in text:
        positive_signals.append("Known job platform is mentioned")

    score = max(0, min(100, score))

    return {
        "score": score,
        "risk_level": get_risk_level(score),
        "red_flags": red_flags,
        "positive_signals": positive_signals
    }


def run_verification_engine(title, description, company_profile, requirements, benefits):
    content_result = analyze_content_quality(
        title, description, requirements, benefits
    )

    company_result = analyze_company_identity(
        company_profile, description
    )

    contact_result = analyze_contact_risk(description)

    source_result = analyze_source_verification(description)

    return {
        "content": content_result,
        "company": company_result,
        "contact": contact_result,
        "source": source_result
    }