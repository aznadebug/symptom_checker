"""Symptom Checker Pro - web version (Streamlit).
Educational only. NOT a medical diagnosis.
Run locally: streamlit run app.py
"""
from datetime import datetime

import pandas as pd
import streamlit as st

# ---------------------------------------------------------------- DATA
CONDITIONS = {
    "Common Cold": {
        "symptoms": {"runny nose": 3, "sneezing": 3, "sore throat": 2,
                     "cough": 2, "mild fever": 1, "fatigue": 1},
        "advice": "Rest, drink fluids, and use over-the-counter relief."},
    "Influenza (Flu)": {
        "symptoms": {"high fever": 3, "body aches": 3, "fatigue": 2,
                     "cough": 2, "headache": 2, "chills": 3},
        "advice": "Rest and hydrate. See a doctor if high-risk or worsening."},
    "COVID-19": {
        "symptoms": {"high fever": 2, "cough": 3, "loss of smell": 4,
                     "fatigue": 2, "shortness of breath": 3, "sore throat": 1},
        "advice": "Take a test, isolate, and monitor your breathing."},
    "Allergies": {
        "symptoms": {"sneezing": 3, "runny nose": 2, "itchy eyes": 4,
                     "rash": 2, "cough": 1},
        "advice": "Avoid triggers; antihistamines may help."},
    "Migraine": {
        "symptoms": {"headache": 4, "nausea": 3, "light sensitivity": 4,
                     "dizziness": 2},
        "advice": "Rest in a dark, quiet room and stay hydrated."},
    "Food Poisoning": {
        "symptoms": {"nausea": 3, "vomiting": 4, "diarrhea": 4,
                     "stomach pain": 3, "mild fever": 1},
        "advice": "Replace fluids with oral rehydration. Seek care if severe."},
}
RED_FLAGS = {"shortness of breath", "chest pain"}
ALL_SYMPTOMS = sorted({s for c in CONDITIONS.values()
                       for s in c["symptoms"]} | RED_FLAGS)
SEVERITY = {"Mild": 0.6, "Moderate": 1.0, "Severe": 1.4}
RISK_COLORS = {"LOW": "#2e9e5b", "MODERATE": "#e0a100", "HIGH": "#d64545"}


# ---------------------------------------------------------------- LOGIC
def score_conditions(selected):
    """selected: {symptom: multiplier} -> sorted [(name, pct)]."""
    results = []
    for name, data in CONDITIONS.items():
        weights = data["symptoms"]
        total = sum(weights.values())
        matched = sum(w * selected[s] for s, w in weights.items()
                      if s in selected)
        pct = min(100.0, round(matched / total * 100, 1))
        if pct > 0:
            results.append((name, pct))
    return sorted(results, key=lambda x: x[1], reverse=True)


def assess_risk(selected, severities, results, age, days):
    """Combine several factors into LOW / MODERATE / HIGH."""
    points, reasons = 0, []
    if set(selected) & RED_FLAGS:
        points += 3
        reasons.append("red-flag symptom present")
    if severities.count("Severe") >= 3:
        points += 1
        reasons.append("multiple severe symptoms")
    if results and results[0][1] >= 60:
        points += 1
        reasons.append("strong match to a condition")
    if age < 5 or age > 65:
        points += 1
        reasons.append("age is a higher-risk group")
    if days > 7:
        points += 1
        reasons.append("symptoms lasting over a week")
    level = "HIGH" if points >= 3 else "MODERATE" if points == 2 else "LOW"
    return level, reasons


# ---------------------------------------------------------------- PAGE
st.set_page_config(page_title="Symptom Checker Pro", page_icon="🩺",
                   layout="centered")
st.title("🩺 Symptom Checker Pro")
st.caption("Educational tool only. Not a medical diagnosis. "
           "In an emergency, call your local emergency number.")

if "history" not in st.session_state:
    st.session_state.history = []
if "last" not in st.session_state:
    st.session_state.last = None

tab_check, tab_hist, tab_about = st.tabs(["Check", "History", "About"])

# ---- Check tab
with tab_check:
    c1, c2 = st.columns(2)
    age = c1.number_input("Age", min_value=0, max_value=120, value=25)
    days = c2.number_input("Days sick", min_value=0, max_value=60, value=1)

    chosen_titles = st.multiselect("Select your symptoms",
                                   [s.title() for s in ALL_SYMPTOMS])
    chosen = [t.lower() for t in chosen_titles]

    severities = {}
    if chosen:
        st.write("**Severity of each symptom**")
        for s in chosen:
            severities[s] = st.select_slider(
                s.title(), options=list(SEVERITY), value="Moderate",
                key=f"sev_{s}")

    if st.button("Analyze", type="primary", use_container_width=True):
        if not chosen:
            st.warning("Select at least one symptom.")
        else:
            selected = {s: SEVERITY[v] for s, v in severities.items()}
            results = score_conditions(selected)
            level, reasons = assess_risk(
                selected, list(severities.values()), results,
                int(age), int(days))
            st.session_state.last = (results, level, reasons)
            top = results[0] if results else ("None", 0)
            st.session_state.history.append({
                "Time": f"{datetime.now():%Y-%m-%d %H:%M}",
                "Age": int(age), "Days": int(days),
                "Symptoms": ", ".join(chosen),
                "Top match": top[0], "Match %": top[1], "Risk": level})

    if st.session_state.last:
        results, level, reasons = st.session_state.last
        st.markdown(
            f"<div style='background:{RISK_COLORS[level]};color:white;"
            "padding:12px;border-radius:8px;text-align:center;"
            f"font-size:22px;font-weight:bold'>RISK LEVEL: {level}</div>",
            unsafe_allow_html=True)
        st.write("")
        if results:
            st.subheader("Possible matches")
            for name, pct in results[:5]:
                st.progress(int(pct), text=f"{name}: {pct}%")
            st.info(f"**Advice for {results[0][0]}:** "
                    f"{CONDITIONS[results[0][0]]['advice']}")
        else:
            st.info("No condition matched. Consider seeing a doctor.")
        if reasons:
            st.write("**Risk factors:** " + "; ".join(reasons) + ".")
        if level == "HIGH":
            st.error("Please seek medical attention promptly.")

# ---- History tab
with tab_hist:
    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history[::-1])
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.download_button("Download history (CSV)",
                           df.to_csv(index=False), "history.csv",
                           "text/csv")
        if st.button("Clear history"):
            st.session_state.history = []
            st.rerun()
    else:
        st.write("No checks yet. Run an analysis on the Check tab.")
    st.caption("History is kept only for your current session.")

# ---- About tab
with tab_about:
    st.markdown("""
**How it works**
1. Each condition has symptoms with different weights.
2. Severity (Mild, Moderate, Severe) adjusts each symptom's weight.
3. Match % = weighted matched symptoms / total weight x 100.
4. Risk is rated from red flags, severity, match strength, age, and duration.

**Limitations:** rule-based, small set of conditions, not clinical advice.
""")
