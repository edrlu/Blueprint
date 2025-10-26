# Quick Start - Intelligent Idea Generator

## What You Have Now

✅ **Intelligent Idea Generator** that:
- Scrapes NEW hackathon rules/requirements
- Analyzes 5 PAST hackathon winners
- Uses Claude AI to generate 10 tailored ideas

## Run It Now!

### Step 1: Basic Command

```bash
python idea_generator.py https://your-new-hackathon.devpost.com
```

**Example:**
```bash
python idea_generator.py https://cal-hacks-11-0.devpost.com
```

This will:
1. Extract rules from Cal Hacks 11.0
2. Analyze 5 default past hackathons
3. Generate 10 ideas adapted to Cal Hacks rules

### Step 2: Check Output

Look in the generated folder: `idea_generation_YYYYMMDD_HHMMSS/`

**Key file:** `generated_ideas.txt` - Your 10 project ideas!

## Advanced Usage

### Choose Specific Past Hackathons

```bash
python idea_generator.py https://new-hackathon.devpost.com \
  --past https://treehacks-2024.devpost.com \
  --past https://hackmit-2024.devpost.com \
  --past https://pennapps-xxiv.devpost.com
```

### Why Choose Specific Hackathons?

Pick past hackathons that:
- Match your new hackathon's theme
- Have similar prize categories
- Are recent (last 1-2 years)

## What Each Idea Includes

1. **Problem Statement** - What problem it solves
2. **Solution Overview** - How it works
3. **Key Technologies** - Specific tech stack
4. **Why It Wins** - Strategic analysis
5. **Inspired By** - Which past winners influenced it
6. **Implementation Roadmap** - How to build it

## Example Workflow

```bash
# 1. Generate ideas for your target hackathon
python idea_generator.py https://treehacks-2025.devpost.com

# 2. Review the generated ideas
cd idea_generation_*/
cat generated_ideas.txt

# 3. Pick your favorite 2-3 ideas
# 4. Validate feasibility
# 5. Add your unique twist
# 6. Build and win! 🏆
```

## Files Created

```
idea_generation_20241024_212704/
├── new_hackathon_rules.json      # Rules from your target hackathon
├── past_hackathon_winners.json   # Winners from 5 past hackathons
└── generated_ideas.txt           # ⭐ YOUR 10 IDEAS HERE
```

## Troubleshooting

**"No Claude API key"**
- Your key is already configured in `config_settings.py`
- If it fails, check the key is correct

**"Could not find projects"**
- Some hackathons hide projects
- Try different past hackathons
- Use the default ones (they work!)

**"Scraping takes too long"**
- Normal! Scraping 5 hackathons + generating ideas takes 5-10 minutes
- Be patient, it's worth it!

## Tips

1. **Run BEFORE the hackathon** - Have ideas ready when it starts
2. **Pick 2-3 favorites** - Don't try to build all 10
3. **Adapt to your skills** - Modify tech stack to what you know
4. **Add your twist** - Make it unique to you
5. **Validate early** - Check if APIs/hardware are available

## Need More Help?

Read the full guide: `IDEA_GENERATOR_GUIDE.md`

## Ready? Let's Go!

```bash
# Replace with YOUR target hackathon
python idea_generator.py https://your-hackathon.devpost.com
```

Good luck! 🚀
