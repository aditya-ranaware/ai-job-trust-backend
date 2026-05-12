# =====================================
# FINAL FLASK API (USER-FRIENDLY VERSION)
# =====================================

from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from scipy.sparse import hstack
from flask_cors import CORS

import pandas as pd
import joblib
import re
import sys
import os


# Fix import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import modules
from feature_engineering import create_features, get_feature_matrix
from company_validation import get_company_score
from trust_score import calculate_trust_score, classify_job
from file_extractor import extract_text_from_pdf, extract_text_from_image
from risk_intelligence import generate_professional_report

app = Flask(__name__)
CORS(app)
# =====================================
# LOAD MODEL
# =====================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

model_path = os.path.join(BASE_DIR, "../models/xgb_model.pkl")
vectorizer_path = os.path.join(BASE_DIR, "../models/vectorizer.pkl")

model = joblib.load(model_path)
vectorizer = joblib.load(vectorizer_path)


# =====================================
# TEXT CLEANING
# =====================================
def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'\W+', ' ', text)
    text = re.sub(r'\d+', ' ', text)
    return text


# =====================================
# ROUTE: HOME
# =====================================
@app.route('/')
def home():
    return "🚀 Fake Job Detection API Running"


# =====================================
# ROUTE: PREDICT
# =====================================
@app.route('/predict', methods=['POST'])
def predict():

    data = request.get_json()

    try:
        title = data.get("title", "")
        description = data.get("description", "")
        company_profile = data.get("company_profile", "")
        requirements = data.get("requirements", "")
        benefits = data.get("benefits", "")

        # Create DataFrame
        df = pd.DataFrame({
            'title': [title],
            'description': [description],
            'company_profile': [company_profile],
            'requirements': [requirements],
            'benefits': [benefits]
        })

        # Combine text
        df['text'] = df['title'] + " " + df['description'] + " " + \
                     df['company_profile'] + " " + df['requirements'] + " " + df['benefits']

        # Clean text
        df['clean_text'] = df['text'].apply(clean_text)

        # Feature Engineering
        df = create_features(df)
        X_extra = get_feature_matrix(df)

        suspicious_score = int(df['suspicious_score'][0])

        # TF-IDF
        X_text_vec = vectorizer.transform(df['clean_text'])

        # Combine features
        X_final = hstack([X_text_vec, X_extra.values])

        # ML Prediction
        pred = model.predict(X_final)[0]
        prob = model.predict_proba(X_final)[0][1]

        # Company Validation
        company_score = get_company_score(description, company_profile)
        report = generate_professional_report(
    ml_score=prob,
    company_score=company_score,
    suspicious_score=suspicious_score,
    title=title,
    description=description,
    company_profile=company_profile,
    requirements=requirements,
    benefits=benefits
)
        # Trust Score
        final_score = calculate_trust_score(prob, company_score, suspicious_score)
        final_label = classify_job(final_score)

        # =====================================
        # USER-FRIENDLY RESPONSE
        # =====================================

        if final_score > 0.7:
            decision = "🚨 High Risk Job"
            message = "This job looks suspicious."
            recommendation = "Avoid applying until the company and job details are verified."
        elif final_score > 0.4:
            decision = "⚠️ Medium Risk Job"
            message = "This job has some suspicious signals."
            recommendation = "Verify the company website, email domain, and job source before applying."
        else:
            decision = "✅ Safe Job"
            message = "This job looks mostly safe based on available details."
            recommendation = "You can proceed, but still verify the company before sharing personal information."

        # Reasons
        reasons = []

        if suspicious_score > 2:
            reasons.append("Suspicious language detected")

        if company_score > 0.5:
            reasons.append("Company details are missing or unverified")

        if prob > 0.7:
            reasons.append("Model detected high fraud probability")

        return jsonify(report)

    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/predict-pdf', methods=['POST'])
def predict_pdf():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"})

        file = request.files['file']

        if file.filename == '':
            return jsonify({"error": "No selected file"})

        filename = secure_filename(file.filename)

        upload_path = os.path.join("uploads", filename)
        file.save(upload_path)

        extracted_text = extract_text_from_pdf(upload_path)

        data = {
            "title": "",
            "description": extracted_text,
            "company_profile": "",
            "requirements": "",
            "benefits": ""
        }

        with app.test_request_context(json=data):
            return predict()

    except Exception as e:
        return jsonify({"error": str(e)})


@app.route('/predict-image', methods=['POST'])
def predict_image():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No image uploaded"})

        file = request.files['file']

        if file.filename == '':
            return jsonify({"error": "No selected image"})

        filename = secure_filename(file.filename)

        upload_path = os.path.join("uploads", filename)
        file.save(upload_path)

        extracted_text = extract_text_from_image(upload_path)

        if extracted_text.strip() == "":
            return jsonify({
                "error": "No readable text found in image. Please upload a clearer screenshot."
            })

        data = {
            "title": "",
            "description": extracted_text,
            "company_profile": "",
            "requirements": "",
            "benefits": ""
        }

        with app.test_request_context(json=data):
            return predict()

    except Exception as e:
        return jsonify({"error": str(e)})
    

# =====================================
# RUN APP
# =====================================
if __name__ == '__main__':
    app.run(debug=True)