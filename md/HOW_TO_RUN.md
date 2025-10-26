# How to Run Blueprint

## Quick Start (Recommended)

### Option 1: Manual Start (Most Reliable)

**Step 1: Start Backend**
```bash
# Open a terminal in the Blueprint folder
python api_server.py
```
Wait until you see: `INFO: Uvicorn running on http://0.0.0.0:8000`

**Step 2: Start Frontend** (in a new terminal)
```bash
cd frontend
npm run dev
```
Wait until you see: `Local: http://localhost:5173/`

**Step 3: Open Browser**
- Go to: http://localhost:5173
- Or click the link in the terminal

---

## Option 2: Using start.bat (Windows)

**Prerequisites:**
1. Create a virtual environment first:
   ```bash
   python -m venv .venv
   ```

2. Then run:
   ```bash
   start.bat
   ```

---

## First Time Setup

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Install Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

### 3. Configure API Keys
Make sure you have a `.env` file with your API keys:
```bash
# Create .env from template
cp .env.example .env

# Add your keys to .env
CLAUDE_API_KEY=your-claude-api-key-here
GEMINI_API_KEY=your-gemini-api-key-here
```
**⚠️ Never commit `.env` to git!** See [SECURITY_SETUP.md](../SECURITY_SETUP.md) for details.

---

## Using the App

### 1. Generate Ideas
1. Enter a new hackathon URL (e.g., `https://cal-hacks-11-0.devpost.com`)
2. (Optional) Add past hackathon URLs to learn from
3. Click **"Generate Ideas"**
4. Wait for the scraping and AI analysis to complete

### 2. View Ideas
1. Click **"View Ideas →"** button
2. Browse through your 5-10 AI-generated ideas
3. Each idea shows:
   - Problem statement
   - Solution overview
   - Key technologies
   - Why it wins
   - Implementation roadmap

### 3. Get Step-by-Step Guide
1. **Hover** over any idea card → See green glow
2. **Click** the idea card
3. Wait ~5 seconds for Gemini AI to generate your guide
4. Read your personalized implementation plan with:
   - Time estimates for each step
   - Code examples
   - What to build first
   - Common pitfalls to avoid
   - Quick wins and shortcuts

---

## Troubleshooting

### Backend won't start
- **Error**: `ModuleNotFoundError: No module named 'fastapi'`
- **Fix**: Run `pip install -r requirements.txt`

### Frontend won't start
- **Error**: `npm: command not found`
- **Fix**: Install Node.js from https://nodejs.org/
- **Error**: `Cannot find module`
- **Fix**: Run `cd frontend && npm install`

### Port already in use
- **Backend (8000)**: Kill the process or change port in `api_server.py`
- **Frontend (5173)**: Vite will automatically use next available port

### API Keys
- **Claude**: Get from https://console.anthropic.com/
- **Gemini**: Already configured in `config_settings.example.py`

---

## Current Status

✅ **Backend**: Running on http://localhost:8000  
✅ **Frontend**: Running on http://localhost:5174  
✅ **All Features Working**:
- Idea generation with Claude AI
- Organized data storage
- Beautiful animated UI
- Clickable idea cards
- Step-by-step breakdown with Gemini AI

---

## Quick Command Reference

```bash
# Start backend
python api_server.py

# Start frontend (in new terminal)
cd frontend
npm run dev

# Install dependencies
pip install -r requirements.txt
cd frontend && npm install

# Check if servers are running
netstat -ano | findstr :8000    # Backend
netstat -ano | findstr :5173    # Frontend
```

---

**Need Help?** Check the documentation:
- `QUICK_START.md` - 5-minute quick start
- `LAUNCH_GUIDE.md` - Detailed launch instructions
- `README.md` - Project overview
- `BREAKDOWN_FEATURE_COMPLETE.md` - New breakdown feature docs
