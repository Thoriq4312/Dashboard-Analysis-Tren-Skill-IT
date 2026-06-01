import streamlit as st
import pandas as pd
import ast
import plotly.graph_objects as go

# File Google Drive
FILE_ID_JD = "1X68LndJS98ZIefRLEi5cwv3pl4-UMsol"
FILE_ID_CV = "13LYhqvUZoIpWHGS1-ijs0aeSRnswl_PB"

def gdrive_url(file_id):
    return f"https://drive.google.com/uc?id={file_id}"

st.set_page_config(
    page_title="ResuMy",
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
    content: "Analisis Tren Skill IT";
    color: white !important;
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
    font-size: 0.72rem;
    font-weight: 600;
    color: #666666;
    letter-spacing: 0.12em;
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
    margin-top: 4px;
    margin-bottom: 20px;
    max-width: 820px;
}
.gap-card {
    background: #181818;
    border: 1px solid #2a2a2a;
    border-left: 3px solid #E4002B;
    border-radius: 8px;
    padding: 20px 24px;
    margin-top: 8px;
}
.gap-card h4 {
    color: #BBBBBB;
    font-size: 0.72rem;
    letter-spacing: 0.10em;
    text-transform: uppercase;
    margin-bottom: 10px;
    margin-top: 14px;
}
.gap-card h4:first-child { margin-top: 0; }
.gap-card ul { color: #CCCCCC; font-size: 0.86rem; line-height: 1.7; padding-left: 18px; }
.gap-card li { color: #CCCCCC; font-size: 0.86rem; line-height: 1.7; }
.gap-card li strong { color: #FFFFFF; }
</style>
""", unsafe_allow_html=True)


def parse_skills(val):
    if isinstance(val, list):
        return val
    if not isinstance(val, str):
        return []
    val = val.strip()
    if val.startswith("["):
        try:
            return ast.literal_eval(val)
        except Exception:
            pass
    return [s.strip() for s in val.split(",") if s.strip()]


@st.cache_data(show_spinner="Memuat data…")
def load_data():
    import gdown, os

    # Load JD
    df_jd = pd.read_csv(gdrive_url(FILE_ID_JD))
    df_jd["require_skills"] = df_jd["require_skills"].apply(parse_skills)
    df_jd["skill_count"] = df_jd["require_skills"].apply(len)

    # Load CV
    cv_path = "cv_dashboard.csv"
    if not os.path.exists(cv_path):
        gdown.download(gdrive_url(FILE_ID_CV), cv_path, quiet=False)
    df_cv = pd.read_csv(cv_path)
    df_cv["skills"] = df_cv["skills"].apply(parse_skills)
    df_cv["skill_count"] = df_cv["skills"].apply(len)

    # Explode skills
    df_jd_skills = (
        df_jd[["job_role", "require_skills"]]
        .assign(skill=lambda x: x["require_skills"])
        .explode("skill")
    )
    df_jd_skills["skill"] = df_jd_skills["skill"].str.strip().str.lower()
    df_jd_skills = df_jd_skills[df_jd_skills["skill"].notna() & (df_jd_skills["skill"] != "")]

    df_cv_skills = (
        df_cv[["cv_role", "skills"]]
        .assign(skill=lambda x: x["skills"])
        .explode("skill")
    )
    df_cv_skills["skill"] = df_cv_skills["skill"].str.strip().str.lower()
    df_cv_skills = df_cv_skills[df_cv_skills["skill"].notna() & (df_cv_skills["skill"] != "")].reset_index(drop=True)

    # Domain avg JD
    domain_avg = (
        df_jd.groupby("job_role")["skill_count"]
        .mean().sort_values(ascending=True).round(1).reset_index()
        .rename(columns={"skill_count": "avg_skill"})
    )

    # Signature JD
    total_jd_freq = df_jd_skills["skill"].value_counts()
    domain_skill_freq = df_jd_skills.groupby(["job_role", "skill"]).size().reset_index(name="domain_count")
    domain_skill_freq["global_count"] = domain_skill_freq["skill"].map(total_jd_freq)
    domain_skill_freq["specificity"] = (domain_skill_freq["domain_count"] / domain_skill_freq["global_count"]).round(3)
    sig_jd = (
        domain_skill_freq[domain_skill_freq["domain_count"] >= 5]
        .sort_values("specificity", ascending=False)
        .groupby("job_role").first().reset_index()
        [["job_role", "skill", "domain_count", "specificity"]]
        .sort_values("specificity", ascending=True)
    )

    # Role avg CV
    role_avg = (
        df_cv.groupby("cv_role")["skill_count"]
        .mean().sort_values(ascending=True).round(1).reset_index()
        .rename(columns={"skill_count": "avg_skill"})
    )

    # Signature CV
    total_cv_freq = df_cv_skills["skill"].value_counts()
    role_skill_freq = df_cv_skills.groupby(["cv_role", "skill"]).size().reset_index(name="role_count")
    role_skill_freq["global_count"] = role_skill_freq["skill"].map(total_cv_freq)
    role_skill_freq["specificity"] = (role_skill_freq["role_count"] / role_skill_freq["global_count"]).round(3)
    sig_cv = (
        role_skill_freq[role_skill_freq["role_count"] >= 3]
        .sort_values("specificity", ascending=False)
        .groupby("cv_role").first().reset_index()
        [["cv_role", "skill", "role_count", "specificity"]]
        .sort_values("specificity", ascending=True)
    )

    # Gap
    jd_freq = df_jd_skills["skill"].value_counts().reset_index()
    jd_freq.columns = ["skill", "jd_count"]
    cv_freq = df_cv_skills["skill"].value_counts().reset_index()
    cv_freq.columns = ["skill", "cv_count"]
    gap_df = pd.merge(jd_freq, cv_freq, on="skill", how="inner")
    gap_df["jd_pct"] = (gap_df["jd_count"] / gap_df["jd_count"].sum()) * 100
    gap_df["cv_pct"] = (gap_df["cv_count"] / gap_df["cv_count"].sum()) * 100
    gap_df["gap_score"] = 100 - ((gap_df["cv_pct"] / gap_df["jd_pct"]).round(5)) * 100
    gap_df = gap_df[gap_df["gap_score"] > 0]

    return {
        "df_jd":        df_jd,
        "df_cv":        df_cv,
        "df_jd_skills": df_jd_skills,
        "df_cv_skills": df_cv_skills,
        "domain_avg":   domain_avg,
        "sig_jd":       sig_jd,
        "role_avg":     role_avg,
        "sig_cv":       sig_cv,
        "gap_df":       gap_df,
    }


# Chart constants
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
    xaxis=dict(gridcolor=GRID_COLOR, gridwidth=1, zeroline=False, showline=False, tickcolor=TEXT_COLOR),
    yaxis=dict(gridcolor="rgba(0,0,0,0)", zeroline=False, showline=False, tickcolor=TEXT_COLOR),
    hoverlabel=dict(bgcolor="#1e1e1e", bordercolor=ACCENT, font=dict(color="#FFFFFF", size=12)),
)


def hbar_chart(y_labels, x_vals, title, text_labels=None, reversed_axis=False,
               bar_color=ACCENT, height=420, x_title=""):
    hover_text = [
        f"<b>{lbl.title()}</b><br>{txt}" if text_labels else f"<b>{lbl.title()}</b><br>{x:.2f}"
        for lbl, x, txt in zip(y_labels, x_vals, text_labels if text_labels else [""]*len(y_labels))
    ]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=y_labels, x=x_vals, orientation="h",
        marker=dict(color=bar_color, line=dict(width=0)),
        text=text_labels, textposition="outside",
        textfont=dict(color=TEXT_COLOR, size=10),
        hovertemplate="%{customdata}<extra></extra>",
        customdata=hover_text,
    ))
    layout = {**PLOTLY_LAYOUT}
    layout["title"] = dict(text=f"<b>{title}</b>", font=dict(color="#FFFFFF", size=14), x=0, xanchor="left")
    layout["height"] = height
    layout["xaxis"]["title"] = x_title
    layout["xaxis"]["title_font"] = dict(color="#888888", size=11)
    layout["bargap"] = 0.35
    if reversed_axis:
        layout["yaxis"]["side"] = "right"
        layout["xaxis"]["autorange"] = "reversed"
    fig.update_layout(**layout)
    return fig


def make_top_n_chart(skills_df, role_col, selected_role, top_n, df_raw, title):
    data = (
        skills_df[skills_df[role_col] == selected_role]
        .groupby("skill").size().reset_index(name="count")
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
        title=title, text_labels=text_labels,
        height=max(320, n * 52 + 80),
    )


def make_jumlah_skill_chart(avg_df, role_col, avg_col, title, reversed_axis=False):
    labels = avg_df[role_col].tolist()
    values = avg_df[avg_col].tolist()
    return hbar_chart(
        y_labels=labels, x_vals=values, title=title,
        text_labels=[f"{v}" for v in values],
        reversed_axis=reversed_axis,
        height=max(400, len(labels) * 28 + 80),
    )


def make_signature_chart(sig_df, role_col, title, reversed_axis=False):
    labels = sig_df[role_col].tolist()
    values = sig_df["specificity"].tolist()
    skills = sig_df["skill"].str.title().tolist()
    return hbar_chart(
        y_labels=labels, x_vals=values, title=title,
        text_labels=[f'"{s}" ({v:.0%})' for s, v in zip(skills, values)],
        reversed_axis=reversed_axis,
        height=max(400, len(labels) * 28 + 80), x_title="Specificity Score",
    )


def make_gap_chart(gap_df, top_n, ascending=False):
    data = (
        gap_df.sort_values("gap_score", ascending=ascending)
        .head(top_n)
        .sort_values("gap_score", ascending=not ascending)
    )
    labels   = data["skill"].str.title().tolist()
    jd_vals  = data["jd_pct"].round(3).tolist()
    gap_vals = data["gap_score"].round(2).tolist()
    h        = max(360, top_n * 52 + 80)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=labels, x=jd_vals, orientation="h",
        marker=dict(color=ACCENT, line=dict(width=0)),
        text=[f"{v:.3f}  ▏Gap {g:.1f}%" for v, g in zip(jd_vals, gap_vals)],
        textposition="outside",
        textfont=dict(color=TEXT_COLOR, size=10),
        hovertemplate="<b>%{y}</b><br>Industry: %{x:.3f}%<extra></extra>",
    ))
    layout = {**PLOTLY_LAYOUT, "height": h, "bargap": 0.38,
              "title": dict(text="<b>Industry Skill Demand</b>",
                            font=dict(color="#FFFFFF", size=14), x=0)}
    fig.update_layout(**layout)
    return fig


# Sidebar
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 16px 0 8px 0;'>
        <div style='font-size:2.4rem; margin-bottom:4px; color:white'><b>ResuMy</b></div>
        <div style='font-size:1.1rem; font-weight:800; color:#E4002B;
                    letter-spacing:0.08em; text-transform:uppercase;'>
            CC26-PSU006
        </div>
    </div>
    <hr style='border-color:#2a2a2a; margin: 10px 0 16px 0;'>
    """, unsafe_allow_html=True)

    st.markdown("<div style='color:#888;font-size:0.72rem;letter-spacing:0.08em;"
                "text-transform:uppercase;margin-bottom:8px;'>Halaman Dashboard</div>",
                unsafe_allow_html=True)

    if "page" not in st.session_state:
        st.session_state.page = "industri"

    pages = {
        "industri": "Tren Kebutuhan Industri",
        "kandidat": "Karakteristik Kandidat",
        "gap":      "Analisis Gap Skill",
    }
    for key, label in pages.items():
        if st.button(label, key=f"nav_{key}", use_container_width=True):
            st.session_state.page = key

    st.markdown("<hr style='border-color:#2a2a2a; margin:16px 0;'>", unsafe_allow_html=True)

# Load data
try:
    D = load_data()
except Exception as e:
    st.error(f"**Error saat memuat data:** {e}")
    st.stop()

page = st.session_state.page


# PAGE 1 Industri
if page == "industri":
    st.markdown("""
        <style>
        div[data-testid="stVerticalBlock"] > div:has(div.page-title) {
            position: -webkit-sticky; position: sticky; top: 0rem;
            background-color: #111111; z-index: 999;
            padding-top: 4rem; padding-bottom: 1rem; margin-top: -4rem;
        }
        </style>
    """, unsafe_allow_html=True)
    st.markdown('<div class="page-title">Tren Kebutuhan Industri</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Pertanyaan Bisnis 1: Bagaimana tren kebutuhan skill IT pada berbagai role industri, serta skill apa yang bersifat universal dan spesifik pada masing-masing role?</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Role Industri", D["df_jd"]["job_role"].nunique())
    col2.metric("Total Job Postings",  f"{len(D['df_jd']):,}")
    col3.metric("Unique Skills",       D["df_jd_skills"]["skill"].nunique())

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="section-title" style="text-align:center">Top Skill</div>', unsafe_allow_html=True)

    ctrl1, ctrl2 = st.columns([3, 1])
    with ctrl1:
        selected_domain = st.selectbox("Pilih Role Industri",
                                       sorted(D["df_jd"]["job_role"].unique()),
                                       label_visibility="collapsed")
    with ctrl2:
        top_n_jd = st.selectbox("Top N", [3, 5, 10], index=1, label_visibility="collapsed")

    fig = make_top_n_chart(D["df_jd_skills"], "job_role", selected_domain, top_n_jd,
                           D["df_jd"], f"Top {top_n_jd} Skill {selected_domain}")
    fig.update_layout(title_x=0.5, title_xanchor="center")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="section-title" style="text-align:center">Ringkasan Semua Role</div>', unsafe_allow_html=True)

    col_left, col_right = st.columns(2)
    with col_left:
        fig_avg = make_jumlah_skill_chart(D["domain_avg"], "job_role", "avg_skill",
                                          "Rata-Rata Jumlah Skill")
        fig_avg.update_layout(title_x=0.5, title_xanchor="center")
        st.plotly_chart(fig_avg, use_container_width=True)
    with col_right:
        fig_sig = make_signature_chart(D["sig_jd"], "job_role",
                                       "Signature Skill", reversed_axis=True)
        fig_sig.update_layout(title_x=0.5, title_xanchor="center")
        st.plotly_chart(fig_sig, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="section-title" style="text-align:center">Kesimpulan & Rekomendasi</div>', unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""
        <div class="gap-card">
            <h4>Skill yang Mendominasi Secara Keseluruhan</h4>
            <li>Python, SQL, Analytics, Reporting, dan Excel ditemukan pada banyak role, menunjukkan bahwa skill tersebut dibutuhkan di berbagai bidang pekerjaan IT.</li>
            <br>
            <h4>Skill Signature Role</h4>
            <ul>
                <li>Artificial Intelligence → AI Engineer</li>
                <li>Machine Learning → Machine Learning Engineer</li>
                <li>Business Intelligence → BI Analyst</li>
                <li>Javascript → Web Developer</li>
                <li>Azure / AWS → Cloud Architect</li>
            </ul>
            <h4>Frekuensi Kemunculan vs Keunikan</h4>
            <li>Python dan Excel banyak ditemukan di berbagai role. Sebaliknya, Artificial Intelligence dan Machine Learning lebih identik dengan role tertentu.</li>
        </div>
        """, unsafe_allow_html=True)
    with col_b:
        st.markdown("""
        <div class="gap-card">
            <h4>Action Item</h4>
            <li>Skill yang khas pada suatu role dapat menjadi fokus utama dalam job posting. Sementara itu, skill yang umum ditemukan di berbagai role dapat dijadikan persyaratan tambahan.</li>
        </div>
        """, unsafe_allow_html=True)


# PAGE 2 Kandidat
if page == "kandidat":
    st.markdown("""
        <style>
        div[data-testid="stVerticalBlock"] > div:has(div.page-title) {
            position: -webkit-sticky; position: sticky; top: 0rem;
            background-color: #111111; z-index: 999;
            padding-top: 4rem; padding-bottom: 1rem; margin-top: -4rem;
        }
        </style>
    """, unsafe_allow_html=True)
    st.markdown('<div class="page-title">Karakteristik Kandidat</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Pertanyaan Bisnis 2: Bagaimana karakteristik kepemilikan skill kandidat pada berbagai role IT?</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Role Kandidat", D["df_cv"]["cv_role"].nunique())
    col2.metric("Total Kandidat",      f"{len(D['df_cv']):,}")
    col3.metric("Unique Skills",       D["df_cv_skills"]["skill"].nunique())

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="section-title" style="text-align:center">Top Skill Kandidat</div>', unsafe_allow_html=True)

    ctrl1, ctrl2 = st.columns([3, 1])
    with ctrl1:
        selected_role = st.selectbox("Pilih Role Kandidat",
                                     sorted(D["df_cv"]["cv_role"].unique()),
                                     label_visibility="collapsed")
    with ctrl2:
        top_n_cv = st.selectbox("Top N", [3, 5, 10], index=1, label_visibility="collapsed")

    fig = make_top_n_chart(D["df_cv_skills"], "cv_role", selected_role, top_n_cv,
                           D["df_cv"], f"Top {top_n_cv} Skill Kandidat {selected_role}")
    fig.update_layout(title_x=0.5, title_xanchor="center")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="section-title" style="text-align:center">Ringkasan Semua Role Kandidat</div>', unsafe_allow_html=True)

    col_left, col_right = st.columns(2)
    with col_left:
        fig_avg = make_jumlah_skill_chart(D["role_avg"], "cv_role", "avg_skill",
                                          "Rata-Rata Jumlah Skill Kandidat")
        fig_avg.update_layout(title_x=0.5, title_xanchor="center")
        st.plotly_chart(fig_avg, use_container_width=True)
    with col_right:
        fig_sig = make_signature_chart(D["sig_cv"], "cv_role",
                                       "Signature Skill", reversed_axis=True)
        fig_sig.update_layout(title_x=0.5, title_xanchor="center")
        st.plotly_chart(fig_sig, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="section-title" style="text-align:center">Kesimpulan & Rekomendasi</div>', unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""
        <div class="gap-card">
            <h4>Skill Terpopuler</h4>
            <li>SQL dan Testing merupakan skill yang paling sering muncul pada berbagai role kandidat. Selain itu, HTML dan JavaScript juga banyak ditemukan pada CV kandidat di beberapa role.</li>
            <br>
            <h4>Variasi Jumlah Skill per Role</h4>
            <li>Business Analyst memiliki rata-rata jumlah skill tertinggi (32,6 skill per CV), sedangkan Cloud Engineer memiliki rata-rata terendah (8,1 skill per CV).</li>
            <h4>Pola Signature Skill Kandidat</h4>
            <li>Beberapa skill terlihat sangat identik dengan role tertentu. Contohnya, A/B Testing muncul pada seluruh kandidat Data Scientist, sedangkan ASP.NET ditemukan pada 77% kandidat Business Analyst.</li>
        </div>
        """, unsafe_allow_html=True)
    with col_b:
        st.markdown("""
        <div class="gap-card">
            <h4>Action Item</h4>
            <li>Perusahaan sebaiknya menerapkan strategi screening berbasis signature skill untuk menyaring tumpukan CV. Mengingat tingginya persentase skill universal seperti SQL dan Testing yang dicantumkan oleh kandidat di hampir semua role, fokus pada skill spesifik yang memiliki skor keunikan tinggi seperti "A/B Testing" pada Data Scientist atau "Asp.Net" pada Business Analyst, ini akan menghasilkan shortlist kandidat yang jauh lebih berkualitas dan relevan.</li>
        </div>
        """, unsafe_allow_html=True)


# PAGE 3 Gap
elif page == "gap":
    st.markdown("""
        <style>
        div[data-testid="stVerticalBlock"] > div:has(div.page-title) {
            position: -webkit-sticky; position: sticky; top: 0rem;
            background-color: #111111; z-index: 999;
            padding-top: 4rem; padding-bottom: 1rem; margin-top: -4rem;
        }
        </style>
    """, unsafe_allow_html=True)
    st.markdown('<div class="page-title">Analisis Gap Skill</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Pertanyaan Bisnis 3: Bagaimana gap skill antara Kebutuhan Industri dengan Kandidat?</div>', unsafe_allow_html=True)

    gap_df = D["gap_df"]
    high_gap_row = gap_df.sort_values("gap_score", ascending=False).iloc[0]
    low_gap_row  = gap_df.sort_values("gap_score", ascending=True).iloc[0]

    m1, m2, m3 = st.columns(3)
    m1.metric("Total Skill", f"{len(gap_df):,}")
    m2.metric("Gap Terbesar",  f"{high_gap_row['gap_score']:.1f}%", f"{high_gap_row['skill'].title()}")
    m3.metric("Gap Terkecil", f"{low_gap_row['gap_score']:.1f}%",  f"{low_gap_row['skill'].title()}")

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="section-title" style="text-align:center">Analisis Kesenjangan Kebutuhan vs Ketersediaan Skill</div>', unsafe_allow_html=True)

    top_n_gap = st.selectbox("Tampilkan Top N Skill Gap", [3, 5, 10], index=1, label_visibility="collapsed")

    col_l, col_r = st.columns(2)
    with col_l:
        fig_high = make_gap_chart(gap_df, top_n_gap, ascending=False)
        fig_high.update_layout(title=f"Top {top_n_gap} Gap Tertinggi (Largest Gap)",
                               title_x=0.5, title_xanchor="center")
        st.plotly_chart(fig_high, use_container_width=True)
    with col_r:
        fig_low = make_gap_chart(gap_df, top_n_gap, ascending=True)
        fig_low.update_layout(title=f"Top {top_n_gap} Gap Terendah (Smallest Gap)",
                              title_x=0.5, title_xanchor="center")
        st.plotly_chart(fig_low, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="section-title" style="text-align:center">Kesimpulan & Rekomendasi</div>', unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""
        <div class="gap-card">
            <h4>Gap Tertinggi</h4>
            <ul>
                <li><strong>Node.Js</strong> — gap 98.8%</li>
                <li><strong>A/B Testing</strong> — gap 98%</li>
                <li><strong>Looker</strong> — gap 97.3%</li>
                <li><strong>Operations Research</strong> — gap 96.8%</li>
                <li><strong>Artificial Intelligence</strong> — gap 96.7%</li>
            </ul>
            <br>
            <h4>Gap Terkecil</h4>
            <ul>
                <li><strong>Switching</strong> — gap 1%</li>
                <li><strong>Siem</strong> — gap 1.8%</li>
                <li><strong>Elasticsearch</strong> — gap 2%</li>
                <li><strong>Incident Management</strong> — gap 2.5%</li>
                <li><strong>C</strong> — gap 3.2%</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    with col_b:
        st.markdown("""
        <div class="gap-card">
            <h4>Action Items untuk Kandidat</h4>
            <ul>
                <li>Skill seperti Node.js, A/B Testing, Looker, dan Artificial Intelligence masih banyak dicari industri, namun belum banyak dimiliki kandidat. Mengembangkan skill tersebut dapat menjadi peluang untuk meningkatkan daya saing di dunia kerja.</li>
            </ul>
            <br>
            <h4>Action Items untuk Perusahaan</h4>
            <ul>
                <li>Skill dengan gap tinggi menunjukkan bahwa kebutuhan industri masih lebih besar dibandingkan jumlah kandidat yang memilikinya. Oleh karena itu, perusahaan dapat memprioritaskan rekrutmen atau pelatihan pada skill-skill tersebut.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
