# Blueprint Hackathon Idea Generator - Complete Workflow

## Visual Workflow

```text
┌─────────────────────────────────────────────────────────────────┐
│                    USER STARTS GENERATION                        │
│  (Enters new hackathon URL + optional past hackathon URLs)      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                  STEP 1: SCRAPE NEW HACKATHON                    │
│                                                                   │
│  Input: https://new-hackathon.devpost.com                       │
│  Scrapes: Overview, Rules, Prizes, Schedule                     │
│                                                                   │
│  Output: idea_generation_*/new_hackathon_rules.json             │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              STEP 2: SCRAPE PAST HACKATHONS                      │
│                                                                   │
│  For each past hackathon URL:                                   │
│  ┌─────────────────────────────────────────────────┐           │
│  │  1. Create organized folder:                     │           │
│  │     treehacks_2023_data_YYYYMMDD_HHMMSS/        │           │
│  │                                                  │           │
│  │  2. Scrape winning projects (top 10)            │           │
│  │                                                  │           │
│  │  3. Save to folder:                              │           │
│  │     ├─ winning_projects.json (detailed data)    │           │
│  │     └─ summary.txt (human-readable)             │           │
│  └─────────────────────────────────────────────────┘           │
│                                                                   │
│  Creates folders for:                                            │
│  • treehacks_2023_data_*/                                       │
│  • hackmit_2024_data_*/                                         │
│  • pennapps_xxiv_data_*/                                        │
│  • ... (all past hackathons)                                    │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                STEP 3: AGGREGATE DATA                            │
│                                                                   │
│  Combines all past hackathon data into:                         │
│  • past_hackathon_winners.json (all winners combined)           │
│  • data_index.txt (index of all folders)                        │
│                                                                   │
│  Saved to: idea_generation_*/                                   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│            STEP 4: ANALYZE WITH CLAUDE AI                        │
│                                                                   │
│  Input:                                                          │
│  ├─ new_hackathon_rules.json (what to follow)                  │
│  └─ past_hackathon_winners.json (what worked before)           │
│                                                                   │
│  Claude AI analyzes:                                            │
│  • Success patterns from past winners                           │
│  • Technology trends                                            │
│  • Problem-solution fit                                         │
│  • Innovation approaches                                        │
│                                                                   │
│  Generates: 10 innovative project ideas                         │
│                                                                   │
│  Output: idea_generation_*/generated_ideas.txt                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                STEP 5: DISPLAY IN UI                             │
│                                                                   │
│  Frontend reads generated_ideas.txt and displays:               │
│  • Animated list of 10 ideas                                    │
│  • Each idea with:                                              │
│    - Problem statement                                          │
│    - Solution overview                                          │
│    - Key technologies                                           │
│    - Why it wins                                                │
│    - Implementation roadmap                                     │
└─────────────────────────────────────────────────────────────────┘
```

## Data Organization After Completion

```text
Blueprint/
│
├── idea_generation_20251025_185706/  ← MAIN OUTPUT
│   ├── new_hackathon_rules.json      ← Rules for new hackathon
│   ├── past_hackathon_winners.json   ← All past winners (aggregated)
│   ├── data_index.txt                ← Index of data folders
│   └── generated_ideas.txt           ← 10 AI-generated ideas ✨
│
├── treehacks_2023_data_20251025_185706/  ← ORGANIZED DATA
│   ├── winning_projects.json         ← 10 winning projects
│   └── summary.txt                   ← Quick summary
│
├── hackmit_2024_data_20251025_185710/
│   ├── winning_projects.json
│   └── summary.txt
│
├── pennapps_xxiv_data_20251025_185715/
│   ├── winning_projects.json
│   └── summary.txt
│
└── ... (more hackathon folders)
```

## Key Features

### 🗂️ Organized Storage
- Each hackathon gets its own folder
- Easy to navigate and verify data
- No clutter in the main directory

### 📊 Aggregated Analysis
- All data combined for Claude AI analysis
- Index file for quick reference
- Human-readable summaries

### 🤖 AI-Powered Generation
- Learns from past winners
- Follows new hackathon rules
- Generates 10 unique ideas

### 🎨 Beautiful UI
- Animated idea display
- Real-time progress updates
- Dark greenish-grey theme

## Example Usage

### Via Command Line

```bash
python idea_generator.py https://new-hackathon.devpost.com \
  --past https://treehacks-2023.devpost.com \
  --past https://hackmit-2024.devpost.com
```

### Via Web UI

1. Open http://localhost:5174
2. Enter new hackathon URL
3. (Optional) Add past hackathon URLs
4. Click "Generate Ideas"
5. Watch the magic happen! ✨

## Data Flow Summary

```text
NEW HACKATHON URL
       ↓
   [SCRAPE]
       ↓
new_hackathon_rules.json ──┐
                           │
PAST HACKATHON URLS        │
       ↓                   │
   [SCRAPE]                │
       ↓                   │
Individual Folders         │
  ├─ treehacks_2023/       │
  ├─ hackmit_2024/         │
  └─ pennapps_xxiv/        │
       ↓                   │
   [AGGREGATE]             │
       ↓                   │
past_hackathon_winners.json├─→ [CLAUDE AI ANALYSIS]
                           │           ↓
                           └─→  generated_ideas.txt
                                       ↓
                                  [DISPLAY IN UI]
                                       ↓
                                  Beautiful Ideas! 🎉
```

---

**Last Updated**: October 25, 2025
