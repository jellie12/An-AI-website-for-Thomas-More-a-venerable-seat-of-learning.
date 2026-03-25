import base64
import json
from io import BytesIO
from typing import Any, Dict

import streamlit as st
from groq import Groq


DEFAULT_MODEL_ID = "meta-llama/llama-4-scout-17b-16e-instruct"


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
    api_key = st.secrets["GROQ_API_KEY"]

    try:
        model_id = st.secrets["GROQ_VISION_MODEL"]
    except Exception:
        model_id = DEFAULT_MODEL_ID

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


st.set_page_config(page_title="Wildlife Scanner", layout="wide")

st.title("Wildlife Scanner")
st.caption("Identify animals and learn about their conservation status and SDG 15 connection.")

uploaded_file = st.file_uploader("Upload an Animal Image", type=["jpg", "jpeg", "png", "webp"])

if "analysis" not in st.session_state:
    st.session_state.analysis = None

col_left, col_right = st.columns([1, 2])

with col_left:
    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        st.image(file_bytes, use_container_width=True, caption=uploaded_file.name)

        if st.button("Analyze Animal", type="primary", use_container_width=True):
            with st.spinner("Analyzing..."):
                try:
                    st.session_state.analysis = analyze_image(file_bytes, uploaded_file.name)
                except Exception as e:
                    st.session_state.analysis = {
                        "not_animal": True,
                        "message": f"Error analyzing image: {str(e)}",
                    }

with col_right:
    analysis = st.session_state.analysis
    if not analysis:
        st.info("Upload an image of any animal to learn about its conservation status and how it connects to SDG 15.")
        st.stop()

    if analysis.get("not_animal"):
        st.error(analysis.get("message") or "Please upload an image containing an animal.")
        st.stop()

    animal_name = analysis.get("animal_name") or "Unknown Animal"
    scientific_name = analysis.get("scientific_name") or ""
    conservation_status = analysis.get("conservation_status") or "Unknown Status"

    st.subheader(animal_name)
    if scientific_name:
        st.caption(scientific_name)

    tabs = st.tabs(["Background", "Habitat & Threats", "SDG 15", "Conservation"])

    with tabs[0]:
        st.write(analysis.get("background") or "No information available.")

    with tabs[1]:
        st.write("### Habitat")
        st.write(analysis.get("habitat") or "No information available.")
        st.write("### Threats")
        st.write(analysis.get("threats") or "No information available.")

    with tabs[2]:
        st.write("### Connection to SDG 15: Life on Land")
        st.write(analysis.get("sdg_connection") or "No information available.")

    with tabs[3]:
        st.write("### Conservation Efforts")
        st.write(analysis.get("conservation_efforts") or "No information available.")

