import google.generativeai as genai
import os
import logging
from dotenv import load_dotenv
import random

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure the Google AI client
api_key = os.getenv("GOOGLE_AI_API_KEY")
if not api_key or api_key == "YOUR_API_KEY" or api_key.strip() == "":
    logger.error("Google AI API key not found or invalid. Please set GOOGLE_AI_API_KEY in .env file")
    api_key = None
else:
    try:
        genai.configure(api_key=api_key)
        logger.info(f"Google AI API key loaded successfully: {api_key[:10]}...")
    except Exception as e:
        logger.error(f"Failed to configure Google AI: {e}")
        api_key = None

# --- Improved Model Configuration ---
generation_config = {
    "temperature": 0.8,  # Sedikit lebih tinggi untuk respons yang lebih kreatif
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 1024,  # Tingkatkan untuk jawaban yang lebih panjang dan detail
}

# safety settings - try most permissive first
safety_settings_permissive = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE"
    }
]

# Fallback safety settings
safety_settings_moderate = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_ONLY_HIGH"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_ONLY_HIGH"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_ONLY_HIGH"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_ONLY_HIGH"
    }
]

# --- Persona & Instruksi Sistem yang Lebih Kuat ---
SYSTEM_INSTRUCTION = """
Anda adalah seniman visual ahli yang mendeskripsikan lukisan dalam Bahasa Indonesia.

Tugas: Deskripsikan konsep yang diberikan sebagai lukisan visual yang detail dan puitis.

Format wajib:
- Paragraf 1: Suasana dan atmosfer keseluruhan
- Paragraf 2: Detail warna, komposisi, dan pencahayaan  
- Paragraf 3: Makna dan emosi yang disampaikan

Gunakan bahasa Indonesia yang indah, pisahkan paragraf dengan baris kosong, dan fokus pada konsep yang diminta.
"""

# Initialize the model
model = None
if api_key and api_key != "YOUR_API_KEY":
    try:
        model = genai.GenerativeModel(
            model_name="gemini-flash-latest",
            generation_config=generation_config,
            system_instruction=SYSTEM_INSTRUCTION  # Menggunakan instruksi sistem yang baru
        )
        logger.info("Successfully initialized Gemini Flash model with system instruction.")
    except Exception as e:
        logger.error(f"Failed to initialize Gemini Flash model: {e}")
        try:
            # Fallback tanpa system instruction
            model = genai.GenerativeModel(
                model_name="gemini-flash-latest",
                generation_config=generation_config
            )
            logger.info("Initialized Gemini model without system instruction as fallback")
        except Exception as e2:
            logger.error(f"Failed to initialize any model: {e2}")
            model = None


def get_fallback_response(prompt_text: str) -> str:
    """Generate a more creative fallback response when AI is unavailable."""
    templates = [
        f"Di atas kanvas imajinasi, konsep '{prompt_text}' terlukis dalam simfoni warna yang mendalam. Sebuah palet yang dipilih dengan cermat—dari nada yang paling lembut hingga yang paling berani—berpadu untuk menciptakan suasana yang menggugah jiwa, merefleksikan esensi dari ide itu sendiri.",
        f"Visualisasi dari '{prompt_text}' adalah sebuah tarian antara cahaya dan bayangan. Komposisi yang dinamis membawa mata kita menyusuri setiap detail, di mana bentuk-bentuk simbolis muncul dari kedalaman, menceritakan sebuah kisah tanpa kata tentang makna '{prompt_text}'.",
        f"Jika '{prompt_text}' adalah sebuah lukisan, maka ia akan memiliki tekstur yang kaya dan berlapis. Goresan kuas yang ekspresif menangkap energi dari konsep ini, sementara gradasi warna yang halus mengungkapkan kompleksitas emosi yang tersembunyi di baliknya, menciptakan sebuah karya yang tidak hanya dilihat, tetapi juga dirasakan."
    ]
    return random.choice(templates)


async def generate_visual_description(prompt_text: str) -> str:
    """
    Generate a rich, artistic, and expert visual description for the given abstract concept.
    """
    if not prompt_text or not prompt_text.strip():
        raise ValueError("Prompt text cannot be empty")

    clean_prompt = prompt_text.strip()
    logger.info(f"Generating visual description for: {clean_prompt[:50]}...")
    
    # Debug API key status
    if not api_key:
        logger.error("API key is None - check .env file")
        return get_fallback_response(clean_prompt)
    
    logger.info(f"API key status: {'Valid' if api_key and len(api_key) > 10 else 'Invalid'}")

    if not model:
        logger.warning("AI model not initialized. Using fallback response.")
        return get_fallback_response(clean_prompt)

    try:
        logger.info(f"Sending prompt to AI: '{clean_prompt}'")
        response = model.generate_content(clean_prompt)

        if response and hasattr(response, 'text') and response.text:
            response_text = response.text.strip()
            logger.info(f"AI response length: {len(response_text)} characters")
            
            # Validasi untuk memastikan respons berkualitas
            if len(response_text) > 100 and clean_prompt.lower() in response_text.lower():
                logger.info("Successfully generated AI response with relevant content.")
                return response_text
            elif len(response_text) > 100:
                logger.info("AI generated good response, using it.")
                return response_text
            else:
                logger.warning(f"AI response too short: {response_text[:100]}...")
                return get_fallback_response(clean_prompt)
        else:
            logger.warning("AI response was empty or invalid.")
            return get_fallback_response(clean_prompt)

    except Exception as e:
        logger.error(f"Error during AI generation: {str(e)}")
        logger.error(f"Exception type: {type(e).__name__}")
        return get_fallback_response(clean_prompt)
