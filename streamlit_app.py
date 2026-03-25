import base64
import json
from typing import Any, Dict

import streamlit as st
from groq import Groq


DEFAULT_MODEL_ID = "meta-llama/llama-4-scout-17b-16e-instruct"

st.set_page_config(page_title="Wildlife Scanner", layout="wide")


def render_css() -> None:
    st.markdown(
        """
        <style>
          :root{
            --brand:#1f6f4a;
            --brand-dark:#16553a;
            --card:#ffffff;
            --muted:#6b7280;
            --danger:#dc2626;
            --vulnerable:#f59e0b;
            --safe:#16a34a;
            --bg:#f3f4f6;
          }
          html, body, .stApp {
            background: var(--bg) !important;
            color: #111827 !important;
          }

          .wc-header{
            background: linear-gradient(180deg, var(--brand), var(--brand-dark));
            color: white;
            padding: 22px 26px;
            border-radius: 14px;
            margin-bottom: 18px;
          }
          .wc-title{ font-size: 30px; font-weight: 800; margin-bottom: 4px; }
          .wc-subtitle{ color: rgba(255,255,255,0.85); font-size: 14px; }

          .wc-card{
            background: var(--card) !important;
            border: 1px solid rgba(0,0,0,0.06);
            border-radius: 16px;
            padding: 18px;
            box-shadow: 0 1px 0 rgba(0,0,0,0.02);
          }
          .wc-upload{
            border: 2px dashed rgba(31,111,74,0.25);
            border-radius: 16px;
            padding: 16px;
            text-align: center;
            background: rgba(31,111,74,0.03);
          }

          .wc-pill{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            padding: 6px 12px;
            border-radius: 999px;
            color: white;
            font-weight: 700;
            font-size: 12px;
            letter-spacing: 0.2px;
          }
          .wc-pill-danger{ background: var(--danger); }
          .wc-pill-vulnerable{ background: var(--vulnerable); }
          .wc-pill-safe{ background: var(--safe); }
          .wc-pill-neutral{ background: #6b7280; }

          /* Streamlit buttons */
          .stButton > button{
            width: 100%;
            background: var(--brand) !important;
            color: white !important;
            font-weight: 800 !important;
            border-radius: 12px !important;
            border: none !important;
            padding: 10px 14px !important;
          }
          .stButton > button:hover{
            background: var(--brand-dark) !important;
          }
          .stButton > button:disabled{
            opacity: 0.6;
          }

          /* Tabs (Streamlit uses BaseWeb components) */
          div[data-baseweb="tablist"] button{
            color: #374151 !important;
            background: transparent !important;
          }
          div[data-baseweb="tablist"] button[aria-selected="true"]{
            color: #ffffff !important;
            border: 1px solid rgba(31,111,74,0.25) !important;
            background: #16a34a !important;
            border-radius: 10px !important;
          }
          /* Make sure inner label text is also forced (Streamlit renders nested spans). */
          div[data-baseweb="tablist"] button *{
            color: inherit !important;
          }
          div[data-baseweb="tablist"] button[aria-selected="true"] *{
            color: #ffffff !important;
          }
          /* SVG icons (if any) sometimes keep a different fill color. */
          div[data-baseweb="tablist"] button[aria-selected="true"] svg{
            fill: #ffffff !important;
            color: #ffffff !important;
          }

          /* Override Streamlit's dark card backgrounds inside our wrappers */
          .wc-card, .wc-card *{
            color: inherit !important;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )


def status_to_pill(status: str | None) -> tuple[str, str]:
    """
    Returns (pill_class_suffix, label) for the conservation status.
    """
    if not status:
        return ("neutral", "Unknown Status")
    s = status.lower()
    if "critically" in s or "endangered" in s:
        # Treat "Endangered" and "Critically Endangered" as danger.
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
    """
    Extract the JSON object from the model response and parse it.
    Returns a fallback structure if parsing fails.
    """
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
        model_id = st.secrets["GROQ_VISION_MODEL"]  # optional
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

render_css()

st.markdown(
    """
    <div class="wc-header">
      <div class="wc-title">Wildlife Scanner</div>
      <div class="wc-subtitle">Identify animals and learn about their conservation status and SDG 15 connection.</div>
      <div style="margin-top:10px;">
        <span class="wc-pill wc-pill-safe">SDG 15: Life on Land</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)


if "analysis" not in st.session_state:
    st.session_state.analysis = None

col_left, col_right = st.columns([1, 2])

with col_left:
    with st.container(border=True):
        st.markdown("### Upload an Animal Image")

        uploaded_file = st.file_uploader(
            "Upload an Animal Image",
            type=["jpg", "jpeg", "png", "webp"],
            label_visibility="collapsed",
        )

        file_bytes = None
        if uploaded_file is not None:
            file_bytes = uploaded_file.getvalue()
            st.image(file_bytes, use_container_width=True, caption=uploaded_file.name)
            st.caption(f"File size: {len(file_bytes) / 1024:.1f} KB")

        if uploaded_file is not None and st.button("Analyze Animal", type="primary"):
                with st.spinner("Analyzing..."):
                    try:
                        st.session_state.analysis = analyze_image(file_bytes, uploaded_file.name)
                    except Exception as e:
                        st.session_state.analysis = {
                            "not_animal": True,
                            "message": f"Error analyzing image: {str(e)}",
                        }

    with st.container(border=True):
        st.markdown("### About SDG 15: Life on Land")
        st.write(
            "Protect, restore and promote sustainable use of terrestrial ecosystems. "
            "Sustainably manage forests, combat desertification, and halt and reverse land "
            "degradation and halt biodiversity loss."
        )

with col_right:
    analysis = st.session_state.analysis
    if not analysis:
        st.info(
            "Upload an image of any animal to learn about its conservation status and how it connects to SDG 15."
        )
        st.stop()

    if analysis.get("not_animal"):
        st.error(analysis.get("message") or "Please upload an image containing an animal.")
        st.stop()

    animal_name = normalize_text_maybe(analysis.get("animal_name")) or "Unknown Animal"
    scientific_name = normalize_text_maybe(analysis.get("scientific_name")) or ""
    conservation_status_raw = normalize_text_maybe(analysis.get("conservation_status"))
    pill_suffix, pill_label = status_to_pill(conservation_status_raw)

    with st.container(border=True):
        st.markdown(
            f"<h2 style='margin-top:0;margin-bottom:6px;'>{animal_name}</h2>",
            unsafe_allow_html=True,
        )
        if scientific_name:
            st.markdown(
                f"<div style='color:rgba(0,0,0,0.55); font-style:italic; margin-bottom:12px;'>{scientific_name}</div>",
                unsafe_allow_html=True,
            )

        st.markdown(
            f'<span class="wc-pill wc-pill-{pill_suffix}">{pill_label if pill_label else "Unknown Status"}</span>',
            unsafe_allow_html=True,
        )

        pop_row = st.columns(2)
        with pop_row[0]:
            st.markdown("#### Population Trend")
            st.write(analysis.get("population_trend") or "Unknown")
        with pop_row[1]:
            st.markdown("#### Est. Population")
            st.write(analysis.get("estimated_population") or "Unknown")

    tab_labels = ["Background", "Habitat & Threats", "SDG 15", "Conservation"]
    # Streamlit's built-in `st.tabs` styling is hard to control cross-themes, so use `st.radio`
    # to guarantee text stays visible.
    active_tab = st.radio(
        label="",
        options=tab_labels,
        horizontal=False,
        index=tab_labels.index(st.session_state.get("active_tab", "Background")),
        label_visibility="collapsed",
    )
    st.session_state.active_tab = active_tab

    if active_tab == "Background":
        with st.container(border=True):
            st.markdown("### Background")
            st.write(analysis.get("background") or "No information available.")

    elif active_tab == "Habitat & Threats":
        with st.container(border=True):
            st.markdown("### Habitat")
            st.write(analysis.get("habitat") or "No information available.")
            st.divider()
            st.markdown("### Threats")
            threats = analysis.get("threats")
            st.write(threats if threats else "No information available.")

    elif active_tab == "SDG 15":
        with st.container(border=True):
            st.markdown("### Connection to SDG 15: Life on Land")
            st.write(analysis.get("sdg_connection") or "No information available.")

    elif active_tab == "Conservation":
        with st.container(border=True):
            st.markdown("### Conservation Efforts")
            st.write(analysis.get("conservation_efforts") or "No information available.")

