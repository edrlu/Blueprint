# Blueprint - Hackathon Idea Generator

Beautiful web interface for generating winning hackathon ideas powered by AI.

## ✨ Features

- 🎨 **Stunning DarkVeil Animation** - Mesmerizing WebGL background
- 🤖 **AI-Powered** - Uses Claude to analyze past winners
- 📊 **Real-time Progress** - Watch the generation process live
- 💎 **Glassmorphic UI** - Modern, aesthetic design
- ⚡ **Fast & Responsive** - Built with React + Vite

## 🚀 Quick Start

### Option 1: Use the Startup Script (Easiest)

```bash
# Double-click start.bat or run:
start.bat
```

This will:
1. Install all dependencies
2. Start the backend API server
3. Start the frontend dev server
4. Open the app in your browser

### Option 2: Manual Start

**Terminal 1 - Backend:**
```bash
# Activate virtual environment
.venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Start API server
python api_server.py
```

**Terminal 2 - Frontend:**
```bash
# Navigate to frontend
cd frontend

# Install dependencies (first time only)
npm install

# Start dev server
npm run dev
```

Then open http://localhost:5173 in your browser.

## 📖 How to Use

1. **Enter Hackathon URL**
   - Paste the Devpost URL of your target hackathon
   - Example: `https://cal-hacks-12-0.devpost.com`

2. **Click "Generate Ideas"**
   - The system will scrape the hackathon rules
   - Analyze 5 past hackathon winners
   - Generate 10 tailored project ideas

3. **View Results**
   - Watch real-time progress updates
   - Get a file with 10 detailed ideas
   - Each idea includes implementation plans

## 🎨 UI Customization

The DarkVeil animation can be customized in `App.jsx`:

```jsx
<DarkVeil 
  hueShift={180}           // Color shift (0-360)
  noiseIntensity={0.05}    // Grain effect
  scanlineIntensity={0.1}  // CRT scanlines
  speed={0.3}              // Animation speed
  scanlineFrequency={0.5}  // Scanline density
  warpAmount={0.3}         // Wave distortion
  resolutionScale={1}      // Performance vs quality
/>
```

## 🛠️ Tech Stack

### Frontend
- **React** - UI framework
- **Vite** - Build tool
- **OGL** - WebGL library for DarkVeil
- **CSS3** - Glassmorphic styling

### Backend
- **FastAPI** - Modern Python API
- **Claude AI** - Idea generation
- **BeautifulSoup** - Web scraping
- **Uvicorn** - ASGI server

## 📁 Project Structure

```
Blueprint/
├── frontend/               # React frontend
│   ├── src/
│   │   ├── App.jsx        # Main component
│   │   ├── App.css        # Styles
│   │   ├── DarkVeil.jsx   # Animation component
│   │   └── DarkVeil.css   # Animation styles
│   └── package.json
├── api_server.py          # FastAPI backend
├── idea_generator.py      # Core logic
├── devpost_scraper.py     # Web scraper
├── claude_analyzer.py     # AI integration
├── config_settings.py     # Configuration
├── requirements.txt       # Python deps
└── start.bat             # Startup script
```

## 🔧 Configuration

### API Keys

Your Claude API key is in `config_settings.py`:

```python
CLAUDE_API_KEY = "your-key-here"
```

### CORS Settings

If you need to change ports, update `api_server.py`:

```python
allow_origins=["http://localhost:5173", "http://localhost:3000"]
```

And update the fetch URL in `App.jsx`:

```javascript
fetch('http://localhost:8000/generate', ...)
```

## 🐛 Troubleshooting

**"Failed to fetch"**
- Make sure the backend is running on port 8000
- Check CORS settings in `api_server.py`

**"Module not found"**
- Run `pip install -r requirements.txt` in the backend
- Run `npm install` in the frontend folder

**Animation not showing**
- Check browser console for WebGL errors
- Try reducing `resolutionScale` for better performance

**Slow generation**
- Normal! Scraping 5 hackathons takes 5-10 minutes
- Watch the progress updates to see what's happening

## 🎯 Tips for Best Results

1. **Use clean URLs** - Remove query parameters
   - ✅ `https://cal-hacks-12-0.devpost.com`
   - ❌ `https://cal-hacks-12-0.devpost.com/?ref=...`

2. **Choose active hackathons** - Recent or ongoing events work best

3. **Be patient** - Quality idea generation takes time

4. **Review all 10 ideas** - Pick 2-3 that match your skills

## 📊 API Endpoints

### POST `/generate`
Generate hackathon ideas

**Request:**
```json
{
  "hackathon_url": "https://cal-hacks-12-0.devpost.com",
  "past_hackathons": ["url1", "url2"] // optional
}
```

**Response:** Server-Sent Events stream with progress updates

### GET `/health`
Health check

**Response:**
```json
{
  "status": "ok",
  "message": "Blueprint API is running"
}
```

## 🌟 Credits

- **DarkVeil Animation** - Beautiful WebGL shader art
- **Claude AI** - Anthropic's language model
- **Devpost** - Hackathon platform data source

## 📝 License

MIT License - Feel free to use and modify!

---

**Built with ❤️ for hackathon enthusiasts**
