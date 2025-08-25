# data_extractor/exporters/data_exporter.py

import os
import pandas as pd
import re

# at top of file, add imports

from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk

# Ensure the VADER lexicon is available
nltk.download('vader_lexicon', quiet=True)

# Initialize the analyzer once
VADER = SentimentIntensityAnalyzer()


def clean_reviews_text(reviews: list[str]) -> str:
    """Clean and format reviews to contain only text and numbers."""
    if not reviews:
        return "NIL"
    
    cleaned_reviews = []
    for review in reviews:
        # Remove special characters, keep only letters, numbers, spaces, and basic punctuation
        cleaned = re.sub(r'[^\w\s\.,!?\-()]', '', review)
        # Remove extra whitespace
        cleaned = ' '.join(cleaned.split())
        if cleaned.strip():
            cleaned_reviews.append(cleaned.strip())
    
    if not cleaned_reviews:
        return "NIL"
    
    # Join reviews with clear separators
    return " | ".join(cleaned_reviews)

def clean_text(text: str) -> str:
    # Remove unwanted characters like '*'
    cleaned = re.sub(r'[*]', '', text)
    # Fix missing spaces after punctuation (e.g., "Happy withDoctor friendliness" → "Happy with Doctor friendliness")
    cleaned = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', cleaned)
    # Normalize whitespace
    cleaned = ' '.join(cleaned.split())
    return cleaned

"""
def generate_pros_cons_summary(reviews: list[str], recommendation: int | None) -> str:
    
    Generate comprehensive pros and cons summary with recommendation analysis.
    
    if not reviews:
        if recommendation and recommendation > 0:
            return f"No detailed reviews available. Overall recommendation: {recommendation}% - {'Highly recommended' if recommendation >= 80 else 'Moderately recommended' if recommendation >= 60 else 'Mixed reviews'}"
        return "No reviews or recommendation data available."
    
    # Analyze reviews for positive and negative aspects
    pros = []
    cons = []
    
    positive_indicators = [
        'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'helpful', 
        'professional', 'satisfied', 'recommend', 'friendly', 'caring', 'experienced',
        'skilled', 'knowledgeable', 'effective', 'successful', 'comfortable', 'clean',
        'polite', 'understanding', 'patient', 'thorough', 'detailed', 'explained well'
    ]
    
    negative_indicators = [
        'bad', 'poor', 'terrible', 'awful', 'horrible', 'disappointing', 'unsatisfied',
        'rude', 'unprofessional', 'late', 'delay', 'waiting', 'expensive', 'costly',
        'rushed', 'not helpful', 'confused', 'unclear', 'problem', 'issue', 'complaint',
        'worst', 'never again', 'avoid', 'waste'
    ]
    
    for review in reviews:
        review_lower = review.lower()
        
        # Find positive aspects
        for indicator in positive_indicators:
            if indicator in review_lower:
                # Extract sentence containing the positive indicator
                sentences = review.split('.')
                for sentence in sentences:
                    if indicator in sentence.lower():
                        pros.append(sentence.strip())
                        break
        
        # Find negative aspects
        for indicator in negative_indicators:
            if indicator in review_lower:
                # Extract sentence containing the negative indicator
                sentences = review.split('.')
                for sentence in sentences:
                    if indicator in sentence.lower():
                        cons.append(sentence.strip())
                        break
    
    # Remove duplicates and limit
    pros = list(dict.fromkeys([p for p in pros if p]))[:3]
    cons = list(dict.fromkeys([c for c in cons if c]))[:2]
    
    # Build summary
    summary_parts = []
    
    if pros:
        summary_parts.append("PROS: " + "; ".join(pros))
    
    if cons:
        summary_parts.append("CONS: " + "; ".join(cons))
    
    # Add recommendation analysis
    if recommendation is not None:
        if recommendation >= 90:
            rec_text = "HIGHLY RECOMMENDED - Excellent patient satisfaction"
        elif recommendation >= 80:
            rec_text = "STRONGLY RECOMMENDED - Very good patient satisfaction"
        elif recommendation >= 70:
            rec_text = "RECOMMENDED - Good patient satisfaction"
        elif recommendation >= 60:
            rec_text = "MODERATELY RECOMMENDED - Above average satisfaction"
        elif recommendation >= 50:
            rec_text = "AVERAGE - Mixed patient feedback"
        else:
            rec_text = "BELOW AVERAGE - Consider other options"
        
        summary_parts.append(f"RECOMMENDATION: {recommendation}% - {rec_text}")
    
    if not summary_parts:
        return "Limited review information available for analysis."
    
    return " || ".join(summary_parts)
"""
"""
def generate_pros_cons_summary(reviews: list[str], recommendation: int | None) -> str:
    
    Use VADER sentiment scores to create a pros/cons summary:
      • Positive reviews (compound ≥ 0.05): PROS only
      • Negative reviews (compound ≤ -0.05): CONS only
      • Otherwise: MIXED with top 2 from each side
    
    if not reviews:
        return "No reviews available."

    sentences = []
    for r in reviews:
        # Split into sentences on punctuation
        parts = re.split(r'[\.!?]\s*', r)
        sentences.extend([p.strip() for p in parts if p.strip()])

    # Score each sentence
    scored = [(s, VADER.polarity_scores(s)['compound']) for s in sentences]
    # Sort
    positives = [s for s,c in sorted(scored, key=lambda x: -x[1]) if c > 0.1][:3]
    negatives = [s for s,c in sorted(scored, key=lambda x: x[1]) if c < -0.1][:3]

    compound = pd.Series([VADER.polarity_scores(s)['compound'] for s in reviews]).mean()

    summary_parts = []
    if compound >= 0.05:
        if positives:
            summary_parts.append("PROS: " + "; ".join(positives))
    elif compound <= -0.05:
        if negatives:
            summary_parts.append("CONS: " + "; ".join(negatives))
    else:
        if positives:
            summary_parts.append("PROS: " + "; ".join(positives[:2]))
        if negatives:
            summary_parts.append("CONS: " + "; ".join(negatives[:2]))
        if not (positives or negatives):
            summary_parts.append("MIXED feedback.")

    # Recommendation narrative
    if recommendation is not None:
        if recommendation >= 85:
            rec_text = "Highly recommended"
        elif recommendation >= 70:
            rec_text = "Recommended"
        elif recommendation >= 50:
            rec_text = "Average"
        else:
            rec_text = "Not recommended"
        summary_parts.append(f"RECOMMENDATION: {recommendation}% — {rec_text}")

    return " || ".join(summary_parts)
"""
"""
def generate_pros_cons_summary(reviews: list[str], recommendation: int | None) -> str:
    
    Generalized pros/cons summary:
    - Pros: up to 3 most positive sentences (compound ≥ 0.1)
    - Cons: up to 3 most negative sentences (compound ≤ -0.1), or 'none'
    - Recommendation: narrative based on recommendation%
    
    if not reviews:
        rec_part = _format_recommendation(recommendation)
        return f"PROS: none || CONS: none || {rec_part}"

    # Split reviews into sentences
    sentences = []
    for review in reviews:
        parts = re.split(r'[\.!?]\s*', review)
        sentences.extend([p.strip() for p in parts if p.strip()])

    # Score each sentence
    scored = [(s, VADER.polarity_scores(s)['compound']) for s in sentences]

    # Select pros and cons
    pros = [s for s, score in sorted(scored, key=lambda x: -x[1]) if score >= 0.1][:3]
    cons = [s for s, score in sorted(scored, key=lambda x: x[1]) if score <= -0.1][:3]

    # Ensure defaults
    if not pros:
        pros = ["none"]
    if not cons:
        cons = ["none"]

    # Build parts
    pros_part = "PROS: " + "; ".join(pros)
    cons_part = "CONS: " + "; ".join(cons)
    rec_part  = _format_recommendation(recommendation)

    return f"{pros_part} || {cons_part} || {rec_part}"
"""
"""
def generate_pros_cons_summary(reviews: list[str], recommendation: int | None) -> str:
    
    Improved generalized summary:
    - Extract pros from 'Happy with' segments cleanly
    - Extract cons by filtering more carefully
    - Provide default 'none' if no pros or cons
    
    pros = []
    cons = []
    
    for review in reviews:
        cleaned_review = clean_text(review)
        
        # Extract pros: look for "Happy with" and capture meaningful phrases afterwards
        if "happy with" in cleaned_review.lower():
            # capture text after 'Happy with'
            match = re.search(r'Happy with\s*([^\|\.]+)', cleaned_review, flags=re.I)
            if match:
                pros_text = match.group(1)
                # Split by common delimiters or known tags
                for phrase in re.split(r'[,;:\-\|]', pros_text):
                    phrase = phrase.strip()
                    if phrase and phrase.lower() != "none":
                        pros.append(phrase)
        
        # Extract cons: look for negative sentiment phrases 
        # Here, explicitly filter out known positive segments and extract possible negatives
        neg_phrases = [
            "doesnt", "doesn't", "avoid", "rush", "poor", "bad", "late", "unprofessional", "complain",
            "problem", "worst", "delay", "disappoint", "not good"
        ]
        if any(neg in cleaned_review.lower() for neg in neg_phrases):
            # Extract sentences containing neg_phrases
            sentences = re.split(r'(?<=[.!?])\s+', cleaned_review)
            for s in sentences:
                if any(neg in s.lower() for neg in neg_phrases):
                    cons.append(s.strip())
    
    # Remove duplicates and limit
    pros = list(dict.fromkeys(pros))[:3] if pros else ["none"]
    cons = list(dict.fromkeys(cons))[:3] if cons else ["none"]

    # Recommendation narrative
    rec_text = "No recommendation data"
    if recommendation is not None:
        pct = float(recommendation)
        if pct >= 85:
            rec_text = "Highly recommended"
        elif pct >= 70:
            rec_text = "Recommended"
        elif pct >= 50:
            rec_text = "Average recommendation"
        else:
            rec_text = "Not recommended"
        rec_text = f"{pct:.1f}% — {rec_text}"

    return (
        f"PROS: {', '.join(pros)} || CONS: {', '.join(cons)} || RECOMMENDATION: {rec_text}"
    )

def _format_recommendation(recommendation: int | None) -> str:
    Helper to format recommendation narrative.
    if recommendation is None:
        return "RECOMMENDATION: none"
    pct = recommendation
    if pct >= 85:
        label = "Highly recommended"
    elif pct >= 70:
        label = "Recommended"
    elif pct >= 50:
        label = "Average recommendation"
    else:
        label = "Not recommended"
    return f"RECOMMENDATION: {pct}% — {label}"
"""

import re
import pandas as pd
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Create VADER analyzer instance once globally
VADER = SentimentIntensityAnalyzer()

"""def generate_pros_cons_summary(reviews: list[str], recommendation: int | None) -> str:
    
    - Analyze reviews sentence-wise for sentiment.
    - If no negatives, CONS: none, use given recommendation.
    - If negatives present, CONS show those negatives and recommendation adjusted to 40-60%.
    - PROS extracted from positive sentences.
    
    if not reviews:
        rec_text = _format_recommendation(recommendation)
        return f"PROS: none || CONS: none || {rec_text}"
    
    sentences = []
    for review in reviews:
        parts = re.split(r'[\.!?]\s*', review)
        sentences.extend([p.strip() for p in parts if p.strip()])
    
    scored = [(s, VADER.polarity_scores(s)['compound']) for s in sentences]
    
    pros = [s for s, score in sorted(scored, key=lambda x: -x[1]) if score >= 0.1][:3]
    cons = [s for s, score in sorted(scored, key=lambda x: x[1]) if score <= -0.1][:3]
    
    # If no pros found, set default none
    if not pros:
        pros = ["none"]
    
    # Adjust recommendation if negatives found
    recom_value = recommendation if recommendation is not None else 0
    if cons and cons != ["none"]:
        # Adjust recommendation to mid (e.g., 50%), override if original was higher
        if recom_value > 60 or recom_value < 40:
            recom_value = 50
    else:
        # No negatives, cons none
        cons = ["none"]
    
    rec_text = _format_recommendation(recom_value)
    
    pros_part = "PROS: " + "; ".join(pros)
    cons_part = "CONS: " + "; ".join(cons)
    rec_part = f"RECOMMENDATION: {rec_text}"
    
    return f"{pros_part} || {cons_part} || {rec_part}"
"""

def generate_pros_cons_summary(reviews: list[str], recommendation: int | None) -> str:
    """
    - Analyze reviews sentence-wise for sentiment.
    - If no negatives, CONS: none, use given recommendation.
    - If negatives present, CONS show those negatives and recommendation adjusted to 40-60%.
    - PROS extracted from positive sentences.
    - If both PROS and CONS are 'none', show 'No recommendations available'.
    """
    if not reviews:
        rec_text = _format_recommendation(recommendation)
        return f"PROS: none || CONS: none || {rec_text}"
    
    sentences = []
    for review in reviews:
        parts = re.split(r'[\.!?]\s*', review)
        sentences.extend([p.strip() for p in parts if p.strip()])
    
    scored = [(s, VADER.polarity_scores(s)['compound']) for s in sentences]
    
    pros = [s for s, score in sorted(scored, key=lambda x: -x[1]) if score >= 0.1][:3]
    cons = [s for s, score in sorted(scored, key=lambda x: x[1]) if score <= -0.1][:3]
    
    if not pros:
        pros = ["none"]
    
    recom_value = recommendation if recommendation is not None else 0
    if cons and cons != ["none"]:
        if recom_value > 60 or recom_value < 40:
            recom_value = 50
    else:
        cons = ["none"]
    
    # New check: If both pros and cons are 'none'
    if pros == ["none"] and cons == ["none"]:
        return "No recommendations available."
    
    rec_text = _format_recommendation(recom_value)
    
    pros_part = "PROS: " + "; ".join(pros)
    cons_part = "CONS: " + "; ".join(cons)
    rec_part = f"RECOMMENDATION: {rec_text}"
    
    return f"{pros_part} || {cons_part} || {rec_part}"

def _format_recommendation(rec_score: int | float | None) -> str:
    if rec_score is None:
        return "none"
    pct = float(rec_score)
    if pct >= 85:
        return f"{pct:.1f}% — Highly recommended"
    elif pct >= 70:
        return f"{pct:.1f}% — Recommended"
    elif pct >= 50:
        return f"{pct:.1f}% — Average recommendation"
    elif pct >= 40:
        return f"{pct:.1f}% — Moderate caution"
    else:
        return f"{pct:.1f}% — Not recommended"

def _format_recommendation(rec_score: int | float | None) -> str:
    if rec_score is None:
        return "none"
    pct = float(rec_score)
    if pct >= 85:
        return f"{pct:.1f}% — Highly recommended"
    elif pct >= 70:
        return f"{pct:.1f}% — Recommended"
    elif pct >= 50:
        return f"{pct:.1f}% — Average recommendation"
    elif pct >= 40:
        return f"{pct:.1f}% — Moderate caution"
    else:
        return f"{pct:.1f}% — Not recommended"


def format_contact_number(contact_num) -> str:
    """Format contact number to prevent Excel scientific notation."""
    if pd.isna(contact_num) or contact_num == "" or contact_num is None:
        return ""
    
    # Convert to string and ensure it starts with + if it's a phone number
    contact_str = str(contact_num)
    
    # If it's already formatted correctly, return as is
    if contact_str.startswith('+91') and len(contact_str) == 13:
        return contact_str
    
    # If it's a 10-digit number, add +91
    if contact_str.isdigit() and len(contact_str) == 10:
        return f"+91{contact_str}"
    
    return contact_str

def format_rating(rating) -> str:
    """Format rating to show 'not available' for null/0/NIL values."""
    if pd.isna(rating) or rating == "" or rating is None or rating == "NIL" or rating == 0:
        return "not available"
    return str(rating)

def run_export(raw_json_path: str, structured_json_path: str, output_excel_path: str, test_limit: int = None) -> None:
    """Export structured JSON to Excel with custom formatting."""
    df = pd.read_json(structured_json_path)
    
    if test_limit:
        df = df.head(test_limit)
        print(f"Processing first {test_limit} records for testing...")

    # Build output DataFrame
    out = pd.DataFrame()
    
    # 1. Complete Address + Locality
    out["Complete Address"] = (
        df.get("complete_address", "").fillna("") + " " +
        df.get("locality", "").fillna("")
    ).str.strip()
    
    # 2. Doctor Name
    out["Doctor Name"] = df.get("doctor_name", "").fillna("")
    
    # 3. Specialty
    out["Specialty"] = df.get("specialty_raw", "").fillna("")
    
    # 4. Clinic/Hospital
    out["Clinic/Hospital"] = df.get("clinic_hospital_standardized", "").fillna("")
    
    # 5. Years of Experience
    out["Years of Experience"] = df.get("years_of_experience")
    
    # 6. Contact Number (formatted to prevent scientific notation)
    out["Contact Number"] = df.get("contact_number", "").apply(format_contact_number)
    
    # 7. Contact Email
    out["Contact Email"] = df.get("contact_email", "").fillna("")
    
    # 8. Ratings (formatted to show "not available" for null/0/NIL)
    out["Ratings"] = df.get("ratings", "").apply(format_rating)
    
    # 9. Reviews (cleaned text only)
    def format_reviews(row):
        count = row.get("review_count", 0)
        summaries = row.get("reviews_summary") or []
        
        if not count or count == 0 or not summaries:
            return "NIL"
        
        return clean_reviews_text(summaries)
    
    out["Reviews"] = df.apply(format_reviews, axis=1)
    
    # 10. Summary of Pros and Cons (renamed and improved)
    out["Summary of Pros and Cons (Summary of reviews), and recommendation"] = df.apply(
        lambda r: generate_pros_cons_summary(
            r.get("reviews_summary") or [], 
            r.get("recommendation_percent")
        ),
        axis=1
    )

    # Create Excel file
    os.makedirs(os.path.dirname(output_excel_path), exist_ok=True)
    
    with pd.ExcelWriter(output_excel_path, engine="openpyxl") as writer:
        out.to_excel(writer, sheet_name="Doctor Data", index=False)
        
        # Get the workbook and worksheet
        workbook = writer.book
        worksheet = writer.sheets["Doctor Data"]
        
        # Format contact number column as text to prevent scientific notation
        contact_col = None
        for idx, col_name in enumerate(out.columns):
            if col_name == "Contact Number":
                contact_col = idx + 1  # Excel columns are 1-indexed
                break
        
        if contact_col:
            # Set the entire contact number column format to text
            for row in range(2, len(out) + 2):  # Start from row 2 (after header)
                cell = worksheet.cell(row=row, column=contact_col)
                cell.number_format = '@'  # Text format
        
        # Auto-adjust column widths
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            
            adjusted_width = min(max_length + 2, 50)  # Cap at 50 for readability
            worksheet.column_dimensions[column_letter].width = adjusted_width

    print(f"Excel exported successfully to: {output_excel_path}")
    print(f"Total records exported: {len(out)}")
