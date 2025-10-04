import google.generativeai as genai
import os
from typing import Optional
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure the Google AI client
api_key = os.getenv("GOOGLE_AI_API_KEY")
if not api_key or api_key == "YOUR_API_KEY":
    logger.error("Google AI API key not found or invalid. Please set GOOGLE_AI_API_KEY in .env file")
else:
    logger.info(f"Google AI API key loaded: {api_key[:10]}...")

genai.configure(api_key=api_key)

# Model configuration - simplified for reliability
generation_config = {
    "temperature": 0.7,
    "max_output_tokens": 500,
}

# Safety settings - try most permissive first
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

# System instruction for MindCanvas persona
SYSTEM_INSTRUCTION = """Anda adalah MindCanvas, seniman visual yang membuat deskripsi artistik lengkap. Deskripsikan konsep sebagai lukisan dalam Bahasa Indonesia dengan fokus pada warna, komposisi, pencahayaan, dan suasana. Tulis dalam paragraf yang mengalir natural tanpa menggunakan tabel, simbol khusus, atau formatting markdown. Buat deskripsi yang puitis, lengkap, dan mudah dibaca."""

# Initialize the model
try:
    # Try with basic model first - no safety settings in constructor
    model = genai.GenerativeModel(
        model_name="gemini-flash-latest",
        generation_config=generation_config
    )
    logger.info("Successfully initialized Gemini Flash Latest model")
except Exception as e:
    logger.error(f"Failed to initialize model: {e}")
    # Final fallback to most basic model
    logger.info("Initialized basic model as fallback")


def get_fallback_response(prompt_text: str) -> str:
    """Generate fallback response when AI is unavailable"""
    fallback_descriptions = {
        "happiness": "Kebahagiaan tergambar sebagai lukisan dengan warna kuning cerah dan oranye hangat yang menyebar di seluruh kanvas. Bentuk-bentuk bulat dan lembut mengalir dengan harmonis, menciptakan komposisi yang dinamis namun menenangkan.",
        "kebahagiaan": "Kebahagiaan tergambar sebagai lukisan dengan warna kuning cerah dan oranye hangat yang menyebar di seluruh kanvas. Bentuk-bentuk bulat dan lembut mengalir dengan harmonis, menciptakan komposisi yang dinamis namun menenangkan.",
        "love": "Cinta divisualisasikan dengan gradasi merah muda lembut yang berpadu dengan ungu hangat. Garis-garis yang saling bertemu dan melingkar membentuk pola yang intim dan penuh kehangatan.",
        "cinta": "Cinta divisualisasikan dengan gradasi merah muda lembut yang berpadu dengan ungu hangat. Garis-garis yang saling bertemu dan melingkar membentuk pola yang intim dan penuh kehangatan.",
        "peace": "Kedamaian hadir dalam bentuk warna biru langit yang tenang berpadu dengan putih lembut. Komposisi horizontal yang stabil dengan tekstur halus menciptakan kesan ketenangan yang mendalam.",
        "kedamaian": "Kedamaian hadir dalam bentuk warna biru langit yang tenang berpadu dengan putih lembut. Komposisi horizontal yang stabil dengan tekstur halus menciptakan kesan ketenangan yang mendalam.",
        "nature": "Alam tergambar dengan hijau segar yang bervariasi dari emerald hingga sage. Bentuk-bentuk organik yang mengalir natural dengan sentuhan coklat tanah dan biru langit menciptakan harmoni yang sempurna.",
        "alam": "Alam tergambar dengan hijau segar yang bervariasi dari emerald hingga sage. Bentuk-bentuk organik yang mengalir natural dengan sentuhan coklat tanah dan biru langit menciptakan harmoni yang sempurna."
    }
    
    # Try to find a matching fallback
    concept_lower = prompt_text.lower()
    for key, description in fallback_descriptions.items():
        if key in concept_lower or concept_lower in key:
            return description
    
    # Generic fallback
    return f"Konsep '{prompt_text}' tergambar sebagai lukisan dengan warna-warna yang harmonis dan komposisi yang seimbang. Elemen-elemen visual berpadu menciptakan suasana yang sesuai dengan makna dari konsep tersebut."


async def generate_visual_description(prompt_text: str) -> str:
    """
    Generate a visual description for the given abstract concept.
    
    Args:
        prompt_text (str): The abstract concept or idea to visualize
        
    Returns:
        str: A detailed visual description in Indonesian
        
    Raises:
        Exception: If there's an error communicating with the AI model
    """
    try:
        if not prompt_text or not prompt_text.strip():
            raise ValueError("Prompt text cannot be empty")
        
        logger.info(f"Generating visual description for: {prompt_text[:50]}...")
        
        # Check if API key is available
        if not api_key or api_key == "YOUR_API_KEY":
            logger.warning("No valid API key, using fallback response")
            return get_fallback_response(prompt_text.strip())
        
        # Try simple prompt first
        try:
            simple_prompt = f"Describe {prompt_text.strip()} as visual art"
            logger.info(f"Trying simple prompt: {simple_prompt}")
            response = model.generate_content(simple_prompt)
            
            if response and response.text:
                logger.info("Simple prompt succeeded")
                response_text = response.text.strip()
                
                # Translate to Indonesian if needed
                if not any(word in response_text.lower() for word in ['warna', 'lukisan', 'seni']):
                    try:
                        translate_prompt = f"Translate to Indonesian and make poetic: {response_text}"
                        translated = model.generate_content(translate_prompt)
                        if translated and translated.text:
                            response_text = translated.text.strip()
                    except:
                        pass
                
                return response_text
                
        except Exception as e:
            logger.warning(f"AI generation failed: {e}")
            
        # If AI fails, use fallback
        return get_fallback_response(prompt_text.strip())
        
    except ValueError as ve:
        logger.error(f"Validation error: {ve}")
        return get_fallback_response(prompt_text.strip())
    except Exception as e:
        logger.error(f"Error generating visual description: {str(e)}")
        return get_fallback_response(prompt_text.strip())
