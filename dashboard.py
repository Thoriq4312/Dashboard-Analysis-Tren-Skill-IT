import streamlit as st
import pandas as pd
import plotly.graph_objects as go

INDUSTRY_CSV  = "jd_eda.csv"
CANDIDATE_CSV = "cv_eda.csv"

st.set_page_config(
    page_title="ResuMy",
    page_icon="🔴",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
header[data-testid="stHeader"] {
    background-color: #111111 !important;
    border-bottom: 1px solid #2a2a2a !important;
    box-shadow: none !important;
}

header[data-testid="stHeader"]::before {
    content: "💻 Analisis Tren Skill IT";
    color: #888888 !important;
    font-size: 1.5rem !important;
    font-family: sans-serif;
    font-weight: 600;
    letter-spacing: 0.05em;
    position: absolute;
    left: 4.5rem;
    top: 50%;
    transform: translateY(-50%);
    pointer-events: none;
}

html, body, [data-testid="stApp"] {
    background-color: #111111 !important;
    color: #FFFFFF;
}
[data-testid="stSidebar"] {
    background-color: #1A1A1A !important;
    border-right: 1px solid #2a2a2a;
}

[data-testid="stAppViewContainer"] > .main > .block-container {
    padding-top: 5rem !important; 
}

div[data-testid="stSidebar"] .stButton > button {
    width: 100%;
    background: transparent;
    color: #CCCCCC;
    border: 1px solid #2e2e2e;
    border-radius: 6px;
    padding: 10px 14px;
    text-align: left;
    font-size: 0.85rem;
    letter-spacing: 0.02em;
    transition: all 0.2s ease;
    margin-bottom: 4px;
}
div[data-testid="stSidebar"] .stButton > button:hover {
    background: #E4002B22;
    border-color: #E4002B;
    color: #FFFFFF;
}

div[data-testid="stSidebar"] .stButton > button[aria-pressed="true"],
div[data-testid="stSidebar"] .stButton > button:focus {
    background: #E4002B !important;
    border-color: #E4002B !important;
    color: #FFFFFF !important;
}

[data-testid="stMetric"] {
    background: #1A1A1A;
    border: 1px solid #2a2a2a;
    border-radius: 10px;
    padding: 16px 20px;
}
[data-testid="stMetricLabel"] { color: #AAAAAA !important; font-size: 0.78rem; }
[data-testid="stMetricValue"] { color: #FFFFFF !important; font-size: 1.5rem; }
[data-testid="stMetricDelta"] { color: #E4002B !important; }

hr { border-color: #2a2a2a; }

.stSelectbox label, .stNumberInput label { color: #CCCCCC !important; font-size: 0.82rem; }

.section-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: #E4002B;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-bottom: 6px;
}
.page-title {
    font-size: 1.7rem;
    font-weight: 800;
    color: #FFFFFF;
    letter-spacing: -0.01em;
}
.page-subtitle {
    color: #888888;
    font-size: 0.88rem;
    margin-top: 2px;
    margin-bottom: 20px;
}

.insight-card {
    background: #1A1A1A;
    border-left: 4px solid #E4002B;
    border-radius: 0 8px 8px 0;
    padding: 14px 18px;
    margin-bottom: 10px;
    color: #CCCCCC;
    font-size: 0.88rem;
    line-height: 1.6;
}
.insight-card strong { color: #FFFFFF; }

.gap-card {
    background: linear-gradient(135deg, #1A0508 0%, #1A1A1A 100%);
    border: 1px solid #3a1018;
    border-top: 3px solid #E4002B;
    border-radius: 10px;
    padding: 20px 24px;
    margin-top: 8px;
}
.gap-card h4 {
    color: #E4002B;
    font-size: 0.8rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 8px;
}
.gap-card ul { color: #CCCCCC; font-size: 0.86rem; line-height: 1.7; padding-left: 18px; }
.gap-card li strong { color: #FFFFFF; }
.tag {
    display: inline-block;
    background: #E4002B22;
    color: #E4002B;
    border: 1px solid #E4002B44;
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    margin-right: 4px;
}
</style>
""", unsafe_allow_html=True)

@st.cache_data(show_spinner="Memuat data…")
def load_data():
    df_jd = pd.read_csv(INDUSTRY_CSV)
    df_cv = pd.read_csv(CANDIDATE_CSV)

    if "soft_skills" in df_jd.columns:
        df_jd["soft_skills"] = df_jd["soft_skills"].fillna("Tidak ada soft skills")

    id_col_jd = "job_id" if "job_id" in df_jd.columns else df_jd.columns[0]
    df_jd_skills = (
        df_jd[[id_col_jd, "industry_domain", "required_skills"]]
        .assign(skill=lambda x: x["required_skills"].str.split(","))
        .explode("skill")
    )
    df_jd_skills["skill"] = df_jd_skills["skill"].str.strip().str.lower()
    df_jd_skills = df_jd_skills[
        df_jd_skills["skill"].notna() & (df_jd_skills["skill"] != "")
    ]

    df_jd["skill_count"] = (
        df_jd["required_skills"]
        .str.split(",")
        .apply(lambda x: len([s for s in x if s.strip()]) if isinstance(x, list) else 0)
    )
    domain_avg = (
        df_jd.groupby("industry_domain")["skill_count"]
        .mean()
        .sort_values(ascending=True)
        .round(1)
        .reset_index()
        .rename(columns={"skill_count": "avg_skill"})
    )

    total_jd_freq = df_jd_skills["skill"].value_counts()
    domain_skill_freq = (
        df_jd_skills.groupby(["industry_domain", "skill"])
        .size()
        .reset_index(name="domain_count")
    )
    domain_skill_freq["global_count"] = domain_skill_freq["skill"].map(total_jd_freq)
    domain_skill_freq["specificity"] = (
        domain_skill_freq["domain_count"] / domain_skill_freq["global_count"]
    ).round(3)
    sig_jd = (
        domain_skill_freq[domain_skill_freq["domain_count"] >= 5]
        .sort_values("specificity", ascending=False)
        .groupby("industry_domain")
        .first()
        .reset_index()[["industry_domain", "skill", "domain_count", "specificity"]]
        .sort_values("specificity", ascending=True)
    )

    id_col_cv = "cv_id" if "cv_id" in df_cv.columns else df_cv.columns[0]
    df_cv_skills = (
        df_cv[[id_col_cv, "candidate_role", "candidate_skills"]]
        .assign(skill=lambda x: x["candidate_skills"].str.split(","))
        .explode("skill")
    )
    df_cv_skills["skill"] = df_cv_skills["skill"].str.strip().str.lower()
    df_cv_skills = df_cv_skills[
        df_cv_skills["skill"].notna() & (df_cv_skills["skill"] != "")
    ].reset_index(drop=True)

    df_cv["skill_count"] = df_cv["candidate_skills"].str.split(",").apply(
        lambda x: len([s for s in x if s.strip()])
    )
    role_avg = (
        df_cv.groupby("candidate_role")["skill_count"]
        .mean()
        .sort_values(ascending=True)
        .round(1)
        .reset_index()
        .rename(columns={"skill_count": "avg_skill"})
    )

    total_cv_freq = df_cv_skills["skill"].value_counts()
    role_skill_freq = (
        df_cv_skills.groupby(["candidate_role", "skill"])
        .size()
        .reset_index(name="role_count")
    )
    role_skill_freq["global_count"] = role_skill_freq["skill"].map(total_cv_freq)
    role_skill_freq["specificity"] = (
        role_skill_freq["role_count"] / role_skill_freq["global_count"]
    ).round(3)
    sig_cv = (
        role_skill_freq[role_skill_freq["role_count"] >= 3]
        .sort_values("specificity", ascending=False)
        .groupby("candidate_role")
        .first()
        .reset_index()[["candidate_role", "skill", "role_count", "specificity"]]
        .sort_values("specificity", ascending=True)
    )

    jd_freq = df_jd_skills["skill"].value_counts().reset_index()
    jd_freq.columns = ["skill", "jd_count"]
    cv_freq = df_cv_skills["skill"].value_counts().reset_index()
    cv_freq.columns = ["skill", "cv_count"]
    gap_df = pd.merge(jd_freq, cv_freq, on="skill", how="inner")
    gap_df["jd_pct"] = (gap_df["jd_count"] / gap_df["jd_count"].sum()) * 100
    gap_df["cv_pct"] = (gap_df["cv_count"] / gap_df["cv_count"].sum()) * 100
    gap_df["gap_score"] = ((gap_df["cv_pct"] / gap_df["jd_pct"]).round(5)) * 100
    gap_df["gap_score"] = 100 - gap_df["gap_score"]
    gap_df = gap_df[gap_df["gap_score"] > 0]

    return {
        "df_jd": df_jd,
        "df_cv": df_cv,
        "df_jd_skills": df_jd_skills,
        "df_cv_skills": df_cv_skills,
        "domain_avg": domain_avg,
        "sig_jd": sig_jd,
        "role_avg": role_avg,
        "sig_cv": sig_cv,
        "gap_df": gap_df,
    }

ACCENT     = "#E4002B"
ACCENT_DIM = "#7a0016"
BG_PLOT    = "#161616"
GRID_COLOR = "#2a2a2a"
TEXT_COLOR = "#CCCCCC"

PLOTLY_LAYOUT = dict(
    paper_bgcolor=BG_PLOT,
    plot_bgcolor=BG_PLOT,
    font=dict(color=TEXT_COLOR, family="Inter, sans-serif", size=12),
    margin=dict(l=0, r=0, t=40, b=0),
    xaxis=dict(
        gridcolor=GRID_COLOR, gridwidth=1,
        zeroline=False, showline=False, tickcolor=TEXT_COLOR,
    ),
    yaxis=dict(
        gridcolor="rgba(0,0,0,0)", zeroline=False,
        showline=False, tickcolor=TEXT_COLOR,
    ),
    hoverlabel=dict(
        bgcolor="#1e1e1e", bordercolor=ACCENT,
        font=dict(color="#FFFFFF", size=12),
    ),
)


def hbar_chart(
    y_labels, x_vals, title,
    text_labels=None,
    reversed_axis=False,
    bar_color=ACCENT,
    height=420,
    x_title="",
):

    fig = go.Figure()

    hover_text = [
        f"<b>{lbl.title()}</b><br>{x:.2f}" if text_labels is None
        else f"<b>{lbl.title()}</b><br>{txt}"
        for lbl, x, txt in zip(
            y_labels, x_vals,
            text_labels if text_labels else [""]*len(y_labels)
        )
    ]

    fig.add_trace(go.Bar(
        y=y_labels,
        x=x_vals,
        orientation="h",
        marker=dict(
            color=bar_color,
            line=dict(width=0),
        ),
        text=text_labels,
        textposition="outside",
        textfont=dict(color=TEXT_COLOR, size=10),
        hovertemplate="%{customdata}<extra></extra>",
        customdata=hover_text,
    ))

    layout = {**PLOTLY_LAYOUT}
    layout["title"] = dict(
        text=f"<b>{title}</b>",
        font=dict(color="#FFFFFF", size=14),
        x=0,
        xanchor="left",
    )
    layout["height"] = height
    layout["xaxis"]["title"] = x_title
    layout["xaxis"]["title_font"] = dict(color="#888888", size=11)
    layout["bargap"] = 0.35

    if reversed_axis:
        layout["yaxis"]["side"] = "right"
        layout["xaxis"]["autorange"] = "reversed"

    fig.update_layout(**layout)
    return fig


def make_top_n_chart(skills_df, role_col, selected_role, top_n, df_raw, id_col, title):
    data = (
        skills_df[skills_df[role_col] == selected_role]
        .groupby("skill").size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )
    n = min(top_n, len(data))
    data = data.head(n).sort_values("count", ascending=True)

    n_records = df_raw[df_raw[role_col] == selected_role].shape[0]
    pct = (data["count"] / n_records * 100).round(1)
    text_labels = [f"{c} ({p:.0f}%)" for c, p in zip(data["count"], pct)]

    return hbar_chart(
        y_labels=data["skill"].str.title().tolist(),
        x_vals=data["count"].tolist(),
        title=title,
        text_labels=text_labels,
        height=max(320, n * 52 + 80),
    )


def make_jumlah_skill_chart(avg_df, role_col, avg_col, title, reversed_axis=False):
    labels   = avg_df[role_col].tolist()
    values   = avg_df[avg_col].tolist()
    texts    = [f"{v}" for v in values]
    h        = max(400, len(labels) * 28 + 80)
    return hbar_chart(
        y_labels=labels,
        x_vals=values,
        title=title,
        text_labels=texts,
        reversed_axis=reversed_axis,
        height=h,
    )


def make_signature_chart(sig_df, role_col, title, reversed_axis=False):
    labels  = sig_df[role_col].tolist()
    values  = sig_df["specificity"].tolist()
    skills  = sig_df["skill"].str.title().tolist()
    texts   = [f'"{s}" ({v:.0%})' for s, v in zip(skills, values)]
    h       = max(400, len(labels) * 28 + 80)
    return hbar_chart(
        y_labels=labels,
        x_vals=values,
        title=title,
        text_labels=texts,
        reversed_axis=reversed_axis,
        bar_color=ACCENT_DIM,
        height=h,
        x_title="Specificity Score",
    )


def make_gap_facing_charts(gap_df, top_n):
    data = gap_df.sort_values("gap_score", ascending=False).head(top_n)
    data = data.sort_values("gap_score", ascending=True)

    labels   = data["skill"].str.title().tolist()
    jd_vals  = data["jd_pct"].round(3).tolist()
    cv_vals  = data["cv_pct"].round(3).tolist()
    gap_vals = data["gap_score"].round(2).tolist()
    h        = max(360, top_n * 52 + 80)

    fig_jd = go.Figure()
    fig_jd.add_trace(go.Bar(
        y=labels, x=jd_vals, orientation="h",
        marker=dict(color=ACCENT, line=dict(width=0)),
        text=[f"{v:.3f}  ▏Gap {g:.1f}%" for v, g in zip(jd_vals, gap_vals)],
        textposition="outside",
        textfont=dict(color=TEXT_COLOR, size=10),
        hovertemplate="<b>%{y}</b><br>Industry: %{x:.3f}%<extra></extra>",
    ))
    jd_layout = {**PLOTLY_LAYOUT,
                 "height": h,
                 "bargap": 0.38,
                 "title": dict(text="<b>🏭 Industry Skill Demand</b>",
                               font=dict(color="#FFFFFF", size=14), x=0)}
    fig_jd.update_layout(**jd_layout)

    fig_cv = go.Figure()
    fig_cv.add_trace(go.Bar(
        y=labels, x=cv_vals, orientation="h",
        marker=dict(color="#555555", line=dict(width=0)),
        text=[f"{v:.3f}  ▏Gap {g:.1f}%" for v, g in zip(cv_vals, gap_vals)],
        textposition="outside",
        textfont=dict(color=TEXT_COLOR, size=10),
        hovertemplate="<b>%{y}</b><br>Candidate: %{x:.3f}%<extra></extra>",
    ))
    cv_layout = {**PLOTLY_LAYOUT,
                 "height": h,
                 "bargap": 0.38,
                 "yaxis": {**PLOTLY_LAYOUT["yaxis"], "side": "right"},
                 "xaxis": {**PLOTLY_LAYOUT["xaxis"], "autorange": "reversed"},
                 "title": dict(text="<b>👤 Candidate Skill Supply</b>",
                               font=dict(color="#FFFFFF", size=14), x=0)}
    fig_cv.update_layout(**cv_layout)

    return fig_jd, fig_cv

with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 16px 0 8px 0;'>
        <div style='font-size:2.4rem; margin-bottom:4px;'>ResuMy</div>
        <div style='font-size:1.1rem; font-weight:800; color:#E4002B;
                    letter-spacing:0.08em; text-transform:uppercase;'>
            CC26-PSU006
        </div>
        <div style='font-size:0.7rem; color:#555555; margin-top:4px;
                    letter-spacing:0.06em; text-transform:uppercase;'>
            DBS Coding Camp · Capstone
        </div>
    </div>
    <hr style='border-color:#2a2a2a; margin: 10px 0 16px 0;'>
    """, unsafe_allow_html=True)

    st.markdown("<div style='color:#888;font-size:0.72rem;letter-spacing:0.08em;"
                "text-transform:uppercase;margin-bottom:8px;'>Navigasi</div>",
                unsafe_allow_html=True)

    if "page" not in st.session_state:
        st.session_state.page = "industri"

    pages = {
        "industri":   "📊  Tren Kebutuhan Industri",
        "kandidat":   "👤  Karakteristik Kandidat",
        "gap":        "⚡  Analisis Gap Skill",
    }
    for key, label in pages.items():
        if st.button(label, key=f"nav_{key}",
                     use_container_width=True):
            st.session_state.page = key

    st.markdown("<hr style='border-color:#2a2a2a; margin:16px 0;'>", unsafe_allow_html=True)

try:
    D = load_data()
except FileNotFoundError as e:
    st.error(f"❌ **File tidak ditemukan:** `{e.filename}`  \n"
             f"Perbarui konstanta `INDUSTRY_CSV` / `CANDIDATE_CSV` "
             f"di bagian atas script sesuai lokasi file CSV-mu.")
    st.stop()
except Exception as e:
    st.error(f"❌ **Error saat memuat data:** {e}")
    st.stop()

page = st.session_state.page

if page == "industri":
    header_container = st.container()
    with header_container:
        st.markdown("""
            <style>
            div[data-testid="stVerticalBlock"] > div:has(div.page-title) {
                position: -webkit-sticky;
                position: sticky;
                top: 0rem;
                background-color: #111111;
                z-index: 999;
                padding-top: 2rem;
                padding-bottom: 0.5rem;
                margin-top: -4rem;
            }
            </style>
        """, unsafe_allow_html=True)

        st.markdown('<div class="page-title">📊 Tren Kebutuhan Industri</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle" style="font-size:1.2rem";>Pertanyaan Bisnis 1: Skill apa yang paling dibutuhkan industri per role?</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Role Industri",  D["df_jd"]["industry_domain"].nunique())
    col2.metric("Total Job Postings",   f"{len(D['df_jd']):,}")
    col3.metric("Unique Skills",        D["df_jd_skills"]["skill"].nunique())

    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown('<div class="section-title" style="text-align: center;">🔥 Top Skill per Role</div>', unsafe_allow_html=True)

    ctrl1, ctrl2 = st.columns([3, 1])
    with ctrl1:
        domains = sorted(D["df_jd"]["industry_domain"].unique())
        selected_domain = st.selectbox("Pilih Role Industri", domains,
                                       label_visibility="collapsed")
    with ctrl2:
        top_n_jd = st.selectbox("Top N", [3, 5, 10], index=1,
                                 label_visibility="collapsed")

    fig_top_jd = make_top_n_chart(
        D["df_jd_skills"], "industry_domain",
        selected_domain, top_n_jd,
        D["df_jd"], "job_id" if "job_id" in D["df_jd"].columns else D["df_jd"].columns[0],
        f"Top {top_n_jd} Skill {selected_domain}",
    )
    fig_top_jd.update_layout(
    title_x=0.5,
    title_xanchor='center'
    )
    st.plotly_chart(fig_top_jd, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown('<div class="section-title" style="text-align: center;">📋 Ringkasan Semua Role</div>', unsafe_allow_html=True)

    col_left, col_right = st.columns(2)

    with col_left:
        fig_jumlah_jd = make_jumlah_skill_chart(
            D["domain_avg"], "industry_domain", "avg_skill",
            "Rata-Rata Jumlah Skill per Role",
            reversed_axis=False,
        )
        fig_jumlah_jd.update_layout(
            title_x=0.5,
            title_xanchor='center'
        )
        st.plotly_chart(fig_jumlah_jd, use_container_width=True)

    with col_right:
        fig_sig_jd = make_signature_chart(
            D["sig_jd"], "industry_domain",
            "Signature Skill per Role",
            reversed_axis=True,
        )
        fig_sig_jd.update_layout(
            title_x=0.5,
            title_xanchor='center'
        )
        st.plotly_chart(fig_sig_jd, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown('<div class="section-title" style="text-align: center;">📝 Kesimpulan & Rekomendasi</div>', unsafe_allow_html=True)

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("""
        <div class="gap-card">
            <h4>🔥 Skill yang Mendominasi Secara Keseluruhan</h4>
            <li>Skill seperti Python, SQL, Data Analysis, dan Machine Learning muncul di banyak role sekaligus, ini menandakan bahwa literasi data telah menjadi fondasi penting di industri IT secara luas, bukan hanya terdapat pada role Data Scientist atau Data Analyst.</li>
            <br>
            <h4>🧬 Skill Signature Role</h4>
            <ul>
                <li>ReactJS / Node.js → Full Stack Developer & Web Developer</li>
                <li>AWS / Azure / GCP → Cloud Architect & DevOps Engineer</li>
                <li>Hadoop / Spark → Big Data Engineer</li>
                <li>Hardware Troubleshooting → IT Systems Administrator</li>
            </ul>
            <h4>✨ Frekuensi Kemunculan vs Keunikan</h4>
            <li>Skill dengan frekuensi tinggi seperti Python belum tentu bersifat unik per role, justru skill dengan skor spesifisitas tinggi menjadi pembeda kuat antar role. Rekruter dapat memanfaatkan hal ini untuk menyusun kriteria seleksi yang lebih tepat sasaran.</li>
        </div>
        """, unsafe_allow_html=True)

    with col_b:
        st.markdown("""
        <div class="gap-card">
            <h4>🎯 Action Item</h4>
            <li>Perusahaan perlu memperhatikan bahwa kandidat cenderung mencantumkan skill universal dan kurang mencantumkan skill signature. Strategi screening berbasis skill spesifik role akan menghasilkan shortlist kandidat yang lebih berkualitas.</li>
        </div>
        """, unsafe_allow_html=True)

if page == "kandidat":
    header_container = st.container()
    with header_container:
        st.markdown("""
            <style>
            div[data-testid="stVerticalBlock"] > div:has(div.page-title) {
                position: -webkit-sticky;
                position: sticky;
                top: 0rem;
                background-color: #111111;
                z-index: 999;
                padding-top: 2rem;
                padding-bottom: 0.5rem;
                margin-top: -4rem;
            }
            </style>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="page-title">👤 Karakteristik Kandidat</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle" style="font-size:1.2rem";>Pertanyaan Bisnis 2: Bagaimana profil skill yang dimiliki kandidat IT?</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Role Kandidat", D["df_cv"]["candidate_role"].nunique())
    col2.metric("Total Kandidat",      f"{len(D['df_cv']):,}")
    col3.metric("Unique Skills",       D["df_cv_skills"]["skill"].nunique())

    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown('<div class="section-title" style="text-align: center;">🔥 Top Skill Kandidat per Role</div>', unsafe_allow_html=True)

    ctrl1, ctrl2 = st.columns([3, 1])
    with ctrl1:
        roles = sorted(D["df_cv"]["candidate_role"].unique())
        selected_role = st.selectbox("Pilih Role Kandidat", roles,
                                     label_visibility="collapsed")
    with ctrl2:
        top_n_cv = st.selectbox("Top N", [3, 5, 10], index=1,
                                 label_visibility="collapsed")

    fig_top_cv = make_top_n_chart(
        D["df_cv_skills"], "candidate_role",
        selected_role, top_n_cv,
        D["df_cv"], "cv_id" if "cv_id" in D["df_cv"].columns else D["df_cv"].columns[0],
        f"Top {top_n_cv} Skill Kandidat {selected_role}",
    )
    fig_top_cv.update_layout(
    title_x=0.5,
    title_xanchor='center'
    )
    st.plotly_chart(fig_top_cv, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown('<div class="section-title" style="text-align: center;">📋 Ringkasan Semua Role Kandidat</div>', unsafe_allow_html=True)

    col_left, col_right = st.columns(2)

    with col_left:
        fig_jumlah_cv = make_jumlah_skill_chart(
            D["role_avg"], "candidate_role", "avg_skill",
            "Rata-Rata Jumlah Skill Kandidat per Role",
            reversed_axis=False,
        )
        fig_jumlah_cv.update_layout(
            title_x=0.5,
            title_xanchor='center'
        )
        st.plotly_chart(fig_jumlah_cv, use_container_width=True)

    with col_right:
        fig_sig_cv = make_signature_chart(
            D["sig_cv"], "candidate_role",
            "Signature Skill Kandidat per Role",
            reversed_axis=True,
        )
        fig_sig_cv.update_layout(
            title_x=0.5,
            title_xanchor='center'
        )
        st.plotly_chart(fig_sig_cv, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown('<div class="section-title" style="text-align: center;">📝 Kesimpulan & Rekomendasi</div>', unsafe_allow_html=True)

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("""
        <div class="gap-card">
            <h4>🔥 Skill Terpopuler</h4>
            <li>SQL adalah skill yang paling banyak tercantum di CV kandidat secara keseluruhan, diikuti Testing, HTML, JavaScript, dan Java. Ini mencerminkan bahwa kandidat IT saat ini memiliki kecenderungan kuat pada skill database dan pengembangan web.</li>
            <br>
            <h4>🔀 Variasi Jumlah Skill per Role</h4>
            <ul>
                <li>Web Developer memiliki rata-rata skill tertinggi (30.5 skill/kandidat), mencerminkan luasnya ekosistem teknologi web</li>
                <li>QA Tester memiliki rata-rata skill paling sedikit (5 skill/kandidat), menunjukkan profil yang lebih terspesialisasi dan sempit</li>
            </ul>
            <h4>🧬 Pola Signature Skill Kandidat</h4>
            <li>Beberapa role memiliki signature skill yang sangat khas di CV mereka, menandakan komunitas kandidat memiliki standar yang jelas.</li>
        </div>
        """, unsafe_allow_html=True)

    with col_b:
        st.markdown("""
        <div class="gap-card">
            <h4>🎯 Action Item</h4>
            <li>Perusahaan perlu memperhatikan bahwa kandidat cenderung mencantumkan skill universal dan kurang mencantumkan skill signature. Strategi screening berbasis skill spesifik role akan menghasilkan shortlist kandidat yang lebih berkualitas.</li>
        </div>
        """, unsafe_allow_html=True)

elif page == "gap":
    header_container = st.container()
    with header_container:
        st.markdown("""
            <style>
            div[data-testid="stVerticalBlock"] > div:has(div.page-title) {
                position: -webkit-sticky;
                position: sticky;
                top: 0rem;
                background-color: #111111;
                z-index: 999;
                padding-top: 2rem;
                padding-bottom: 0.5rem;
                margin-top: -4rem;
            }
            </style>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="page-title">⚡ Analisis Gap Skill</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle" style="font-size:1.2rem";>Pertanyaan Bisnis 3: Seberapa besar kesenjangan antara kebutuhan industri dan kemampuan kandidat?</div>', unsafe_allow_html=True)

    gap_df = D["gap_df"]

    high_gap_row = gap_df.sort_values("gap_score", ascending=False).iloc[0]
    low_gap_row  = gap_df.sort_values("gap_score", ascending=True).iloc[0]

    m1, m2, m3 = st.columns(3)
    m1.metric("Skills Analyzed",    f"{len(gap_df):,}")
    m2.metric("Largest Gap",        f"{high_gap_row['gap_score']:.1f}%",
              f"{high_gap_row['skill'].title()}")
    m3.metric("Smallest Gap",       f"{low_gap_row['gap_score']:.1f}%",
              f"{low_gap_row['skill'].title()}")

    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown('<div class="section-title" style="text-align: center;">⚡ Analisis Kesenjangan Kebutuhan vs Ketersediaan Skill</div>', unsafe_allow_html=True)
    top_n_gap = st.selectbox("Tampilkan Top N Skill Gap", [3, 5, 10], index=1,
                              label_visibility="collapsed")

    high_gap_df = gap_df.sort_values("gap_score", ascending=False).head(top_n_gap)
    low_gap_df  = gap_df.sort_values("gap_score", ascending=True).head(top_n_gap)

    fig_jd_gap = make_gap_facing_charts(high_gap_df, top_n_gap)[0]
    fig_cv_gap = make_gap_facing_charts(low_gap_df, top_n_gap)[0]

    col_l, col_r = st.columns(2)
    with col_l:
        fig_jd_gap.update_layout(
            title=f"Top {top_n_gap} Gap Tertinggi (Largest Gap)",
            title_x=0.5,
            title_xanchor='center'
        )
        st.plotly_chart(fig_jd_gap, use_container_width=True)
    with col_r:
        fig_cv_gap.update_layout(
            title=f"Top {top_n_gap} Gap Terendah (Smallest Gap)",
            title_x=0.5,
            title_xanchor='center'
        )
        st.plotly_chart(fig_cv_gap, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown('<div class="section-title" style="text-align: center;">📝 Kesimpulan & Rekomendasi</div>', unsafe_allow_html=True)

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("""
        <div class="gap-card">
            <h4>📈 Gap Tertinggi</h4>
            <ul>
                <li><strong>Artificial Intelegence</strong> — gap ~97.11% (kebutuhan industri jauh melampaui kesiapan kandidat)</li>
                <li><strong>Data Governance</strong> — gap ~96.66%</li>
                <li><strong>Statistical Analysis</strong> — gap ~96.03%</li>
                <li><strong>Data Engineering</strong> — gap ~94.85%</li>
                <li><strong>Data Analysis</strong> — gap ~93.79%</li>
            </ul>
            <br>
            <h4>📉 Gap Terkecil</h4>
            <ul>
                <li><strong>Risk Management</strong> — gap hanya ~1.67%</li>
                <li><strong>Kotlin</strong> — gap ~4.74%</li>
                <li><strong>System Monitoring</strong> — gap 4.74%</li>
                <li><strong>Pandas</strong> — gap 4.74%</li>
                <li><strong>Spacy</strong> — gap 4.74%</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col_b:
        st.markdown("""
        <div class="gap-card">
            <h4>🎯 Action Items untuk Kandidat</h4>
            <ul>
                <li>Prioritaskan <strong>upskilling pada skill dengan gap &gt;90%</strong>
                    untuk meningkatkan daya saing di pasar kerja</li>
                <li>Fokus pada ekosistem <strong>Data &amp; AI</strong>:
                    Data Engineering, Statistical Analysis, Data Governance</li>
                <li>Skill dengan gap rendah (Kubernetes, Pandas) sudah umum —
                    kurang memberikan keunggulan kompetitif</li>
            </ul>
            <br>
            <h4>🎯 Action Items untuk Perusahaan</h4>
            <ul>
                <li>Rancang <strong>program rekrutmen terarah</strong> khusus untuk
                    skill defisit tinggi (Data &amp; AI, Data Governance)</li>
                <li>Pertimbangkan <strong>program pelatihan internal</strong> untuk skill
                    dengan gap ekstrem agar tidak bergantung pada pasar kandidat yang terbatas</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)