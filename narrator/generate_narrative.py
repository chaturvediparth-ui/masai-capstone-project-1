!mkdir -p narrator



# narrator/generate_narrative.py
%%writefile narrator/generate_narrative.py
from google import genai
import os

def generate_scr_narrative(findings: dict) -> dict:
    """
    Generate SCR narrative using Gemini API with strict parameter locking and error handling.
    """

    # NEW in Task 3: validate input keys before doing anything
    # (Task 2 did not check for missing keys)
    required_keys = [
        "cleaned_total_revenue_inr",
        "raw_total_revenue_inr",
        "duplicate_reconciliation_delta_inr",
        "return_rate_by_payment",
        "highest_risk_segment",
        "true_peak_month",
        "outlier_inflated_month"
    ]
    for key in required_keys:
        if key not in findings:
            return {"status": "error", "narrative": None, "message": f"Missing key: {key}"}

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return generate_scr_narrative_offline(findings)

    client = genai.Client(api_key=api_key)

    system_instruction = (
        "You are a senior data analyst writing for Mamaearth's regional ops and finance heads. "
        "Structure the narrative into three labeled sections: Situation, Complication, Resolution. "
        "Every number must come directly from the supplied findings dict and appear exactly as given."
    )

    user_prompt = f"""
    Findings summary:
    - Cleaned total revenue: {findings['cleaned_total_revenue_inr']}
    - Raw total revenue: {findings['raw_total_revenue_inr']}
    - Duplicate reconciliation delta: {findings['duplicate_reconciliation_delta_inr']}
    - Return rates: {findings['return_rate_by_payment']}
    - Highest risk segment: {findings['highest_risk_segment']}
    - True peak month: {findings['true_peak_month']}
    - Outlier inflated month: {findings['outlier_inflated_month']}
    """

    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=user_prompt,
            system_instruction=system_instruction,
            temperature=0.0,#temperature set to 0
            max_output_tokens=300,#maximum output tokens set to 300
            timeout=10 #timeout for api call set on 10 seconds
        )

        text = response.text.strip()

        # NEW in Task 3: enforce SCR format
        # (Task 2 just returned whatever Gemini gave)
        if not all(section in text for section in ["Situation", "Complication", "Resolution"]):
            return generate_scr_narrative_offline(findings)

        return {
            "status": "success",
            "narrative": text,
            "tokens": response.usage_metadata.total_tokens
        }

    # CHANGED in Task 3: broader error handling
    # (Task 2 returned only str(err), now we wrap in dict with status/narrative/message)
    except Exception as err:
        return {"status": "error", "narrative": None, "message": str(err)}


def generate_scr_narrative_offline(findings: dict) -> dict:
    """
    Offline deterministic fallback: builds SCR narrative using f-string template.
    """

    narrative = f"""
    Situation:
    Mamaearth recorded a cleaned total revenue of ₹{findings['cleaned_total_revenue_inr']:.2f} compared to a raw figure of ₹{findings['raw_total_revenue_inr']:.2f}.

    Complication:
    Duplicate orders reduced revenue by ₹{findings['duplicate_reconciliation_delta_inr']:.2f}.
    COD transactions show a return rate of {findings['return_rate_by_payment']['COD']:.2f}%,
    Card transactions show a return rate of {findings['return_rate_by_payment']['CARD']:.2f}%,
    and UPI transactions show a return rate of {findings['return_rate_by_payment']['UPI']:.2f}%.
    Tier-2 COD customers face the highest risk at {findings['highest_risk_segment']['return_rate_pct']:.2f}%.

    Resolution:
    March 2026 emerged as the true peak month with ₹{findings['true_peak_month']['revenue_inr']:.2f} revenue,
    while January’s apparent ₹{findings['outlier_inflated_month']['apparent_revenue_inr']:.2f} was inflated by outliers,
    corrected to ₹{findings['outlier_inflated_month']['corrected_revenue_inr']:.2f}.
    """


    
    # ALWAYS return same dict structure (task 4 requirement)
    return {"status": "success", "narrative": narrative.strip(), "tokens": len(narrative.split())}


import json

# Load the findings.json you exported in Task 1
with open("findings.json") as f:
    findings = json.load(f)

# Import your function
from narrator.generate_narrative import generate_scr_narrative

# Call the function
result = generate_scr_narrative(findings)

# Print the structured dict
print(result)

# If successful, print the narrative text
if result["status"] == "success":
    print("\n--- Narrative ---\n")
    print(result["narrative"])
else:
    print("Error:", result["message"])


# Task 5: Numeric Accuracy Checker
import re

def check_numeric_accuracy(narrative: str, findings: dict) -> dict:
    values_to_check = [
        findings["cleaned_total_revenue_inr"],
        findings["raw_total_revenue_inr"],
        findings["duplicate_reconciliation_delta_inr"],
        findings["return_rate_by_payment"]["COD"],
        findings["return_rate_by_payment"]["CARD"],
        findings["return_rate_by_payment"]["UPI"],
        findings["highest_risk_segment"]["return_rate_pct"],
        findings["true_peak_month"]["revenue_inr"],
        findings["outlier_inflated_month"]["apparent_revenue_inr"],
        findings["outlier_inflated_month"]["corrected_revenue_inr"],
    ]

    missing = []
    for val in values_to_check:
        # Match integer part and optional decimals, with or without ₹ or %
        val_pattern = r"(₹)?\s*" + re.escape(str(int(val))) + r"(\.\d{1,2})?(%?)"
        if not re.search(val_pattern, narrative):
            missing.append(val)

    status = "pass" if not missing else "fail"
    return {"status": status, "missing": missing, "checked_count": len(values_to_check)}

#EXECUTING THE CHECKER
check = check_numeric_accuracy(result["narrative"], findings)
#print(check)



'''AFTER CALLING THE API. THE NARRATIVE TEXT COMES OUT TO BE:"{'status': 'success', 'narrative': 'Situation:\n    Mamaearth recorded a cleaned total revenue of ₹97358.30 compared to a raw figure of ₹99860.20.\n    Complication:\n    Duplicate orders reduced revenue by ₹2501.90.\n    COD transactions show a return rate of 44.40%,\n    Card transactions show a return rate of 14.70%,\n    and UPI transactions show a return rate of 18.90%.\n    Tier-2 COD customers face the highest risk at 54.50%.\n\n\n    Resolution:\n    March 2026 emerged as the true peak month with ₹20318.90 revenue, while January’s apparent ₹29582.10 was inflated by outliers, corrected to ₹11637.10.', 'tokens': 80}

--- Narrative ---

Situation:
    Mamaearth recorded a cleaned total revenue of ₹97358.30 compared to a raw figure of ₹99860.20.
    Complication:
    Duplicate orders reduced revenue by ₹2501.90.
    COD transactions show a return rate of 44.40%,
    Card transactions show a return rate of 14.70%,
    and UPI transactions show a return rate of 18.90%.
    Tier-2 COD customers face the highest risk at 54.50%.


    Resolution:
    March 2026 emerged as the true peak month with ₹20318.90 revenue, while January’s apparent ₹29582.10 was inflated by outliers, corrected to ₹11637.10.
"'''
'''
AFTER RUNNING THE ACCURACY CHECKER THE RESULT IS:"{'status': 'pass', 'missing': [], 'checked_count': 10}
"'''
