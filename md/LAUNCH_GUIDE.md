# 🚀 Blueprint Launch Guide

## ✨ What You Have

A beautiful web application with:
- 🎨 **Stunning DarkVeil animation background**
- 🤖 **AI-powered idea generation** (Claude)
- 📊 **Real-time progress tracking**
- 💎 **Glassmorphic UI design**

## 🎯 Quick Launch (2 Steps)

### Step 1: Run the Startup Script

```bash
# Double-click this file or run in terminal:
start.bat
```

This automatically:
- ✅ Installs all dependencies
- ✅ Starts the backend API (port 8000)
- ✅ Starts the frontend (port 5173)
- ✅ Opens your browser

### Step 2: Generate Ideas

1. Enter a hackathon URL (e.g., `https://cal-hacks-12-0.devpost.com`)
2. Click "Generate Ideas"
3. Watch the magic happen! ✨

## 📱 Access Points

Once started, you can access:

- **Frontend UI**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 🎨 What It Looks Like

```
┌─────────────────────────────────────────────┐
│                                             │
│         [DarkVeil Animation Background]     │
│                                             │
│              Blueprint                      │
│     AI-Powered Hackathon Idea Generator    │
│                                             │
│  ┌───────────────────────────────────────┐ │
│  │ Enter hackathon URL...                │ │
│  └───────────────────────────────────────┘ │
│           [Generate Ideas]                  │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │ Status: Scraping rules...           │   │
│  │ Progress:                           │   │
│  │ → Extracting requirements           │   │
│  │ → Analyzing past winners            │   │
│  │ → Generating ideas with Claude      │   │
│  └─────────────────────────────────────┘   │
│                                             │
└─────────────────────────────────────────────┘
```

## 🔧 Manual Start (If Needed)

**Terminal 1 - Backend:**
```bash
.venv\Scripts\activate
python api_server.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

## 📖 How It Works

1. **You enter** a hackathon URL
2. **Backend scrapes** the rules and requirements
3. **Backend analyzes** 5 past hackathon winners
4. **Claude AI generates** 10 tailored project ideas
5. **You receive** a detailed file with implementation plans

## 🎯 Example Usage

```
Input: https://cal-hacks-12-0.devpost.com

Output: idea_generation_20241024_HHMMSS/
  ├── new_hackathon_rules.json
  ├── past_hackathon_winners.json
  └── generated_ideas.txt  ⭐ (10 ideas with details)
```

## 💡 Tips

1. **Use clean URLs** - Remove `?ref=...` parameters
2. **Be patient** - Generation takes 5-10 minutes
3. **Watch progress** - Real-time updates show what's happening
4. **Review all ideas** - Pick 2-3 that match your skills

## 🛠️ Tech Stack

**Frontend:**
- React + Vite
- OGL (WebGL for DarkVeil)
- Glassmorphic CSS

**Backend:**
- FastAPI
- Claude AI (Anthropic)
- BeautifulSoup (scraping)

## 🐛 Troubleshooting

**"Cannot connect to backend"**
- Make sure `api_server.py` is running
- Check http://localhost:8000/health

**"Module not found"**
- Run: `.venv\Scripts\python.exe -m pip install -r requirements.txt`

**Animation not showing**
- Check browser console for errors
- Try a different browser (Chrome/Edge recommended)

## 📚 Documentation

- **Full Frontend Guide**: `README_FRONTEND.md`
- **Idea Generator Guide**: `IDEA_GENERATOR_GUIDE.md`
- **Quick Start**: `QUICK_START.md`

## 🎉 Ready to Go!

Just run `start.bat` and you're all set!

The interface will guide you through the rest.

---

**Happy Hacking! 🚀**
