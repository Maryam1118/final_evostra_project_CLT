# EVOASTRA Clinical Trial Matcher

Streamlit app that connects directly to ClinicalTrials.gov API v2, fetches live trial data, builds a TF-IDF matching model, and recommends trials for a patient profile.

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy On Streamlit Cloud

Upload only these files to GitHub:

```text
app.py
requirements.txt
README.md
clinical_trial_api_model.py
```

Then choose `app.py` as the Streamlit entry point.

## Note

This is an educational prototype. It is not medical advice and should not be used as the only basis for clinical trial enrollment decisions.
