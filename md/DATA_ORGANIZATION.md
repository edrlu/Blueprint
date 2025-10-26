# Data Organization Guide

## Overview

The Blueprint Hackathon Idea Generator now saves all scraped data in **organized folders** for easy access and analysis.

## Folder Structure

When you run the idea generator, it creates the following structure:

```
Blueprint/
├── idea_generation_YYYYMMDD_HHMMSS/     # Main output folder
│   ├── new_hackathon_rules.json         # Rules for the new hackathon
│   ├── past_hackathon_winners.json      # Aggregated data from all past hackathons
│   ├── data_index.txt                   # Index of all data folders
│   └── generated_ideas.txt              # AI-generated ideas
│
├── treehacks_2023_data_YYYYMMDD_HHMMSS/ # Individual hackathon folder
│   ├── winning_projects.json            # Detailed winning projects data
│   └── summary.txt                      # Human-readable summary
│
├── hackmit_2024_data_YYYYMMDD_HHMMSS/   # Another hackathon folder
│   ├── winning_projects.json
│   └── summary.txt
│
└── ... (more hackathon folders)
```

## File Descriptions

### Main Output Folder (`idea_generation_*`)

**`new_hackathon_rules.json`**
- Contains rules, requirements, prizes, and schedule for the NEW hackathon you want to participate in
- Includes overview, rules, prizes, and schedule tabs
- Used by Claude AI to ensure generated ideas follow the rules

**`past_hackathon_winners.json`**
- Aggregated data from ALL past hackathons scraped
- Contains winning projects from each hackathon
- References to individual data folders
- Used by Claude AI to learn from past winners

**`data_index.txt`**
- Human-readable index of all scraped hackathons
- Shows folder locations and winner counts
- Quick reference for navigating the data

**`generated_ideas.txt`**
- AI-generated hackathon project ideas
- Based on analysis of past winners and new hackathon rules
- Contains 10 detailed ideas with implementation roadmaps

### Individual Hackathon Folders (`*_data_*`)

**`winning_projects.json`**
- Detailed data for all winning projects from this specific hackathon
- Includes:
  - Project name and tagline
  - Full description
  - Technologies used
  - Team members
  - Awards won
  - Project links

**`summary.txt`**
- Human-readable summary of the hackathon
- Quick overview of:
  - Hackathon name and URL
  - Number of winning projects scraped
  - Total projects in the hackathon
  - List of winner names and taglines

## Data Flow

```
1. SCRAPE NEW HACKATHON
   └─> new_hackathon_rules.json

2. SCRAPE PAST HACKATHONS
   ├─> treehacks_2023_data_*/
   │   ├─> winning_projects.json
   │   └─> summary.txt
   ├─> hackmit_2024_data_*/
   │   ├─> winning_projects.json
   │   └─> summary.txt
   └─> ... (more folders)

3. AGGREGATE DATA
   ├─> past_hackathon_winners.json (all winners combined)
   └─> data_index.txt (index of folders)

4. ANALYZE WITH CLAUDE AI
   ├─ Input: new_hackathon_rules.json + past_hackathon_winners.json
   └─> generated_ideas.txt (AI-generated ideas)
```

## Benefits of Organized Structure

✅ **Easy Navigation**: Each hackathon has its own folder
✅ **Data Preservation**: Individual folders keep data separate and safe
✅ **Quick Reference**: Summary files provide quick overviews
✅ **Scalability**: Can scrape hundreds of hackathons without clutter
✅ **Debugging**: Easy to verify what data was scraped for each hackathon
✅ **Reusability**: Can reuse scraped data without re-scraping

## Accessing the Data

### Via Python Code

```python
from idea_generator import IdeaGenerator

generator = IdeaGenerator(
    new_hackathon_url="https://your-hackathon.devpost.com",
    past_hackathon_urls=[
        "https://treehacks-2023.devpost.com",
        "https://hackmit-2024.devpost.com"
    ]
)

# Scrape and organize data
winners_data = generator.scrape_all_past_hackathons()

# Access individual hackathon data
for hackathon in winners_data:
    print(f"Folder: {hackathon['data_folder']}")
    print(f"Winners: {len(hackathon['winning_projects'])}")
```

### Via File System

1. Navigate to the Blueprint folder
2. Look for folders ending with `_data_YYYYMMDD_HHMMSS`
3. Open `summary.txt` for a quick overview
4. Open `winning_projects.json` for detailed data

### Via Web UI

The frontend automatically reads from the organized folders and displays the data in a beautiful animated interface.

## Data Retention

- All data folders are **gitignored** to keep your repository clean
- Data is stored locally on your machine
- You can safely delete old folders to free up space
- The `.gitignore` file protects your scraped data from being committed

## Example Output

```
idea_generation_20251025_185706/
├── new_hackathon_rules.json (80 KB)
├── past_hackathon_winners.json (222 KB)
├── data_index.txt (306 bytes)
└── generated_ideas.txt (15 KB)

treehacks_2023_data_20251025_185706/
├── winning_projects.json (175 KB)
└── summary.txt (342 bytes)

hackmit_2024_data_20251025_185710/
├── winning_projects.json (198 KB)
└── summary.txt (389 bytes)
```

## Troubleshooting

**Q: Why are some folders empty?**
A: If a hackathon's project gallery is not accessible or the scraper encounters errors, the folder may be created but remain empty.

**Q: Can I delete old data folders?**
A: Yes! Old folders are safe to delete. Each run creates new timestamped folders.

**Q: How do I view the data?**
A: Use the `show_data_structure.py` script or open the JSON/TXT files directly.

**Q: Where is the data used by Claude AI?**
A: Claude uses the aggregated `past_hackathon_winners.json` file in the main `idea_generation_*` folder.

---

**Last Updated**: October 25, 2025
