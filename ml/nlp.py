import re


def summarize_notes(text: str) -> str:
    # naive keyword-based summarizer for hackathon demo
    findings = []
    if re.search(r"fatigue|tired", text.lower()):
        findings.append("Patient reports fatigue")
    if re.search(r"adherence|non-compliance", text.lower()):
        findings.append("Possible medication non-adherence")
    if re.search(r"bp|blood pressure|hypertension", text.lower()):
        findings.append("Hypertension noted")
    if re.search(r"sugar|glucose|diabetes", text.lower()):
        findings.append("Diabetes-related issues present")
    return "; ".join(findings) if findings else "No significant insights extracted."
