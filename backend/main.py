from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import base64
import os
import json
from groq import Groq

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnimalAnalysis(BaseModel):
    name: str
    scientific_name: str
    conservation_status: str
    population_trend: str
    habitat: str
    description: str
    threats: list[str]
    sdg15_connection: str
    conservation_actions: list[str]
    not_animal: bool = False
    message: str = ""

def parse_response(text: str) -> dict:
    """Parse the AI response to extract JSON"""
    try:
        start = text.find('{')
        end = text.rfind('}') + 1
        if start != -1 and end > start:
            return json.loads(text[start:end])
    except:
        pass
    return {"not_animal": True, "message": "Could not parse response"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/analyze")
async def analyze_animal(file: UploadFile = File(...)):
    """Analyze an uploaded animal image using Groq"""
    
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return {"not_animal": True, "message": "Groq API key not configured. Please add GROQ_API_KEY to your .env file."}
    
    try:
        contents = await file.read()
        base64_image = base64.b64encode(contents).decode("utf-8")
        
        file_ext = file.filename.split('.')[-1].lower() if file.filename else 'jpg'
        mime_type = f"image/{'jpeg' if file_ext == 'jpg' else file_ext}"
        
        client = Groq(api_key=api_key)
        
        # Groq vision model IDs can be deprecated/discontinued; keep it configurable.
        model_id = os.environ.get(
            "GROQ_VISION_MODEL",
            "meta-llama/llama-4-scout-17b-16e-instruct",
        )
        
        prompt = """Analyze this image. If it contains an animal, provide detailed information in JSON format.
        
If the image does NOT contain an animal, respond with:
{"not_animal": true, "message": "This image does not appear to contain an animal."}

If it DOES contain an animal, respond with this JSON structure:
{
    "not_animal": false,
    "animal_name": "Common name of the animal",
    "scientific_name": "Scientific/Latin name",
    "conservation_status": "One of: Critically Endangered, Endangered, Vulnerable, Near Threatened, Least Concern, Data Deficient",
    "population_trend": "Increasing, Stable, Decreasing, or Unknown",
    "estimated_population": "Estimated population size/range if known, otherwise \"Unknown\"",
    "habitat": "Describe habitat in detail (3-5 sentences): where it lives (region/ecosystem), typical climate/altitude/elevation if known, and what environmental features matter for its survival (e.g., bamboo/forest type, cover, water availability).",
    "background": "Brief description of the animal, its characteristics and behavior",
    "threats": "Main threats described as a short sentence (comma-separated if needed)",
    "sdg_connection": "Explain how protecting this species connects to UN SDG 15 (Life on Land) - protecting terrestrial ecosystems and biodiversity",
    "conservation_efforts": "Recommended conservation efforts people can take (short sentence)"
}

Respond ONLY with valid JSON, no other text."""

        response = client.chat.completions.create(
            model=model_id,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=1500
        )
        
        result_text = response.choices[0].message.content
        parsed = parse_response(result_text)
        
        return parsed
        
    except Exception as e:
        return {"not_animal": True, "message": f"Error analyzing image: {str(e)}"}