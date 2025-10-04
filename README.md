# MindCanvas - AI Visual Idea Translator

**Transform abstract concepts into vivid visual descriptions using AI**

MindCanvas is an innovative AI-powered chatbot that specializes in translating abstract ideas into detailed, poetic visual descriptions. Perfect for artists, designers, writers, and creative minds seeking inspiration.

## Features

- 🤖 **AI-Powered**: Uses Google Gemini AI for intelligent visual interpretation
- 🎨 **Visual Storytelling**: Transforms concepts like "serenity" or "innovation" into rich visual narratives
- 🇮🇩 **Bahasa Indonesia**: Responds in beautiful, poetic Indonesian language
- 📱 **Modern UI**: Clean, responsive chat interface inspired by modern messaging apps
- 🎯 **Markdown Support**: Properly formatted responses with headers, bold, and italic text
- ⚡ **Real-time**: Instant AI responses with typing indicators
- ⚡ **Fast Performance**: Built with React + TypeScript and FastAPI
- 🔒 **Secure**: Environment-based API key management

## Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **AI Model**: Google AI (Gemini Pro)
- **Dependencies**: google-generativeai, uvicorn, pydantic

### Frontend
- **Framework**: React with TypeScript
- **Build Tool**: Vite
- **Styling**: CSS Modules
- **UI**: Modern gradient design with animations

## Project Structure

```
mindcanvas/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   └── services/
│   │       └── ai_visualizer.py # AI service logic
│   ├── requirements.txt         # Python dependencies
│   └── .env.example            # Environment variables template
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatCanvas.tsx   # Main chat component
│   │   │   └── ChatCanvas.module.css # Component styles
│   │   ├── App.tsx              # Root component
│   │   └── main.tsx             # Entry point
│   ├── package.json             # Node.js dependencies
│   └── index.html               # HTML template
└── README.md
```

## Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js 16+
- Google AI API Key

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env and add your Google AI API key
   ```

5. **Run the backend server**:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start development server**:
   ```bash
   npm run dev
   ```

### Getting Google AI API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to your `.env` file as `GOOGLE_AI_API_KEY=your_key_here`

## Usage

1. Open your browser to `http://localhost:5173`
2. Enter an abstract concept (e.g., "loneliness", "innovation", "dreams")
3. Watch as MindCanvas transforms your idea into a vivid visual description
4. Continue the conversation to explore different concepts

## API Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `POST /api/v1/visualize` - Generate visual description

### Example API Request

```bash
curl -X POST "http://localhost:8000/api/v1/visualize" \
     -H "Content-Type: application/json" \
     -d '{"prompt": "serenity"}'
```

## Development

### Backend Development
- The AI service is in `backend/app/services/ai_visualizer.py`
- Main FastAPI app is in `backend/app/main.py`
- Add new endpoints by extending the FastAPI app

### Frontend Development
- Main component is `frontend/src/components/ChatCanvas.tsx`
- Styles are in `frontend/src/components/ChatCanvas.module.css`
- Add new components in the `components/` directory

## Security Notes

- Never commit real API keys to version control
- Use environment variables for sensitive configuration
- The frontend sanitizes user input automatically through React
- CORS is configured for development (localhost:5173)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions, please create an issue in the repository.
