# Blueprint - AI Hackathon Idea Generator

A beautiful web application that generates winning hackathon project ideas by analyzing past winners using Claude AI.

## 🎨 Features

- **Stunning DarkVeil WebGL Background** - Animated shader art
- **AI-Powered Idea Generation** - Uses Claude to analyze patterns
- **Real-time Progress Tracking** - Live updates during generation
- **Beautiful Ideas Display** - Animated list with smooth scrolling
- **Dark Greenish-Grey Theme** - Modern glassmorphic UI

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- Claude API key from https://console.anthropic.com/

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd Blueprint
   ```

2. **Set up Python environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

3. **Set up frontend**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. **Configure API key**
   - Edit `config_settings.py`
   - Add your Claude API key to `CLAUDE_API_KEY`

5. **Run the app**
   ```bash
   .\start.bat  # Windows
   ```

6. **Open browser**
   - Go to http://localhost:5173
   - Enter a hackathon URL
   - Click "Generate Ideas"
   - Wait 5-10 minutes
   - Click "View Ideas" to see results

## 📁 Project Structure

```
Blueprint/
├── frontend/                 # React frontend
│   ├── src/
│   │   ├── App.jsx          # Main home page
│   │   ├── App.css          # Home page styles
│   │   ├── IdeasView.jsx    # Ideas display page
│   │   ├── IdeasView.css    # Ideas page styles
│   │   ├── DarkVeil.jsx     # WebGL animation
│   │   ├── DarkVeil.css     # Animation styles
│   │   ├── AnimatedList.jsx # Animated list component
│   │   ├── AnimatedList.css # List styles
│   │   └── main.jsx         # Router setup
│   └── package.json
├── api_server.py            # FastAPI backend
├── idea_generator.py        # Core idea generation logic
├── devpost_scraper.py       # Web scraping
├── claude_analyzer.py       # AI analysis
├── config_settings.py       # Configuration
├── requirements.txt         # Python dependencies
├── start.bat               # Windows startup script
└── README.md

## 🛠️ Tech Stack

### Frontend
- **React 18** - UI framework
- **Vite** - Build tool
- **React Router** - Navigation
- **Motion** (Framer Motion) - Animations
- **OGL** - WebGL for DarkVeil

### Backend
- **FastAPI** - Modern Python API
- **Claude AI** (Anthropic) - Idea generation
- **BeautifulSoup** - Web scraping
- **Uvicorn** - ASGI server

## 🎯 How It Works

1. **User enters hackathon URL** (e.g., Cal Hacks on Devpost)
2. **Backend scrapes** the hackathon rules and requirements
3. **Backend analyzes** 5 past hackathon winners
4. **Claude AI generates** 10 tailored project ideas
5. **Frontend displays** ideas in beautiful animated cards

## 🎨 Color Scheme

- **Primary**: Dark greenish-grey (#4a6a5f → #5a7a6f)
- **Accent**: #6a8a7f
- **Background**: #0a0a0a
- **DarkVeil Hue**: 150° (greenish tone)

## 📝 API Endpoints

### POST `/generate`
Generate hackathon ideas

**Request:**
```json
{
  "hackathon_url": "https://cal-hacks-12-0.devpost.com",
  "past_hackathons": ["url1", "url2"]  // optional
}
```

**Response:** Server-Sent Events stream with progress updates

### GET `/ideas/{file_path}`
Get parsed ideas from generated file

**Response:**
```json
{
  "ideas": [
    {
      "number": 1,
      "title": "Project Name",
      "problem": "...",
      "solution": "...",
      "technologies": ["React", "Python"],
      "whyItWins": ["reason1", "reason2"],
      "inspiredBy": "...",
      "roadmap": ["step1", "step2"]
    }
  ]
}
```

### GET `/health`
Health check

## 🐛 Known Issues

1. **Scraping limitations** - Some hackathons may not have accessible project galleries
2. **Rate limiting** - Claude API has rate limits
3. **Large prompts** - Very large hackathons may need data summarization

## 🔧 Configuration

### `config_settings.py`
```python
CLAUDE_API_KEY = "your-key-here"
AI_MODEL = "claude"
REQUEST_DELAY = 1
PROJECT_SCRAPE_DELAY = 2
TIMEOUT = 10
```

### Frontend Port
Default: 5173 (Vite default)
To change: Edit `vite.config.js`

### Backend Port
Default: 8000
To change: Edit `api_server.py` (last line)

## 📚 Documentation

- `LAUNCH_GUIDE.md` - Quick start guide
- `README_FRONTEND.md` - Frontend documentation
- `IDEAS_VIEW_COMPLETE.md` - Ideas view features
- `IDEA_GENERATOR_GUIDE.md` - How the AI works

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - Feel free to use and modify!

## 🙏 Credits

- **DarkVeil Animation** - Beautiful WebGL shader art
- **Claude AI** - Anthropic's language model
- **Devpost** - Hackathon platform data source

## 💡 Tips

1. Use clean URLs without query parameters
2. Be patient - generation takes 5-10 minutes
3. Check backend terminal for debug messages
4. Verify Claude API key is valid
5. Ensure internet connection is stable

## 🚨 Troubleshooting

**"Connection error"**
- Check internet connection
- Verify API key at https://console.anthropic.com/
- Check firewall/VPN settings

**"Port already in use"**
- Close existing terminal windows
- Run: `Stop-Process -Name python -Force`

**"Empty ideas"**
- Check backend terminal for errors
- Verify hackathon URL is valid
- Ensure Claude API key works

**"CORS error"**
- Backend should allow all origins in development
- Check `api_server.py` CORS settings

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review backend terminal logs
3. Check browser console (F12)
4. Verify all dependencies are installed

---

**Built with ❤️ for hackathon enthusiasts**
