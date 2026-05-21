import re
from functools import lru_cache

import pandas as pd
import requests
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors


BASE_URL = "https://clinicaltrials.gov/api/v2/studies"


def clean_text(value):
    if pd.isna(value):
        return ""
    raw_text = str(value)
    if "<" in raw_text and ">" in raw_text:
        text = BeautifulSoup(raw_text, "html.parser").get_text(" ")
    else:
        text = raw_text
    return re.sub(r"\s+", " ", text).strip()


def list_to_text(value):
    if isinstance(value, list):
        return "; ".join(str(item) for item in value)
    return value or ""


def age_to_years(value, default):
    if pd.isna(value) or str(value).strip().upper() in {"", "N/A", "NA"}:
        return default

    text = str(value).lower()
    match = re.search(r"(\d+)", text)
    if not match:
        return default

    number = int(match.group(1))
    if "month" in text:
        return round(number / 12, 2)
    if "week" in text:
        return round(number / 52, 2)
    if "day" in text:
        return round(number / 365, 2)
    return number


def flatten_study(study):
    protocol = study.get("protocolSection", {})
    identification = protocol.get("identificationModule", {})
    status = protocol.get("statusModule", {})
    description = protocol.get("descriptionModule", {})
    conditions = protocol.get("conditionsModule", {})
    design = protocol.get("designModule", {})
    eligibility = protocol.get("eligibilityModule", {})

    return {
        "NCTId": identification.get("nctId", ""),
        "BriefTitle": identification.get("briefTitle", ""),
        "OverallStatus": status.get("overallStatus", ""),
        "Condition": list_to_text(conditions.get("conditions", [])),
        "BriefSummary": description.get("briefSummary", ""),
        "StudyType": design.get("studyType", ""),
        "EligibilityCriteria": eligibility.get("eligibilityCriteria", ""),
        "Gender": eligibility.get("sex", ""),
        "MinimumAge": eligibility.get("minimumAge", ""),
        "MaximumAge": eligibility.get("maximumAge", ""),
    }


def download_trials(condition, max_studies=100):
    rows = []
    page_token = None

    while len(rows) < max_studies:
        params = {
            "query.cond": condition,
            "filter.overallStatus": "RECRUITING,NOT_YET_RECRUITING,ACTIVE_NOT_RECRUITING",
            "pageSize": min(100, max_studies - len(rows)),
            "format": "json",
        }
        if page_token:
            params["pageToken"] = page_token

        response = requests.get(BASE_URL, params=params, timeout=30)
        response.raise_for_status()
        payload = response.json()

        studies = payload.get("studies", [])
        rows.extend(flatten_study(study) for study in studies)

        page_token = payload.get("nextPageToken")
        if not page_token or not studies:
            break

    return pd.DataFrame(rows)


def preprocess_trials(trials):
    if trials.empty:
        return trials

    trials = trials.drop_duplicates(subset=["NCTId"]).copy()
    for column in ["BriefTitle", "Condition", "BriefSummary", "EligibilityCriteria", "Gender"]:
        trials[column] = trials[column].apply(clean_text)

    trials = trials[trials["EligibilityCriteria"].str.len() > 20].copy()
    trials["MinimumAgeYears"] = trials["MinimumAge"].apply(lambda value: age_to_years(value, 0))
    trials["MaximumAgeYears"] = trials["MaximumAge"].apply(lambda value: age_to_years(value, 120))
    trials["SearchText"] = (
        trials["BriefTitle"].fillna("")
        + " "
        + trials["Condition"].fillna("")
        + " "
        + trials["BriefSummary"].fillna("")
        + " "
        + trials["EligibilityCriteria"].fillna("")
    )
    return trials.reset_index(drop=True)


def build_model(trials):
    vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words="english",
        ngram_range=(1, 2),
        max_features=30000,
    )
    matrix = vectorizer.fit_transform(trials["SearchText"])
    index = NearestNeighbors(metric="cosine", algorithm="brute")
    index.fit(matrix)
    return vectorizer, index


def gender_allowed(patient_gender, trial_gender):
    trial = str(trial_gender).strip().upper()
    patient = str(patient_gender).strip().upper()
    return trial in {"", "ALL", "A", "ANY"} or trial == patient


def age_allowed(patient_age, min_age, max_age):
    try:
        age = float(patient_age)
        minimum = float(min_age) if str(min_age) else 0
        maximum = float(max_age) if str(max_age) else 120
    except ValueError:
        return True
    return minimum <= age <= maximum


@lru_cache(maxsize=8)
def get_cached_model(condition, max_studies):
    raw_trials = download_trials(condition, max_studies)
    trials = preprocess_trials(raw_trials)
    if trials.empty:
        raise ValueError("No usable trials were returned from ClinicalTrials.gov for this condition.")
    vectorizer, index = build_model(trials)
    return trials, vectorizer, index


def match_patient(age, gender, condition, medications="", notes="", max_studies=100, top_k=5):
    condition = condition.lower().strip()
    trials, vectorizer, index = get_cached_model(condition, int(max_studies))
    query = f"{age} {gender} {condition} {medications} {notes}"
    query_vector = vectorizer.transform([query])
    distances, indices = index.kneighbors(query_vector, n_neighbors=min(top_k * 4, len(trials)))

    rows = []
    for distance, trial_index in zip(distances[0], indices[0]):
        trial = trials.iloc[trial_index].copy()
        semantic_score = 1 - float(distance)
        rule_score = 0
        rule_score += 0.2 if age_allowed(age, trial["MinimumAgeYears"], trial["MaximumAgeYears"]) else -0.4
        rule_score += 0.2 if gender_allowed(gender, trial["Gender"]) else -0.4

        trial_condition = str(trial["Condition"]).lower()
        if any(token in trial_condition for token in condition.split()):
            rule_score += 0.2

        trial["SemanticScore"] = round(semantic_score, 4)
        trial["FinalScore"] = round(semantic_score + rule_score, 4)
        trial["AgeAllowed"] = age_allowed(age, trial["MinimumAgeYears"], trial["MaximumAgeYears"])
        trial["GenderAllowed"] = gender_allowed(gender, trial["Gender"])
        trial["ClinicalTrialsUrl"] = f"https://clinicaltrials.gov/study/{trial['NCTId']}"
        rows.append(trial)

    results = pd.DataFrame(rows).sort_values("FinalScore", ascending=False).head(top_k)
    columns = [
        "NCTId",
        "BriefTitle",
        "Condition",
        "OverallStatus",
        "Gender",
        "MinimumAge",
        "MaximumAge",
        "SemanticScore",
        "FinalScore",
        "AgeAllowed",
        "GenderAllowed",
        "ClinicalTrialsUrl",
    ]
    return results[columns]
