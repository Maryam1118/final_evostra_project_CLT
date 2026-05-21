import html
import time

import pandas as pd
import streamlit as st

from clinical_trial_api_model import match_patient


st.set_page_config(page_title="EVOASTRA Trial Intelligence", layout="wide")

DEMO_PROFILES = {
    "Breast Cancer Demo": {
        "condition": "breast cancer",
        "age": 45,
        "gender": "Female",
        "medications": "Tamoxifen",
        "notes": "No pregnancy. Prior surgery completed. Interested in interventional therapy trials.",
    },
    "Diabetes Demo": {
        "condition": "type 2 diabetes",
        "age": 60,
        "gender": "Male",
        "medications": "Metformin",
        "notes": "Stable outpatient care. History of hypertension.",
    },
    "Lung Cancer Demo": {
        "condition": "lung cancer",
        "age": 58,
        "gender": "Female",
        "medications": "Pembrolizumab",
        "notes": "Advanced disease. No active autoimmune disease reported.",
    },
}


def inject_css():
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at 10% 10%, rgba(29, 124, 255, 0.28), transparent 25rem),
                radial-gradient(circle at 85% 8%, rgba(138, 63, 252, 0.22), transparent 28rem),
                linear-gradient(180deg, #050b1f 0%, #071127 48%, #050b1f 100%);
            color: #edf4ff;
        }

        .block-container {
            padding-top: 1.4rem;
            padding-bottom: 2rem;
        }

        [data-testid="stSidebar"] {
            background: #071127;
            border-right: 1px solid #1e335f;
        }

        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] .stCaptionContainer {
            color: #edf4ff !important;
        }

        [data-testid="stSidebar"] input,
        [data-testid="stSidebar"] textarea,
        [data-testid="stSidebar"] div[data-baseweb="select"] > div {
            background-color: #ffffff !important;
            color: #111827 !important;
            border: 1px solid #d8e2f2 !important;
            border-radius: 10px !important;
        }

        [data-testid="stSidebar"] input::placeholder,
        [data-testid="stSidebar"] textarea::placeholder {
            color: #6b7280 !important;
            opacity: 1 !important;
        }

        [data-testid="stSidebar"] div[data-baseweb="select"] span {
            color: #111827 !important;
        }

        [data-testid="stSidebar"] button {
            color: #ffffff !important;
        }

        h1, h2, h3 {
            color: #edf4ff;
            letter-spacing: 0;
        }

        .topbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }

        .brand {
            display: flex;
            gap: 0.8rem;
            align-items: center;
        }

        .brand-mark {
            width: 44px;
            height: 44px;
            border-radius: 14px;
            display: grid;
            place-items: center;
            background: linear-gradient(135deg, #1d7cff, #8a3ffc);
            box-shadow: 0 0 24px rgba(29, 124, 255, 0.45);
            font-size: 1.35rem;
            font-weight: 900;
        }

        .brand-title {
            font-size: 1.15rem;
            font-weight: 850;
        }

        .brand-subtitle {
            color: #9fb2d4;
            font-size: 0.78rem;
        }

        .status-pill {
            padding: 0.45rem 0.75rem;
            border-radius: 999px;
            background: rgba(49, 208, 127, 0.11);
            border: 1px solid rgba(49, 208, 127, 0.35);
            color: #9df2c3;
            font-weight: 750;
            font-size: 0.82rem;
        }

        .hero {
            padding: 1.6rem;
            border: 1px solid #1e335f;
            border-radius: 16px;
            background:
                linear-gradient(120deg, rgba(29, 124, 255, 0.30), rgba(138, 63, 252, 0.22)),
                linear-gradient(180deg, rgba(16, 29, 64, 0.98), rgba(8, 17, 42, 0.98));
            box-shadow: 0 24px 60px rgba(0, 0, 0, 0.28);
            overflow: hidden;
            position: relative;
        }

        .hero:after {
            content: "";
            position: absolute;
            inset: 0;
            background:
                radial-gradient(circle at 75% 35%, rgba(49, 208, 127, 0.20), transparent 11rem),
                radial-gradient(circle at 85% 70%, rgba(29, 124, 255, 0.22), transparent 12rem);
            pointer-events: none;
        }

        .hero-content {
            position: relative;
            z-index: 1;
        }

        .badge-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-bottom: 0.9rem;
        }

        .badge {
            display: inline-block;
            padding: 0.34rem 0.68rem;
            border-radius: 999px;
            background: rgba(237, 244, 255, 0.08);
            border: 1px solid rgba(237, 244, 255, 0.16);
            color: #dce8ff;
            font-size: 0.78rem;
            font-weight: 700;
        }

        .hero-title {
            font-size: 2.35rem;
            line-height: 1.05;
            font-weight: 900;
            margin: 0 0 0.55rem 0;
            color: #ffffff;
        }

        .hero-copy {
            max-width: 48rem;
            color: #c5d4f0;
            line-height: 1.55;
            margin: 0;
        }

        .metric-card,
        .glass-card {
            padding: 1rem;
            border: 1px solid #1e335f;
            border-radius: 14px;
            background: linear-gradient(180deg, rgba(16, 29, 64, 0.96), rgba(9, 18, 43, 0.96));
            box-shadow: 0 16px 36px rgba(0, 0, 0, 0.18);
            min-height: 7.35rem;
        }

        .metric-label {
            color: #9fb2d4;
            font-size: 0.8rem;
            margin-bottom: 0.42rem;
        }

        .metric-value {
            color: #edf4ff;
            font-size: 1.85rem;
            font-weight: 900;
            line-height: 1.1;
        }

        .metric-note {
            color: #31d07f;
            font-size: 0.76rem;
            margin-top: 0.45rem;
        }

        .spotlight {
            padding: 1rem;
            border: 1px solid rgba(49, 208, 127, 0.32);
            border-radius: 16px;
            background:
                radial-gradient(circle at 15% 20%, rgba(49, 208, 127, 0.18), transparent 11rem),
                linear-gradient(180deg, rgba(13, 35, 45, 0.96), rgba(8, 18, 39, 0.96));
            min-height: 100%;
        }

        .donut {
            width: 158px;
            height: 158px;
            border-radius: 50%;
            margin: 0.3rem auto 0.8rem auto;
            display: grid;
            place-items: center;
            background: conic-gradient(#31d07f var(--score), rgba(255,255,255,0.10) 0);
            box-shadow: 0 0 30px rgba(49, 208, 127, 0.28);
        }

        .donut-inner {
            width: 112px;
            height: 112px;
            border-radius: 50%;
            background: #071127;
            display: grid;
            place-items: center;
            border: 1px solid #1e335f;
        }

        .donut-score {
            font-size: 2rem;
            font-weight: 950;
            color: #ffffff;
        }

        .trial-card {
            padding: 0.95rem 1rem;
            border: 1px solid #1e335f;
            border-radius: 14px;
            background: rgba(16, 29, 64, 0.78);
            margin-bottom: 0.75rem;
        }

        .trial-title {
            color: #edf4ff;
            font-weight: 800;
            margin-bottom: 0.25rem;
        }

        .trial-meta {
            color: #9fb2d4;
            font-size: 0.82rem;
            line-height: 1.45;
        }

        .score {
            color: #31d07f;
            font-size: 1.45rem;
            font-weight: 900;
            text-align: right;
            white-space: nowrap;
        }

        .tag {
            display: inline-block;
            padding: 0.22rem 0.52rem;
            border-radius: 999px;
            font-size: 0.72rem;
            font-weight: 750;
            margin-right: 0.35rem;
            margin-top: 0.55rem;
        }

        .tag-green {
            color: #9df2c3;
            background: rgba(49, 208, 127, 0.12);
            border: 1px solid rgba(49, 208, 127, 0.32);
        }

        .tag-orange {
            color: #ffd89a;
            background: rgba(245, 158, 11, 0.13);
            border: 1px solid rgba(245, 158, 11, 0.32);
        }

        .tag-blue {
            color: #b9d7ff;
            background: rgba(29, 124, 255, 0.13);
            border: 1px solid rgba(29, 124, 255, 0.32);
        }

        .explain-line {
            display: flex;
            justify-content: space-between;
            gap: 1rem;
            padding: 0.55rem 0;
            border-bottom: 1px solid rgba(158, 178, 212, 0.14);
            color: #c5d4f0;
            font-size: 0.88rem;
        }

        .explain-line strong {
            color: #edf4ff;
        }

        .footer-note {
            color: #9fb2d4;
            font-size: 0.8rem;
            text-align: center;
            padding: 1rem 0 0.2rem 0;
        }

        button[kind="primary"] {
            background: linear-gradient(90deg, #1d7cff, #8a3ffc);
            border: 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def esc(value):
    return html.escape(str(value if value is not None else ""))


def score_to_percent(score):
    return round(max(0, min(100, (float(score) / 1.6) * 100)))


def render_metric(label, value, note):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{esc(label)}</div>
            <div class="metric-value">{esc(value)}</div>
            <div class="metric-note">{esc(note)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_topbar():
    st.markdown(
        """
        <div class="topbar">
            <div class="brand">
                <div class="brand-mark">E</div>
                <div>
                    <div class="brand-title">EVOASTRA Clinical Trial Intelligence</div>
                    <div class="brand-subtitle">Smart patient-to-study matching with live public registry data</div>
                </div>
            </div>
            <div class="status-pill">ClinicalTrials.gov API Online</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_hero():
    st.markdown(
        """
        <div class="hero">
            <div class="hero-content">
                <div class="badge-row">
                    <span class="badge">Live API</span>
                    <span class="badge">Eligibility AI</span>
                    <span class="badge">Explainable Matching</span>
                    <span class="badge">Research Prototype</span>
                </div>
                <div class="hero-title">Clinical Trial Matching Command Center</div>
                <p class="hero-copy">
                    Search real studies, evaluate patient eligibility signals, rank the best clinical trials,
                    and generate a decision-support style match report in seconds.
                </p>
            </div>
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


def render_score_donut(score):
    st.markdown(
        f"""
        <div class="donut" style="--score:{score}%;">
            <div class="donut-inner">
                <div class="donut-score">{score}%</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_best_match(results):
    best = results.iloc[0]
    st.markdown('<div class="spotlight">', unsafe_allow_html=True)
    st.markdown("#### Best Match Spotlight")
    render_score_donut(int(best["MatchPercent"]))
    st.markdown(f"**{esc(best['BriefTitle'])}**")
    st.caption(f"{best['NCTId']} | {best['OverallStatus']} | {best['Condition']}")
    st.markdown(
        f"""
        <div class="explain-line"><span>Condition similarity</span><strong>{int(best["SemanticScore"] * 100)}%</strong></div>
        <div class="explain-line"><span>Age eligibility</span><strong>{"Passed" if best["AgeAllowed"] else "Needs Review"}</strong></div>
        <div class="explain-line"><span>Gender eligibility</span><strong>{"Passed" if best["GenderAllowed"] else "Needs Review"}</strong></div>
        <div class="explain-line"><span>Recommended action</span><strong>Manual clinical review</strong></div>
        """,
        unsafe_allow_html=True,
    )
    st.link_button("Open Trial Record", best["ClinicalTrialsUrl"], use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


def render_trial_cards(results):
    for position, row in enumerate(results.itertuples(index=False), start=1):
        age_tag = "Age Matched" if row.AgeAllowed else "Age Review"
        gender_tag = "Gender Matched" if row.GenderAllowed else "Gender Review"
        eligibility_tag = "High Fit" if row.MatchPercent >= 75 else "Review Fit"
        tag_class = "tag-green" if row.MatchPercent >= 75 else "tag-orange"

        st.markdown(
            f"""
            <div class="trial-card">
                <div style="display:flex; gap:1rem; justify-content:space-between; align-items:flex-start;">
                    <div>
                        <div class="trial-title">{position}. {esc(row.BriefTitle)}</div>
                        <div class="trial-meta">{esc(row.NCTId)} | {esc(row.OverallStatus)} | {esc(row.Condition)}</div>
                        <div class="trial-meta">Age: {esc(row.MinimumAge)} to {esc(row.MaximumAge)} | Gender: {esc(row.Gender)}</div>
                        <span class="tag {tag_class}">{eligibility_tag}</span>
                        <span class="tag tag-green">{age_tag}</span>
                        <span class="tag tag-blue">{gender_tag}</span>
                    </div>
                    <div class="score">{row.MatchPercent}%</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_explainability(results):
    overall = int(results["MatchPercent"].mean())
    semantic = int(results["SemanticScore"].mean() * 100)
    age_pass = int(results["AgeAllowed"].mean() * 100)
    gender_pass = int(results["GenderAllowed"].mean() * 100)

    st.markdown(
        f"""
        <div class="glass-card">
            <h4 style="margin-top:0;color:#edf4ff;">Model Confidence Breakdown</h4>
            <div class="explain-line"><span>Overall match confidence</span><strong>{overall}%</strong></div>
            <div class="explain-line"><span>Semantic text similarity</span><strong>{semantic}%</strong></div>
            <div class="explain-line"><span>Age rule pass rate</span><strong>{age_pass}%</strong></div>
            <div class="explain-line"><span>Gender rule pass rate</span><strong>{gender_pass}%</strong></div>
            <div class="explain-line"><span>Clinical decision support</span><strong>Use top 3 for review</strong></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def make_report(results, profile, elapsed, fetched_trials):
    lines = [
        "EVOASTRA Clinical Trial Match Report",
        "",
        f"Condition: {profile['condition']}",
        f"Age: {profile['age']}",
        f"Gender: {profile['gender']}",
        f"Medications: {profile['medications']}",
        f"Notes: {profile['notes']}",
        f"Trials analyzed: {fetched_trials}",
        f"API + model time: {elapsed:.2f}s",
        "",
        "Top Matches:",
    ]
    for idx, row in enumerate(results.itertuples(index=False), start=1):
        lines.extend(
            [
                f"{idx}. {row.BriefTitle}",
                f"   NCT ID: {row.NCTId}",
                f"   Match: {row.MatchPercent}%",
                f"   Status: {row.OverallStatus}",
                f"   URL: {row.ClinicalTrialsUrl}",
            ]
        )
    lines.append("")
    lines.append("Disclaimer: This prototype supports research review only and does not replace clinical judgment.")
    return "\n".join(lines)


def sync_profile(profile_name):
    profile = DEMO_PROFILES[profile_name]
    for key, value in profile.items():
        st.session_state[key] = value


inject_css()
render_topbar()
render_hero()

with st.sidebar:
    st.markdown("## EVOASTRA")
    st.caption("AI Clinical Trial Matcher")
    st.divider()

    profile_name = st.selectbox("Demo profile", list(DEMO_PROFILES.keys()))
    if st.button("Load Demo Profile", use_container_width=True):
        sync_profile(profile_name)

    if "condition" not in st.session_state:
        sync_profile("Breast Cancer Demo")

    condition = st.text_input("Condition", key="condition")
    age = st.number_input("Age", min_value=0, max_value=120, key="age")
    gender = st.selectbox("Gender", ["Female", "Male", "All"], key="gender")
    medications = st.text_input("Medications", key="medications")
    notes = st.text_area("Patient notes", key="notes")
    max_studies = st.slider("Trials to fetch from API", min_value=25, max_value=300, value=100, step=25)
    top_k = st.slider("Results to show", min_value=3, max_value=20, value=5)
    search_clicked = st.button("Find Matching Trials", type="primary", use_container_width=True)

    st.divider()
    st.caption("Live source: ClinicalTrials.gov API v2")

profile = {
    "condition": condition,
    "age": age,
    "gender": gender,
    "medications": medications,
    "notes": notes,
}

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
    st.session_state["profile"] = profile

results = st.session_state.get("results")
elapsed = st.session_state.get("elapsed", 0)
fetched_trials = st.session_state.get("fetched_trials", max_studies)
active_profile = st.session_state.get("profile", profile)

st.markdown("")

if results is None:
    st.markdown("### Executive Dashboard Preview")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric("API Status", "Ready", "Live registry connection")
    with c2:
        render_metric("Match Accuracy", "--", "Calculated after search")
    with c3:
        render_metric("Eligibility Score", "--", "Age and gender rules")
    with c4:
        render_metric("Trials Analyzed", "--", "Live API fetch")

    st.markdown("### What This Dashboard Will Show")
    preview_left, preview_right = st.columns([1.2, 1])
    with preview_left:
        st.markdown(
            """
            <div class="glass-card">
                <h4 style="margin-top:0;color:#edf4ff;">Decision Support Workflow</h4>
                <div class="explain-line"><span>1. Fetch public clinical trials</span><strong>API v2</strong></div>
                <div class="explain-line"><span>2. Convert trials into searchable text vectors</span><strong>TF-IDF</strong></div>
                <div class="explain-line"><span>3. Rank studies for the patient profile</span><strong>Similarity</strong></div>
                <div class="explain-line"><span>4. Check age and gender eligibility</span><strong>Rules</strong></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with preview_right:
        st.info("Load a demo profile or enter your own patient profile, then click Find Matching Trials.")
else:
    match_accuracy, eligibility_accuracy, best_match, api_latency, trial_count = build_dashboard_metrics(
        results, elapsed, fetched_trials
    )

    st.markdown("### Executive Metrics")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric("Overall Accuracy", f"{match_accuracy}%", "Average top-result confidence")
    with c2:
        render_metric("Best Match", f"{best_match}%", "Highest ranked trial")
    with c3:
        render_metric("Eligibility Accuracy", f"{eligibility_accuracy}%", "Age and gender compatibility")
    with c4:
        render_metric("API + Model Time", f"{api_latency}s", f"{trial_count} live trials analyzed")

    spotlight_col, chart_col = st.columns([0.9, 1.4])
    with spotlight_col:
        render_best_match(results)
    with chart_col:
        st.markdown("#### Trial Match Scoreboard")
        score_data = results[["NCTId", "MatchPercent"]].rename(columns={"MatchPercent": "Match %"})
        st.bar_chart(score_data, x="NCTId", y="Match %", color="#31d07f")

        status_data = results["OverallStatus"].value_counts().reset_index()
        status_data.columns = ["Trial Status", "Count"]
        st.markdown("#### Trial Status Distribution")
        st.bar_chart(status_data, x="Trial Status", y="Count", color="#1d7cff")

    left, right = st.columns([1.35, 1])
    with left:
        st.markdown("### Top Matching Trials")
        render_trial_cards(results)

    with right:
        st.markdown("### Explainability")
        render_explainability(results)

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
        st.line_chart(insight_data, x="Metric", y="Accuracy", color="#8a3ffc")

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

    report_text = make_report(results, active_profile, elapsed, fetched_trials).encode("utf-8")
    csv = results.to_csv(index=False).encode("utf-8")
    download_left, download_right = st.columns(2)
    with download_left:
        st.download_button(
            "Download Executive Match Report",
            report_text,
            file_name="evoastra_match_report.txt",
            mime="text/plain",
            use_container_width=True,
        )
    with download_right:
        st.download_button(
            "Download Results CSV",
            csv,
            file_name="clinical_trial_matches.csv",
            mime="text/csv",
            use_container_width=True,
        )

st.markdown(
    """
    <div class="footer-note">
        This system is for research support only and does not replace physician review, clinical judgment, or official trial-site confirmation.
    </div>
    """,
    unsafe_allow_html=True,
)
            
                        
            
