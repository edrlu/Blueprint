# Intelligent Hackathon Idea Generator

Generate winning hackathon ideas by learning from past winners and adapting them to new hackathon requirements!

## How It Works

1. **Scrapes NEW hackathon** → Extracts rules, themes, requirements, prizes
2. **Scrapes 5 PAST hackathons** → Analyzes winning projects and success patterns
3. **Uses Claude AI** → Synthesizes ideas that combine past winner strategies with new requirements

## Quick Start

### Basic Usage (Auto-selects past hackathons)

```bash
python idea_generator.py https://your-new-hackathon.devpost.com
```

This will:
- Scrape rules from your new hackathon
- Automatically analyze 5 popular past hackathons
- Generate 10 tailored project ideas

### Advanced Usage (Choose specific past hackathons)

```bash
python idea_generator.py https://your-new-hackathon.devpost.com \
  --past https://treehacks-2024.devpost.com \
  --past https://hackmit-2024.devpost.com \
  --past https://pennapps-xxiv.devpost.com \
  --past https://hacktheburgh-x.devpost.com \
  --past https://calhacks-10-0.devpost.com
```

## What You Get

After running, you'll find in the output folder:

### 1. `new_hackathon_rules.json`
Complete rules, themes, and requirements from your target hackathon

### 2. `past_hackathon_winners.json`
Detailed data on winning projects from 5 past hackathons including:
- Project descriptions
- Technologies used
- Team information
- Problem statements
- Solutions

### 3. `generated_ideas.txt` ⭐
**10 innovative project ideas** with:
- **Problem Statement**: What problem it solves
- **Solution Overview**: How it works
- **Key Technologies**: Specific tech stack to use
- **Why It Wins**: Strategic analysis
- **Inspired By**: Which past winners influenced it
- **Implementation Roadmap**: Step-by-step build plan

## Example Output

```
### Idea 1: NeuroFlow - Brain-Computer Music Therapy

**Problem Statement**: Mental health support is often inaccessible and 
lacks personalization. Traditional therapy doesn't adapt in real-time to 
emotional states.

**Solution Overview**: A brain-computer interface that reads EEG signals 
to detect emotional states and generates personalized therapeutic 
soundscapes using AI...

**Key Technologies**: 
- Muse EEG headband for brainwave detection
- Python + TensorFlow for emotion classification
- Web Audio API for real-time sound generation
- React for web interface

**Why It Wins**:
- Aligns with health & wellness track
- Uses cutting-edge BCI technology
- Addresses real mental health crisis
- Feasible in 36 hours with pre-trained models

**Inspired By**: 
- "Duet: Brainwaves" (Cal Hacks) - BCI + music generation
- "MindfulAI" (TreeHacks) - Mental health + AI personalization

**Implementation Roadmap**:
1. Set up Muse SDK and capture EEG data
2. Integrate pre-trained emotion classification model
3. Build sound generation engine with Web Audio API
4. Create simple React UI for visualization
5. Test and refine with live demos
```

## Tips for Best Results

### Choose Relevant Past Hackathons
Select past hackathons that:
- Have similar themes to your target hackathon
- Are recent (last 1-2 years)
- Had high-quality winning projects
- Match your skill level/interests

### Popular Past Hackathons to Analyze
- **TreeHacks** (Stanford) - AI/ML focus
- **HackMIT** - Technical innovation
- **PennApps** - Diverse categories
- **Cal Hacks** - Large scale, varied themes
- **HackTheNorth** (Canada) - Social impact

### Customize the Ideas
The generated ideas are starting points. You should:
- Adapt them to your team's skills
- Add your unique twist
- Validate technical feasibility
- Check against hackathon rules

## Configuration

### API Key
Your Claude API key is already configured in `config_settings.py`

### Default Past Hackathons
If you don't specify `--past` URLs, the system uses these defaults:
- TreeHacks 2024
- HackMIT 2024
- PennApps XXIV
- HackTheBurgh X
- Cal Hacks 10.0

You can modify these in `idea_generator.py` → `get_default_hackathons()`

## Troubleshooting

### "Could not find projects"
Some hackathons hide project galleries. Try:
- Using a different past hackathon
- Checking if the URL is correct
- Ensuring the hackathon has ended and projects are public

### "No winning projects found"
The scraper looks for winner indicators. If none found:
- The hackathon may not mark winners clearly
- Try a different hackathon
- Check the `past_hackathon_winners.json` to see what was scraped

### Rate Limiting
If scraping multiple hackathons:
- The tool includes delays between requests
- If you hit rate limits, wait a few minutes
- Consider scraping fewer hackathons at once

## Advanced: Programmatic Usage

```python
from idea_generator import IdeaGenerator

# Create generator
generator = IdeaGenerator(
    new_hackathon_url="https://your-hackathon.devpost.com",
    past_hackathon_urls=[
        "https://treehacks-2024.devpost.com",
        "https://hackmit-2024.devpost.com",
        # ... more URLs
    ]
)

# Run the workflow
ideas = generator.run()

# Ideas are also saved to files automatically
print(f"Output in: {generator.output_dir}")
```

## What Makes This Different?

Unlike simple idea generators, this tool:
- ✅ **Learns from real winners** - Not random ideas, but proven patterns
- ✅ **Adapts to YOUR hackathon** - Respects specific rules and themes
- ✅ **Provides implementation plans** - Not just ideas, but how to build them
- ✅ **Shows inspiration sources** - Understand why each idea could win
- ✅ **Uses Claude AI** - Advanced reasoning and synthesis

## Next Steps

1. Run the generator for your target hackathon
2. Review all 10 generated ideas
3. Pick 2-3 favorites that match your skills
4. Validate technical feasibility
5. Refine and add your unique twist
6. Build and win! 🏆

---

**Pro Tip**: Run this tool BEFORE the hackathon starts to have ideas ready. Then you can hit the ground running when the event begins!
