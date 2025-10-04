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

# Model configuration
generation_config = {
    "temperature": 0.8,  # Slightly lower for more focused responses
    "top_p": 0.95,
    "max_output_tokens": 800,  # Balanced length for complete but concise responses
    "top_k": 40,
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
SYSTEM_INSTRUCTION = """Anda adalah MindCanvas, seniman visual yang membuat deskripsi artistik ringkas namun lengkap. Deskripsikan konsep sebagai lukisan dalam Bahasa Indonesia dengan fokus pada: warna utama, komposisi, pencahayaan, dan suasana. Gunakan 2-3 paragraf dengan format markdown. Buat deskripsi yang puitis tapi tidak terlalu panjang."""

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
    model = genai.GenerativeModel(model_name="gemini-flash-latest")
    logger.info("Initialized basic model as fallback")


async def generate_visual_description(prompt_text: str) -> str:
    """
    Generate a visual description for the given abstract concept using Google AI.
    
    Args:
        prompt_text (str): The abstract concept or idea to visualize
        
    Returns:
        str: A detailed, poetic visual description of the concept
        
    Raises:
        Exception: If there's an error communicating with the AI model
    """
    try:
        if not prompt_text or not prompt_text.strip():
            raise ValueError("Prompt text cannot be empty")
        
        logger.info(f"Generating visual description for: {prompt_text[:50]}...")
        
        # Try multiple prompt variations to avoid safety blocks
        prompts_to_try = [
            f"Deskripsikan '{prompt_text.strip()}' sebagai lukisan dalam Bahasa Indonesia. Fokus pada warna, bentuk, dan suasana. Gunakan format: ## untuk judul, **tebal** untuk penekanan. Buat deskripsi yang lengkap tapi ringkas.",
            f"Gambarkan konsep '{prompt_text.strip()}' sebagai karya seni visual dalam Bahasa Indonesia. Jelaskan komposisi, warna, dan atmosfer dengan format markdown yang rapi.",
            f"Visual description of '{prompt_text.strip()}' as artwork in Indonesian. Include colors, composition, mood. Use markdown format. Keep it complete but concise."
        ]
        
        response = None
        last_error = None
        
        for i, prompt in enumerate(prompts_to_try):
            try:
                logger.info(f"Trying prompt variation {i+1}: {prompt[:80]}...")
                response = model.generate_content(prompt)
                
                # Check if we got a valid response
                if response.candidates and len(response.candidates) > 0:
                    candidate = response.candidates[0]
                    if candidate.finish_reason == 1:  # STOP (success)
                        logger.info(f"Success with prompt variation {i+1}")
                        break
                    elif candidate.finish_reason == 3:  # LENGTH (truncated due to max_tokens)
                        logger.warning(f"Response truncated due to length limit, but using it anyway")
                        break  # Still use the response even if truncated
                    elif candidate.finish_reason == 2:  # SAFETY
                        logger.warning(f"Prompt variation {i+1} blocked by safety filter")
                        continue
                    else:
                        logger.warning(f"Unexpected finish_reason: {candidate.finish_reason}")
                        continue
                else:
                    logger.warning(f"No candidates in response for prompt variation {i+1}")
                    continue
                    
            except Exception as e:
                logger.warning(f"Prompt variation {i+1} failed: {e}")
                last_error = e
                continue
        
        if not response:
            raise Exception("Semua variasi prompt gagal. Coba konsep yang lebih sederhana seperti 'alam', 'seni', atau 'warna'.")
        
        # Extract text from successful response
        try:
            if hasattr(response, 'text') and response.text:
                response_text = response.text.strip()
            else:
                # Try to extract from candidates
                candidate = response.candidates[0]
                if candidate.content and candidate.content.parts:
                    text_parts = []
                    for part in candidate.content.parts:
                        if hasattr(part, 'text') and part.text:
                            text_parts.append(part.text)
                    if text_parts:
                        response_text = ''.join(text_parts).strip()
                    else:
                        raise Exception("Tidak dapat mengekstrak teks dari response")
                else:
                    raise Exception("Response tidak mengandung konten teks")
        except Exception as extract_error:
            logger.error(f"Error extracting text: {extract_error}")
            raise Exception("Gagal mengekstrak deskripsi visual. Silakan coba lagi dengan konsep yang berbeda.")
        
        # Check if response was truncated and add note if needed
        if response.candidates and len(response.candidates) > 0:
            candidate = response.candidates[0]
            if candidate.finish_reason == 3:  # LENGTH (truncated)
                response_text += "\n\n---\n*💡 Deskripsi ini dipotong karena terlalu panjang. Coba gunakan konsep yang lebih spesifik untuk hasil yang lebih fokus.*"
                logger.warning("Response was truncated due to length limit")
        
        logger.info("Visual description generated successfully")
        return response_text
        
    except ValueError as ve:
        logger.error(f"Validation error: {ve}")
        raise ve
    except Exception as e:
        logger.error(f"Error generating visual description: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise Exception(f"Failed to generate visual description: {str(e)}")
