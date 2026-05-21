import time

import pandas as pd
import streamlit as st

from clinical_trial_api_model import match_patient


st.set_page_config(page_title="EVOASTRA Trial Matcher", layout="wide")


def inject_css():
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(29, 124, 255, 0.24), transparent 32rem),
                radial-gradient(circle at top right, rgba(138, 63, 252, 0.24), transparent 30rem),
                #050b1f;
            color: #edf4ff;
        }

        [data-testid="stSidebar"] {
            background: #071127;
            border-right: 1px solid #1e335f;
        }

        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] .stCaptionContainer {
            color: #edf4ff !important;
        }

        [data-testid="stSidebar"] input,
        [data-testid="stSidebar"] textarea,
        [data-testid="stSidebar"] select,
        [data-testid="stSidebar"] div[data-baseweb="select"] > div {
            background-color: #ffffff !important;
            color: #111827 !important;
            border: 1px solid #d8e2f2 !important;
        }

        [data-testid="stSidebar"] input::placeholder,
        [data-testid="stSidebar"] textarea::placeholder {
            color: #6b7280 !important;
            opacity: 1 !important;
        }

        [data-testid="stSidebar"] input:focus,
        [data-testid="stSidebar"] textarea:focus {
            color: #111827 !important;
            background-color: #ffffff !important;
        }

        [data-testid="stSidebar"] div[data-baseweb="select"] span {
            color: #111827 !important;
        }

        [data-testid="stSidebar"] button {
            color: #ffffff !important;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }

        h1, h2, h3 {
            color: #edf4ff;
            letter-spacing: 0;
        }

        .hero {
            padding: 1.4rem 1.6rem;
            border: 1px solid #1e335f;
            border-radius: 14px;
            background:
                linear-gradient(120deg, rgba(29, 124, 255, 0.28), rgba(138, 63, 252, 0.2)),
                #0c1633;
            box-shadow: 0 20px 50px rgba(0, 0, 0, 0.25);
        }

        .hero-title {
            font-size: 2rem;
            font-weight: 800;
            margin: 0 0 0.35rem 0;
            color: #edf4ff;
        }

        .hero-copy {
            max-width: 48rem;
            color: #9fb2d4;
            line-height: 1.5;
            margin: 0;
        }

        .badge {
            display: inline-block;
            padding: 0.35rem 0.7rem;
            border-radius: 999px;
            background: rgba(49, 208, 127, 0.12);
            border: 1px solid rgba(49, 208, 127, 0.35);
            color: #9df2c3;
            font-size: 0.8rem;
            font-weight: 700;
            margin-bottom: 0.8rem;
        }

        .metric-card {
            padding: 1rem;
            border: 1px solid #1e335f;
            border-radius: 12px;
            background: linear-gradient(180deg, rgba(16, 29, 64, 0.95), rgba(9, 18, 43, 0.95));
            min-height: 7.2rem;
        }

        .metric-label {
            color: #9fb2d4;
            font-size: 0.82rem;
            margin-bottom: 0.45rem;
        }

        .metric-value {
            color: #edf4ff;
            font-size: 1.8rem;
            font-weight: 800;
            line-height: 1.1;
        }

        .metric-note {
            color: #31d07f;
            font-size: 0.78rem;
            margin-top: 0.45rem;
        }

        .trial-card {
            padding: 0.9rem 1rem;
            border: 1px solid #1e335f;
            border-radius: 12px;
            background: rgba(16, 29, 64, 0.78);
            margin-bottom: 0.75rem;
        }

        .trial-title {
            color: #edf4ff;
            font-weight: 750;
            margin-bottom: 0.25rem;
        }

        .trial-meta {
            color: #9fb2d4;
            font-size: 0.82rem;
        }

        .score {
            color: #31d07f;
            font-size: 1.4rem;
            font-weight: 850;
            text-align: right;
        }

        button[kind="primary"] {
            background: linear-gradient(90deg, #1d7cff, #8a3ffc);
            border: 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def score_to_percent(score):
    return round(max(0, min(100, (float(score) / 1.6) * 100)))


def render_metric(label, value, note):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def build_dashboard_metrics(results, elapsed_seconds, fetched_trials):
    match_accuracy = int(results["MatchPercent"].mean()) if not results.empty else 0
    eligibility_accuracy = int(
        ((results["AgeAllowed"].astype(int) + results["GenderAllowed"].astype(int)) / 2).mean() * 100
    )
    best_match = int(results["MatchPercent"].max()) if not results.empty else 0
    api_latency = round(elapsed_seconds, 2)
    return match_accuracy, eligibility_accuracy, best_match, api_latency, fetched_trials


def render_trial_cards(results):
    for position, row in enumerate(results.itertuples(index=False), start=1):
        st.markdown(
            f"""
            <div class="trial-card">
                <div style="display:flex; gap:1rem; justify-content:space-between; align-items:flex-start;">
                    <div>
                        <div class="trial-title">{position}. {row.BriefTitle}</div>
                        <div class="trial-meta">{row.NCTId} | {row.OverallStatus} | {row.Condition}</div>
                        <div class="trial-meta">Age: {row.MinimumAge} to {row.MaximumAge} | Gender: {row.Gender}</div>
                    </div>
                    <div class="score">{row.MatchPercent}%</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


inject_css()

with st.sidebar:
    st.markdown("## EVOASTRA")
    st.caption("AI Clinical Trial Matcher")
    st.divider()

    condition = st.text_input("Condition", value="breast cancer")
    age = st.number_input("Age", min_value=0, max_value=120, value=45)
    gender = st.selectbox("Gender", ["Female", "Male", "All"])
    medications = st.text_input("Medications", value="Tamoxifen")
    notes = st.text_area("Patient notes", value="No pregnancy. Prior surgery completed.")
    max_studies = st.slider("Trials to fetch from API", min_value=25, max_value=300, value=100, step=25)
    top_k = st.slider("Results to show", min_value=3, max_value=20, value=5)

    search_clicked = st.button("Find Matching Trials", type="primary", use_container_width=True)

    st.divider()
    st.caption("Live source: ClinicalTrials.gov API v2")

st.markdown(
    """
    <div class="hero">
        <div class="badge">AI powered live trial search</div>
        <div class="hero-title">Clinical Trial Matching Dashboard</div>
        <p class="hero-copy">
            Fetch live studies, compare eligibility rules, rank matching trials, and visualize model confidence
            from one Streamlit dashboard.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

if search_clicked:
    with st.spinner("Fetching live trials and building the matching model..."):
        start = time.perf_counter()
        try:
            results = match_patient(
                age=age,
                gender=gender,
                condition=condition,
                medications=medications,
                notes=notes,
                max_studies=max_studies,
                top_k=top_k,
            )
        except Exception as error:
            st.error(f"Could not fetch or match trials: {error}")
            st.stop()

        elapsed = time.perf_counter() - start

    results = results.copy()
    results["MatchPercent"] = results["FinalScore"].apply(score_to_percent)

    st.session_state["results"] = results
    st.session_state["elapsed"] = elapsed
    st.session_state["fetched_trials"] = max_studies

results = st.session_state.get("results")
elapsed = st.session_state.get("elapsed", 0)
fetched_trials = st.session_state.get("fetched_trials", max_studies)

if results is None:
    st.markdown("### Dashboard Preview")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        render_metric("API Status", "Ready", "Waiting for search")
    with c2:
        render_metric("Match Accuracy", "--", "Calculated after search")
    with c3:
        render_metric("Eligibility Score", "--", "Age and gender rules")
    with c4:
        render_metric("Trials Analyzed", "--", "Live API fetch")

    st.info("Enter a patient profile in the sidebar and click Find Matching Trials.")

else:
    match_accuracy, eligibility_accuracy, best_match, api_latency, trial_count = build_dashboard_metrics(
        results, elapsed, fetched_trials
    )

    st.markdown("### Performance Overview")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        render_metric("Overall Accuracy", f"{match_accuracy}%", "Average top-result match")
    with c2:
        render_metric("Best Match", f"{best_match}%", "Highest ranked trial")
    with c3:
        render_metric("Eligibility Accuracy", f"{eligibility_accuracy}%", "Age and gender compatibility")
    with c4:
        render_metric("API + Model Time", f"{api_latency}s", f"{trial_count} live trials analyzed")

    left, right = st.columns([1.35, 1])

    with left:
        st.markdown("### Top Matching Trials")
        render_trial_cards(results)

    with right:
        st.markdown("### Matching Insights")

        insight_data = pd.DataFrame(
            {
                "Metric": ["Overall", "Semantic", "Age", "Gender"],
                "Accuracy": [
                    match_accuracy,
                    int(results["SemanticScore"].mean() * 100),
                    int(results["AgeAllowed"].mean() * 100),
                    int(results["GenderAllowed"].mean() * 100),
                ],
            }
        )

        st.bar_chart(insight_data, x="Metric", y="Accuracy", color="#1d7cff")

        st.markdown("### Rank Confidence")
        rank_data = results[["NCTId", "MatchPercent"]].rename(columns={"MatchPercent": "Match %"})
        st.line_chart(rank_data, x="NCTId", y="Match %", color="#31d07f")

    st.markdown("### Detailed Results")

    st.dataframe(
        results[
            [
                "NCTId",
                "BriefTitle",
                "Condition",
                "OverallStatus",
                "Gender",
                "MinimumAge",
                "MaximumAge",
                "SemanticScore",
                "FinalScore",
                "MatchPercent",
                "AgeAllowed",
                "GenderAllowed",
                "ClinicalTrialsUrl",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )

    csv = results.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Download Matches CSV",
        csv,
        file_name="clinical_trial_matches.csv",
        mime="text/csv",
    )

    st.caption(
        "Accuracy values are prototype matching scores derived from TF-IDF similarity plus age and gender eligibility checks."
    )
            
   
