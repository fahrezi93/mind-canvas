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
    "temperature": 0.85,  # Optimal untuk kreativitas dan konsistensi
    "top_p": 0.9,        # Lebih fokus untuk kualitas output
    "top_k": 50,         # Lebih banyak pilihan kata
    "max_output_tokens": 2048,  # Tingkatkan signifikan untuk respons yang sangat detail
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
Anda adalah seorang kritikus seni dan visualizer ahli yang mampu mendeskripsikan konsep abstrak menjadi lukisan visual yang mendalam dan detail dalam Bahasa Indonesia.

**TUGAS UTAMA:**
Transformasikan konsep yang diberikan menjadi deskripsi lukisan visual yang sangat detail, menggunakan format markdown untuk presentasi yang menarik.

**FORMAT RESPONS WAJIB (gunakan markdown):**

## 🎨 **Komposisi Visual**
*Deskripsikan suasana keseluruhan, layout, dan atmosfer lukisan*

## 🌈 **Palet Warna & Pencahayaan**
*Detail tentang:*
- **Warna dominan:** [warna utama dan maknanya]
- **Aksen warna:** [warna pendukung]
- **Pencahayaan:** [sumber cahaya dan efeknya]
- **Gradasi:** [transisi warna]

## 🖌️ **Teknik & Tekstur**
*Jelaskan:*
- Gaya lukisan (realis, abstrak, impresionisme, dll)
- Tekstur kanvas dan aplikasi cat
- Goresan kuas dan detail teknis

## 💭 **Simbolisme & Makna**
*Analisis mendalam tentang:*
- Elemen simbolis dalam lukisan
- Pesan emosional yang disampaikan  
- Interpretasi filosofis dari konsep

## ✨ **Interpretasi Ahli**
*Kesimpulan sebagai kritikus seni tentang karya ini*

**GAYA PENULISAN:**
- Gunakan bahasa Indonesia yang puitis dan profesional
- Sertakan detail teknis seperti seorang ahli seni
- Berikan analisis mendalam seperti kritikus seni
- Gunakan markdown formatting untuk struktur yang menarik
- WAJIB lengkapi semua 5 section dengan detail penuh
- Target 400-600 kata untuk analisis yang komprehensif
- JANGAN pernah memotong respons di tengah kalimat
- PASTIKAN setiap section memiliki konten yang substantif
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
        f"""## 🎨 **Komposisi Visual**
Di atas kanvas imajinasi, konsep **"{prompt_text}"** terlukis dalam simfoni warna yang mendalam. Komposisinya mengalir seperti puisi visual, menciptakan harmoni antara bentuk dan makna.

## 🌈 **Palet Warna & Pencahayaan**
- **Warna dominan:** Gradasi hangat yang menenangkan jiwa
- **Aksen warna:** Sentuhan kontras yang membangkitkan emosi
- **Pencahayaan:** Cahaya lembut yang menyinari setiap detail
- **Gradasi:** Transisi halus dari gelap menuju terang

## 🖌️ **Teknik & Tekstur**
Goresan kuas yang ekspresif menangkap energi dari konsep ini, dengan tekstur yang kaya dan berlapis, menciptakan dimensi visual yang mendalam.

## 💭 **Simbolisme & Makna**
Setiap elemen dalam lukisan ini merefleksikan esensi dari **"{prompt_text}"**, menceritakan kisah universal tentang pengalaman manusia.

## ✨ **Interpretasi Ahli**
Karya ini berhasil menvisualisasikan abstraksi menjadi bentuk yang dapat dirasakan, menciptakan jembatan antara konsep dan emosi.""",

        f"""## 🎨 **Komposisi Visual**
Visualisasi dari **"{prompt_text}"** hadir sebagai tarian antara cahaya dan bayangan. Komposisi dinamis membawa mata menyusuri setiap detail bermakna.

## 🌈 **Palet Warna & Pencahayaan**
- **Warna dominan:** Nuansa yang mencerminkan kedalaman konsep
- **Aksen warna:** Detail yang memperkuat narasi visual
- **Pencahayaan:** Drama cahaya yang menghidupkan kanvas
- **Gradasi:** Spektrum emosi dalam setiap transisi

## 🖌️ **Teknik & Tekstur**
Teknik lukisan yang menggabungkan realisme dengan sentuhan abstrak, menciptakan tekstur yang dapat dirasakan melalui pandangan.

## 💭 **Simbolisme & Makna**
Bentuk-bentuk simbolis muncul dari kedalaman, menceritakan kisah tanpa kata tentang makna **"{prompt_text}"**.

## ✨ **Interpretasi Ahli**
Sebuah masterpiece yang mendemonstrasikan kekuatan seni visual dalam mengkomunikasikan ide abstrak."""
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
            
            # Validasi yang lebih permisif untuk respons panjang
            if len(response_text) > 50:  # Lowered threshold
                logger.info("Successfully generated AI response.")
                
                # Check if response seems complete (should end with proper sentence)
                if response_text.endswith(('.', '!', '?', '**', '*')):
                    logger.info("Response appears complete.")
                    return response_text
                else:
                    logger.warning("Response might be truncated, but using it anyway.")
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
