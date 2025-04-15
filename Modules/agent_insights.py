import pandas as pd
import re
import json
from textblob import TextBlob
from nltk.tokenize import sent_tokenize
from transformers import T5Tokenizer, T5ForConditionalGeneration

# Load FLAN-T5 model and tokenizer
model_name = "google/flan-t5-small"
tokenizer = T5Tokenizer.from_pretrained(model_name)
model = T5ForConditionalGeneration.from_pretrained(model_name)


def clean_comment(text):
    """
    Clean and normalize noisy system-generated comments.
    """
    if pd.isna(text) or not isinstance(text, str):
        return ""

    text = text.replace("nan", " ")
    text = re.sub(r'\S+@\S+|https?://\S+', '', text)
    text = re.sub(r'<.*?>', '', text)
    text = re.sub(r'\d{2}/\d{2}/\d{4}|\d{2}/[A-Za-z]{3}/\d{4}', '', text)
    text = re.sub(r'\b\d{1,2}:\d{2}\s*(AM|PM|am|pm)?\b', '', text)
    text = re.sub(r'\[[A-Z]+-\d+\]|\[IT-\d+\|?.*?\]', '', text)
    text = re.sub(r'^(hi|hello|dear)\b.*?(?=\n)', '', text, flags=re.IGNORECASE | re.MULTILINE)
    text = re.sub(r'thanks.*|regards.*|sincerely.*|best.*|cheers.*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'{[^}]+}|\[.*?\|.*?\]|[^\x00-\x7F]+|[*_“”"–—]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def extract_fields(text):
    prompt = f"""
### Task
You are an AI assistant for support teams. Extract structured intent from real customer messages only.

### Instruction
From the message below, extract:
- intent (what the user wants)
- target (what the issue or object is)
- timeframe (any date, urgency or time window)

If the message has no real customer content (like system messages), return empty strings.

### Format
Respond only in this JSON format:
{{"intent": "...", "target": "...", "timeframe": "..."}}

### Message
{text.strip()}
""".strip()

    input_ids = tokenizer(prompt, return_tensors="pt").input_ids
    output = model.generate(input_ids, max_length=100, num_beams=4, early_stopping=True)
    raw = tokenizer.decode(output[0], skip_special_tokens=True)

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"intent": "", "target": "", "timeframe": ""}


def summarize_comment_agentic(comment):
    if not isinstance(comment, str) or not comment.strip():
        return []

    sentences = sent_tokenize(comment)
    filtered = [s for s in sentences if len(s.split()) >= 4 and "ticket migrated" not in s.lower()]
    return [f"- {s.strip()}" for s in filtered[:6]]


def estimate_urgency(comment):
    urgent_terms = ['urgent', 'asap', 'immediately', 'today', 'tomorrow', 'by end of day', 'this week']
    comment = comment.lower() if isinstance(comment, str) else ''
    return min(sum(term in comment for term in urgent_terms), 3)


def estimate_seriousness(comment):
    keywords = ['missing', 'broken', 'issue', 'error', 'not working', 'problem']
    score = sum(k in comment.lower() for k in keywords)
    polarity = TextBlob(comment).sentiment.polarity if isinstance(comment, str) else 0
    return min(score + (1 if polarity < -0.3 else 0), 3)


def compute_priority_score(urgency, seriousness):
    score = urgency + seriousness
    if score >= 2:
        return "High"
    elif score >= 1:
        return "Medium"
    else:
        return "Low"


def agentic_summary_pipeline(row):
    comment = row.get("Consumer_Comments", "")
    summary = summarize_comment_agentic(comment)
    urgency = estimate_urgency(comment)
    seriousness = estimate_seriousness(comment)
    priority = compute_priority_score(urgency, seriousness)

    return pd.Series({
        "bullet_points": summary,
        "urgency": urgency,
        "seriousness": seriousness,
        "priority": priority
    })


def build_ticket_json(row):
    row['Consumer_Comments'] = clean_comment(row['Consumer_Comments'])
    extracted = extract_fields(row['Consumer_Comments'])

    return {
        "request_id": row.get('Issue_key', ""),
        "created_at": row.get('Created', ""),
        "customer_message": row.get('Consumer_Comments', ""),
        "intent": extracted.get("intent", ""),
        "target": extracted.get("target", ""),
        "timeframe": extracted.get("timeframe", ""),
        "status": row.get("Status", ""),
        "department": row.get("Relevant_Departments", ""),
        "assignee": row.get("Assignee", "")
    }
