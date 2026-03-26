import base64
import json
from typing import Any, Dict

import streamlit as st
from groq import Groq


DEFAULT_MODEL_ID = "meta-llama/llama-4-scout-17b-16e-instruct"

st.set_page_config(page_title="Wildlife Scanner", layout="wide", page_icon="🌲")


import os
import io

# ─── Media URLs ─────────────────────────────────────────────────────────────
HERO_IMAGE = "https://images.unsplash.com/photo-1425913397330-cf8af2ff40a1?ixlib=rb-4.0.3&auto=format&fit=crop&w=300&q=80"
PLACEHOLDER_IMAGE = "https://images.unsplash.com/photo-1511497584788-876760111969?ixlib=rb-4.0.3&auto=format&fit=crop&w=300&q=80"

# Load local earth.gif as base64
def get_local_gif(filename):
    if os.path.exists(filename):
        with open(filename, "rb") as f:
            return f"data:image/gif;base64,{base64.b64encode(f.read()).decode('utf-8')}"
    return ""

EARTH_GIF = get_local_gif("earth.gif")


def render_css() -> None:
    st.markdown(
        """
        <style>
          @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

          :root{
            --brand: #4ade80;
            --brand-dark: #166534;
            --brand-glow: rgba(74,222,128,0.35);
            --accent: #38bdf8;
            --card: rgba(6, 78, 59, 0.55);
            --card-border: rgba(167, 243, 208, 0.15);
            --muted: #cbd5e1;
            --danger: #ef4444;
            --vulnerable: #f59e0b;
            --safe: #22c55e;
            --bg: #022c22;
          }

          html, body, .stApp {
            /* Full Forest/Lake Photographic Background with Deep Green Overlay */
            background: linear-gradient(rgba(2, 44, 34, 0.88), rgba(2, 44, 34, 0.95)), url('https://images.unsplash.com/photo-1448375240586-882707db888b?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80') center/cover fixed !important;
            color: #f8fafc !important;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
          }

          /* ─── Custom scrollbar ─── */
          ::-webkit-scrollbar { width: 6px; }
          ::-webkit-scrollbar-track { background: transparent; }
          ::-webkit-scrollbar-thumb { background: rgba(74,222,128,0.3); border-radius: 3px; }
          ::-webkit-scrollbar-thumb:hover { background: rgba(74,222,128,0.5); }

          /* ─── Keythemes ─── */
          @keyframes gradientShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
          }
          @keyframes floatIn {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
          }
          @keyframes pulseGlow {
            0%, 100% { box-shadow: 0 0 20px rgba(74,222,128,0.2), 0 0 60px rgba(74,222,128,0.1); }
            50% { box-shadow: 0 0 30px rgba(74,222,128,0.4), 0 0 80px rgba(74,222,128,0.2); }
          }
          @keyframes shimmer {
            0% { background-position: -200% center; }
            100% { background-position: 200% center; }
          }
          @keyframes pulseDanger {
            0%, 100% { box-shadow: 0 0 8px rgba(239,68,68,0.4); }
            50% { box-shadow: 0 0 16px rgba(239,68,68,0.7); }
          }
          @keyframes pulseWarning {
            0%, 100% { box-shadow: 0 0 8px rgba(245,158,11,0.4); }
            50% { box-shadow: 0 0 16px rgba(245,158,11,0.7); }
          }
          @keyframes pulseSafe {
            0%, 100% { box-shadow: 0 0 8px rgba(34,197,94,0.4); }
            50% { box-shadow: 0 0 16px rgba(34,197,94,0.7); }
          }
          @keyframes fadeUp {
            from { opacity: 0; transform: translateY(16px); }
            to { opacity: 1; transform: translateY(0); }
          }

          /* ─── Hero Header (Lake/Forest Theme) ─── */
          .wc-hero {
            position: relative;
            background: linear-gradient(135deg, rgba(6, 78, 59, 0.7), rgba(2, 44, 34, 0.9), rgba(6, 78, 59, 0.7));
            background-size: 300% 300%;
            animation: gradientShift 8s ease infinite, pulseGlow 4s ease-in-out infinite;
            color: white;
            padding: 32px 36px;
            border-radius: 20px;
            margin-bottom: 24px;
            overflow: hidden;
            border: 1px solid rgba(167, 243, 208, 0.2);
            backdrop-filter: blur(20px);
          }
          .wc-hero::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle at 30% 30%, rgba(167, 243, 208, 0.08) 0%, transparent 60%);
            pointer-events: none;
          }
          .wc-hero-content {
            display: flex;
            align-items: center;
            gap: 28px;
            position: relative;
            z-index: 1;
          }
          .wc-hero-text { flex: 1; }
          .wc-hero-gif {
            width: 130px;
            height: 130px;
            border-radius: 50%;
            object-fit: cover;
            border: 4px solid rgba(167, 243, 208, 0.3);
            box-shadow: 0 0 30px rgba(167, 243, 208, 0.2);
            flex-shrink: 0;
            transition: transform 0.3s ease;
          }
          .wc-hero-gif:hover {
            transform: scale(1.05);
          }
          .wc-title {
            font-size: 40px;
            font-weight: 900;
            margin-bottom: 6px;
            letter-spacing: -0.5px;
            background: linear-gradient(to right, #d1fae5, #34d399, #d1fae5);
            background-size: 200% auto;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: floatIn 0.8s ease-out, shimmer 4s linear infinite;
          }
          .wc-subtitle {
            color: rgba(209, 250, 229, 0.85);
            font-size: 16px;
            font-weight: 400;
            line-height: 1.5;
            animation: floatIn 1s ease-out;
          }
          .wc-hero-badges {
            margin-top: 14px;
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            animation: floatIn 1.2s ease-out;
          }
          .wc-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 6px 14px;
            border-radius: 999px;
            font-weight: 600;
            font-size: 13px;
            letter-spacing: 0.3px;
            backdrop-filter: blur(8px);
            border: 1px solid rgba(255,255,255,0.2);
          }
          .wc-badge-green {
            background: rgba(16, 185, 129, 0.3);
            color: #d1fae5;
          }
          .wc-badge-cyan {
            background: rgba(14, 165, 233, 0.3);
            color: #e0f2fe;
          }

          /* ─── Glass Cards with Forest Tint ─── */
          .wc-glass {
            background: var(--card) !important;
            backdrop-filter: blur(16px);
            border: 1px solid var(--card-border);
            border-radius: 18px;
            padding: 22px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            animation: fadeUp 0.6s ease-out;
          }
          .wc-glass:hover {
            border-color: rgba(74,222,128,0.35);
            box-shadow: 0 8px 32px rgba(6, 78, 59, 0.5);
            transform: translateY(-2px);
          }

          /* ─── Status Pills ─── */
          .wc-pill {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            padding: 7px 16px;
            border-radius: 999px;
            color: white;
            font-weight: 700;
            font-size: 13px;
            letter-spacing: 0.3px;
            transition: all 0.3s ease;
          }
          .wc-pill-danger {
            background: linear-gradient(135deg, #dc2626, #ef4444);
            animation: pulseDanger 2s ease-in-out infinite;
          }
          .wc-pill-vulnerable {
            background: linear-gradient(135deg, #d97706, #f59e0b);
            animation: pulseWarning 2s ease-in-out infinite;
          }
          .wc-pill-safe {
            background: linear-gradient(135deg, #15803d, #22c55e);
            animation: pulseSafe 2s ease-in-out infinite;
          }
          .wc-pill-neutral {
            background: linear-gradient(135deg, #475569, #64748b);
          }

          /* ─── Upload Area ─── */
          [data-testid="stFileUploader"] {
            border: 2px dashed rgba(74,222,128,0.4) !important;
            border-radius: 16px !important;
            padding: 8px !important;
            background: rgba(6, 78, 59, 0.3) !important;
            transition: all 0.3s ease !important;
          }
          [data-testid="stFileUploader"]:hover {
            border-color: rgba(74,222,128,0.6) !important;
            background: rgba(6, 78, 59, 0.5) !important;
          }

          /* ─── Buttons ─── */
          .stButton > button {
            width: 100%;
            background: linear-gradient(135deg, #059669, #10b981) !important;
            color: white !important;
            font-weight: 700 !important;
            border-radius: 14px !important;
            border: none !important;
            padding: 12px 18px !important;
            font-size: 15px !important;
            letter-spacing: 0.3px !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            box-shadow: 0 4px 14px rgba(16, 185, 129, 0.3) !important;
          }
          .stButton > button:hover {
            background: linear-gradient(135deg, #047857, #059669) !important;
            transform: translateY(-2px) scale(1.02) !important;
            box-shadow: 0 8px 20px rgba(16, 185, 129, 0.45) !important;
          }
          .stButton > button:active {
            transform: translateY(0) scale(0.98) !important;
          }
          .stButton > button:disabled {
            opacity: 0.5;
            transform: none !important;
          }

          /* ─── Tabs ─── */
          div[data-baseweb="tablist"] {
            background: rgba(2, 44, 34, 0.6);
            border-radius: 14px;
            padding: 4px;
            border: 1px solid rgba(167, 243, 208, 0.1);
          }
          div[data-baseweb="tablist"] button {
            background: transparent !important;
            color: #94a3b8 !important;
            border: none !important;
            border-radius: 10px !important;
            padding: 8px 16px !important;
            font-weight: 500 !important;
            transition: all 0.3s ease !important;
          }
          div[data-baseweb="tablist"] button:hover {
            color: #f8fafc !important;
            background: rgba(16, 185, 129, 0.15) !important;
          }
          div[data-baseweb="tablist"] button[aria-selected="true"] {
            color: #ffffff !important;
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.3), rgba(14, 165, 233, 0.2)) !important;
            border: 1px solid rgba(16, 185, 129, 0.4) !important;
            box-shadow: 0 2px 12px rgba(16, 185, 129, 0.2) !important;
          }
          div[data-baseweb="tablist"] button[aria-selected="true"] * {
            color: #ffffff !important;
          }
          div[data-baseweb="tablist"] button * {
            color: inherit !important;
          }

          /* ─── Container borders ─── */
          [data-testid="stVerticalBlock"] > div:has(> [data-testid="stVerticalBlockBorderWrapper"]) [data-testid="stVerticalBlockBorderWrapper"] {
            background: var(--card) !important;
            border: 1px solid var(--card-border) !important;
            border-radius: 18px !important;
            backdrop-filter: blur(20px) !important;
          }

          /* ─── Section Headings ─── */
          .wc-section-title {
            font-size: 18px;
            font-weight: 700;
            color: #f8fafc;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
          }
          .wc-section-title .icon {
            font-size: 22px;
          }

          /* ─── Animal result card ─── */
          .wc-animal-header {
            animation: fadeUp 0.5s ease-out;
          }
          .wc-animal-name {
            font-size: 32px;
            font-weight: 800;
            color: #d1fae5;
            margin: 0 0 4px 0;
            letter-spacing: -0.3px;
          }
          .wc-scientific-name {
            color: #a7f3d0;
            font-style: italic;
            font-size: 15px;
            margin-bottom: 14px;
            opacity: 0.8;
          }

          /* ─── Stat cards ─── */
          .wc-stat {
            background: rgba(2, 44, 34, 0.5);
            border: 1px solid rgba(167, 243, 208, 0.2);
            border-radius: 14px;
            padding: 16px;
            text-align: center;
            transition: all 0.3s ease;
          }
          .wc-stat:hover {
            border-color: rgba(16, 185, 129, 0.4);
            background: rgba(6, 78, 59, 0.7);
          }
          .wc-stat-label {
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #a7f3d0;
            margin-bottom: 6px;
            opacity: 0.8;
          }
          .wc-stat-value {
            font-size: 16px;
            font-weight: 700;
            color: #f8fafc;
          }

          /* ─── Placeholder / empty state ─── */
          .wc-placeholder {
            text-align: center;
            padding: 48px 24px;
            animation: fadeUp 0.8s ease-out;
          }
          .wc-placeholder-gif {
            width: 220px;
            height: 220px;
            border-radius: 20%;
            object-fit: cover;
            margin-bottom: 24px;
            border: 4px solid rgba(16, 185, 129, 0.3);
            box-shadow: 0 0 50px rgba(16, 185, 129, 0.15);
            transition: transform 0.4s ease;
          }
          .wc-placeholder-gif:hover {
            transform: scale(1.03);
          }
          .wc-placeholder h3 {
            color: #d1fae5;
            font-weight: 800;
            font-size: 26px;
            margin-bottom: 8px;
          }
          .wc-placeholder p {
            color: #cbd5e1;
            font-size: 15px;
            max-width: 460px;
            margin: 0 auto;
            line-height: 1.6;
          }

          /* ─── Info box styling ─── */
          .wc-info-box {
            background: linear-gradient(135deg, rgba(6, 78, 59, 0.5), rgba(2, 44, 34, 0.5));
            border: 1px solid rgba(16, 185, 129, 0.2);
            border-radius: 14px;
            padding: 16px 20px;
            color: #e2e8f0;
            font-size: 14.5px;
            line-height: 1.7;
          }

          /* ─── SDG Card ─── */
          .wc-sdg-card {
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(14, 165, 233, 0.1));
            border: 1px solid rgba(16, 185, 129, 0.3);
            border-radius: 16px;
            padding: 24px;
            animation: fadeUp 0.6s ease-out;
          }
          .wc-sdg-gif {
            width: 70px;
            height: 70px;
            border-radius: 50%;
            object-fit: cover;
            margin-bottom: 16px;
            border: 2px solid rgba(14, 165, 233, 0.4);
            box-shadow: 0 0 20px rgba(14, 165, 233, 0.2);
          }

          /* ─── Divider ─── */
          .wc-divider {
            height: 1px;
            background: linear-gradient(to right, transparent, rgba(16, 185, 129, 0.4), transparent);
            margin: 20px 0;
            border: none;
          }

          /* ─── Hide default Streamlit elements ─── */
          #MainMenu { visibility: hidden; }
          footer { visibility: hidden; }
          header[data-testid="stHeader"] { background: transparent !important; }

          /* ─── Spinner ─── */
          .stSpinner > div > div {
            border-top-color: var(--brand) !important;
          }

          /* ─── Images within containers ─── */
          [data-testid="stImage"] {
            border-radius: 14px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
          }
        </style>
        """,
        unsafe_allow_html=True,
    )


def status_to_pill(status: str | None) -> tuple[str, str]:
    if not status:
        return ("neutral", "Unknown Status")
    s = status.lower()
    if "critically" in s or "endangered" in s:
        return ("danger", status)
    if "vulnerable" in s or "near threatened" in s:
        return ("vulnerable", status)
    return ("safe", status)


def normalize_text_maybe(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value.strip() or None
    return str(value).strip() or None


def parse_response(text: str) -> Dict[str, Any]:
    try:
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            return json.loads(text[start:end])
    except Exception:
        pass
    return {"not_animal": True, "message": "Could not parse response"}


def build_prompt() -> str:
    return (
        "Analyze this image. If it contains an animal, provide detailed information in JSON format.\n\n"
        "If the image does NOT contain an animal, respond with:\n"
        "{\"not_animal\": true, \"message\": \"This image does not appear to contain an animal.\"}\n\n"
        "If it DOES contain an animal, respond with this JSON structure:\n"
        "{\n"
        "  \"not_animal\": false,\n"
        "  \"animal_name\": \"Common name of the animal\",\n"
        "  \"scientific_name\": \"Scientific/Latin name\",\n"
        "  \"conservation_status\": \"One of: Critically Endangered, Endangered, Vulnerable, Near Threatened, Least Concern, Data Deficient\",\n"
        "  \"population_trend\": \"Increasing, Stable, Decreasing, or Unknown\",\n"
        "  \"estimated_population\": \"Estimated population size/range if known, otherwise \\\"Unknown\\\"\",\n"
        "  \"habitat\": \"Describe habitat in detail (3-5 sentences): where it lives (region/ecosystem), typical climate/altitude/elevation if known, and what environmental features matter for its survival (e.g., bamboo/forest type, cover, water availability).\",\n"
        "  \"background\": \"Brief description of the animal, its characteristics and behavior\",\n"
        "  \"threats\": \"Main threats described as a short sentence (comma-separated if needed)\",\n"
        "  \"sdg_connection\": \"Explain how protecting this species connects to UN SDG 15 (Life on Land) - protecting terrestrial ecosystems and biodiversity\",\n"
        "  \"conservation_efforts\": \"Recommended conservation efforts people can take (short sentence)\"\n"
        "}\n\n"
        "Respond ONLY with valid JSON, no other text."
    )


def analyze_image(image_bytes: bytes, filename: str | None) -> Dict[str, Any]:
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except Exception as e:
        raise RuntimeError(
            "Missing Streamlit secret `GROQ_API_KEY`. Go to Streamlit Cloud → Secrets and add it (TOML format)."
        ) from e

    model_id = DEFAULT_MODEL_ID
    try:
        model_id = st.secrets["GROQ_VISION_MODEL"]
    except Exception:
        pass

    file_ext = "jpg"
    if filename and "." in filename:
        file_ext = filename.split(".")[-1].lower()

    mime_type = f"image/{'jpeg' if file_ext == 'jpg' else file_ext}"
    base64_image = base64.b64encode(image_bytes).decode("utf-8")

    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model=model_id,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": build_prompt()},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime_type};base64,{base64_image}"},
                    },
                ],
            }
        ],
        max_tokens=1500,
    )

    result_text = response.choices[0].message.content
    return parse_response(result_text)


# ═══════════════════════════════════════════════════════════════════════════════
# RENDER
# ═══════════════════════════════════════════════════════════════════════════════

render_css()

# ─── Hero Header ──────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div class="wc-hero">
      <div class="wc-hero-content">
        <div class="wc-hero-text">
          <div class="wc-title">🌲 Wildlife Scanner</div>
          <div class="wc-subtitle">
            Upload a photo of any animal to instantly identify it and discover its conservation
            status, habitat, and connection to UN Sustainable Development Goal 15.
          </div>
          <div class="wc-hero-badges">
            <span class="wc-badge wc-badge-green">🌿 SDG 15: Life on Land</span>
            <span class="wc-badge wc-badge-cyan">🔬 AI-Powered Analysis</span>
          </div>
        </div>
        <img src="{HERO_IMAGE}" alt="Forest" class="wc-hero-gif" />
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ─── Session State ─────────────────────────────────────────────────────────────
if "analysis" not in st.session_state:
    st.session_state.analysis = None

col_left, col_right = st.columns([1, 2], gap="large")

# ─── Left Column: Upload & SDG Info ──────────────────────────────────────────
with col_left:
    with st.container(border=True):
        st.markdown(
            '<div class="wc-section-title"><span class="icon">📷</span> Capture Wildlife</div>',
            unsafe_allow_html=True,
        )

        uploaded_file = st.file_uploader(
            "Upload an Animal Image",
            type=["jpg", "jpeg", "png", "webp"],
            label_visibility="collapsed",
        )

        file_bytes = None
        if uploaded_file is not None:
            file_bytes = uploaded_file.getvalue()
            st.image(file_bytes, use_container_width=True, caption=uploaded_file.name)
            st.caption(f"📁 Image size: {len(file_bytes) / 1024:.1f} KB")

        if uploaded_file is not None and st.button("🔍 Analyze Habitat & Species", type="primary"):
            with st.spinner("🧠 AI is analyzing the wildlife..."):
                try:
                    st.session_state.analysis = analyze_image(file_bytes, uploaded_file.name)
                except Exception as e:
                    st.session_state.analysis = {
                        "not_animal": True,
                        "message": f"Error analyzing image: {str(e)}",
                    }

    # SDG 15 Info Card
    with st.container(border=True):
        st.markdown(
            f"""
            <div class="wc-sdg-card">
              <img src="{EARTH_GIF}" alt="Earth animation" class="wc-sdg-gif" />
              <div class="wc-section-title"><span class="icon">🌍</span> SDG 15: Life on Land</div>
              <div class="wc-info-box">
                <strong>Goal:</strong> Protect, restore and promote sustainable use of terrestrial ecosystems.<br/><br/>
                🌲 Sustainably manage forests<br/>
                🏜️ Combat desertification<br/>
                🔄 Halt and reverse land degradation<br/>
                🦎 Halt biodiversity loss
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ─── Right Column: Results ───────────────────────────────────────────────────
with col_right:
    analysis = st.session_state.analysis
    if not analysis:
        st.markdown(
            f"""
            <div class="wc-placeholder">
              <img src="{PLACEHOLDER_IMAGE}" alt="Nature scanning" class="wc-placeholder-gif" />
              <h3>Discover the Wilderness</h3>
              <p>Upload an image of any animal to uncover its species, conservation status,
                 population trends, habitat details, and how protecting it connects to
                 UN Sustainable Development Goal 15.</p>
              <div class="wc-divider"></div>
              <p style="font-size:12px; color:#94a3b8;">
                Supported formats: JPG, JPEG, PNG, WEBP
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.stop()

    if analysis.get("not_animal"):
        st.error(analysis.get("message") or "Please upload an image containing an animal.")
        st.stop()

    # ─── Animal identified ────────────────────────────────────────────────────
    animal_name = normalize_text_maybe(analysis.get("animal_name")) or "Unknown Animal"
    scientific_name = normalize_text_maybe(analysis.get("scientific_name")) or ""
    conservation_status_raw = normalize_text_maybe(analysis.get("conservation_status"))
    pill_suffix, pill_label = status_to_pill(conservation_status_raw)

    with st.container(border=True):
        st.markdown(
            f"""
            <div class="wc-animal-header">
              <div class="wc-animal-name">{animal_name}</div>
              {'<div class="wc-scientific-name">' + scientific_name + '</div>' if scientific_name else ''}
              <span class="wc-pill wc-pill-{pill_suffix}">{pill_label if pill_label else "Unknown Status"}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="wc-divider"></div>', unsafe_allow_html=True)

        # Stats row
        stat_cols = st.columns(2)
        with stat_cols[0]:
            st.markdown(
                f"""
                <div class="wc-stat">
                  <div class="wc-stat-label">📈 Population Trend</div>
                  <div class="wc-stat-value">{analysis.get("population_trend") or "Unknown"}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with stat_cols[1]:
            st.markdown(
                f"""
                <div class="wc-stat">
                  <div class="wc-stat-label">🔢 Est. Population</div>
                  <div class="wc-stat-value">{analysis.get("estimated_population") or "Unknown"}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # ─── Tabs for detailed info ───────────────────────────────────────────────
    tab_labels = ["📖 Background", "🏔️ Habitat & Threats", "🌍 SDG 15", "🛡️ Conservation"]
    tabs = st.tabs(tab_labels)

    with tabs[0]:
        with st.container(border=True):
            st.markdown(
                '<div class="wc-section-title"><span class="icon">📖</span> Background</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div class="wc-info-box">{analysis.get("background") or "No information available."}</div>',
                unsafe_allow_html=True,
            )

    with tabs[1]:
        with st.container(border=True):
            st.markdown(
                '<div class="wc-section-title"><span class="icon">🏔️</span> Habitat</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div class="wc-info-box">{analysis.get("habitat") or "No information available."}</div>',
                unsafe_allow_html=True,
            )
            st.markdown('<div class="wc-divider"></div>', unsafe_allow_html=True)
            st.markdown(
                '<div class="wc-section-title"><span class="icon">⚠️</span> Threats</div>',
                unsafe_allow_html=True,
            )
            threats = analysis.get("threats")
            st.markdown(
                f'<div class="wc-info-box">{threats if threats else "No information available."}</div>',
                unsafe_allow_html=True,
            )

    with tabs[2]:
        with st.container(border=True):
            st.markdown(
                '<div class="wc-section-title"><span class="icon">🌍</span> Connection to SDG 15: Life on Land</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div class="wc-info-box">{analysis.get("sdg_connection") or "No information available."}</div>',
                unsafe_allow_html=True,
            )

    with tabs[3]:
        with st.container(border=True):
            st.markdown(
                '<div class="wc-section-title"><span class="icon">🛡️</span> Conservation Efforts</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div class="wc-info-box">{analysis.get("conservation_efforts") or "No information available."}</div>',
                unsafe_allow_html=True,
            )
