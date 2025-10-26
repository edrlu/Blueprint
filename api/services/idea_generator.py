"""
Intelligent Idea Generator
Analyzes past hackathon winners and generates ideas for new hackathons
"""

import json
import os
import shutil
from datetime import datetime
from typing import Dict, List, Any
from api.services.devpost_scraper import DevpostScraper
from api.services.claude_analyzer import ClaudeAnalyzer
from api.config.settings import CLAUDE_API_KEY
import anthropic


class IdeaGenerator:
    def __init__(self, new_hackathon_url: str, past_hackathon_urls: List[str] = None):
        """
        Initialize the idea generator
        
        Args:
            new_hackathon_url: URL of the hackathon you want to participate in
            past_hackathon_urls: List of past hackathon URLs to learn from (optional)
        """
        # Clean URLs - remove query parameters
        self.new_hackathon_url = new_hackathon_url.split('?')[0]
        self.past_hackathon_urls = [url.split('?')[0] for url in (past_hackathon_urls or [])]
        self.claude_client = None

        # Extract hackathon name for folder structure
        self.hackathon_name = self._extract_hackathon_name(new_hackathon_url)

        # Create hackathon-data directory structure
        self.base_data_dir = "hackathon-data"
        os.makedirs(self.base_data_dir, exist_ok=True)

        self.output_dir = os.path.join(self.base_data_dir, self.hackathon_name)

        # Check if rules data exists (NOT ideas.txt - that's always regenerated)
        self.rules_cached = os.path.exists(self.output_dir) and os.path.exists(
            os.path.join(self.output_dir, "rules.json")
        )
        
    def _extract_hackathon_name(self, url: str) -> str:
        """Extract clean hackathon name from URL"""
        try:
            # Remove protocol and www
            url_clean = url.replace('https://', '').replace('http://', '').replace('www.', '')

            # Extract the subdomain or path
            if '.devpost.com' in url_clean:
                # Format: event-name.devpost.com
                event_part = url_clean.split('.devpost.com')[0]
                if '/' in event_part:
                    event_part = event_part.split('/')[0]
                return event_part.replace('-', '_').replace('.', '_')
            else:
                return "hackathon"
        except Exception as e:
            print(f"Warning: Could not extract hackathon name: {e}")
            return "hackathon"

    def load_cached_rules(self) -> Dict[str, Any]:
        """Load cached rules if they exist"""
        if not self.rules_cached:
            return None

        print(f"📦 Loading cached rules: {self.hackathon_name}")

        try:
            rules_file = os.path.join(self.output_dir, "rules.json")
            with open(rules_file, 'r', encoding='utf-8') as f:
                rules_data = json.load(f)
            print(f"✓ Rules loaded from cache\n")
            return rules_data
        except Exception as e:
            print(f"✗ Error loading cached rules: {e}\n")
            return None

    def load_cached_hackathon_projects(self, hackathon_url: str) -> List[Dict[str, Any]]:
        """Load cached projects for a specific hackathon"""
        hackathon_name = self._extract_hackathon_name(hackathon_url)
        hackathon_dir = os.path.join(self.base_data_dir, hackathon_name)

        if not os.path.exists(hackathon_dir):
            return None

        print(f"📦 Loading cached projects: {hackathon_name}")

        try:
            projects = []
            for filename in os.listdir(hackathon_dir):
                if filename.startswith('project_') and filename.endswith('.json'):
                    filepath = os.path.join(hackathon_dir, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        projects.append(json.load(f))

            if projects:
                print(f"✓ Loaded {len(projects)} cached projects\n")
                return projects
            else:
                print(f"✗ No projects found in cache\n")
                return None

        except Exception as e:
            print(f"✗ Error loading cached projects: {e}\n")
            return None

    def setup_claude(self, api_key: str = None):
        """Setup Claude API"""
        api_key = api_key or CLAUDE_API_KEY
        if not api_key:
            print("✗ No Claude API key")
            return False
        
        try:
            self.claude_client = anthropic.Anthropic(api_key=api_key)
            print("✓ Claude API configured")
            return True
        except Exception as e:
            print(f"✗ Claude setup error: {e}")
            return False
    
    def scrape_new_hackathon_rules(self) -> Dict[str, Any]:
        """Scrape only rules and requirements from the new hackathon"""
        # Check cache first
        cached_rules = self.load_cached_rules()
        if cached_rules:
            return cached_rules

        print(f"\n{'='*60}")
        print(f"📋 Scraping new hackathon rules")
        print(f"{'='*60}")
        print(f"URL: {self.new_hackathon_url}")

        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)

        scraper = DevpostScraper(self.new_hackathon_url)

        # Detect available tabs first
        scraper.detect_available_tabs()

        # Only scrape relevant tabs for rules
        tabs_to_scrape = ['overview', 'rules', 'prizes', 'schedule']
        rules_data = {}

        for tab_name in tabs_to_scrape:
            tab_path = scraper.tabs.get(tab_name, f'/{tab_name}')
            tab_url = scraper.base_url + tab_path
            soup = scraper.get_page_content(tab_url)

            if soup and scraper.is_valid_page(soup):
                rules_data[tab_name] = {
                    'text': scraper.extract_text_content(soup),
                    'structured': scraper.extract_structured_data(soup, tab_name)
                }
                print(f"  ✓ {tab_name}")
            else:
                print(f"  ✗ {tab_name}")

        # Save rules data to rules.json
        rules_file = os.path.join(self.output_dir, "rules.json")
        full_rules_data = {
            'url': self.new_hackathon_url,
            'event_name': scraper.event_name,
            'scraped_at': datetime.now().isoformat(),
            'rules_data': rules_data
        }
        with open(rules_file, 'w', encoding='utf-8') as f:
            json.dump(full_rules_data, f, indent=2, ensure_ascii=False)

        print(f"✓ Saved to: {self.output_dir}/\n")
        return full_rules_data
    
    def scrape_past_hackathon_winners(self, hackathon_url: str) -> List[Dict[str, Any]]:
        """Scrape winning projects from a past hackathon - saves each as individual JSON"""
        # Check cache first
        cached_projects = self.load_cached_hackathon_projects(hackathon_url)
        if cached_projects:
            return cached_projects

        print(f"🔍 Scraping: {hackathon_url}")

        scraper = DevpostScraper(hackathon_url)
        past_hackathon_name = self._extract_hackathon_name(hackathon_url)
        hackathon_folder = os.path.join(self.base_data_dir, past_hackathon_name)
        os.makedirs(hackathon_folder, exist_ok=True)

        # Try project-gallery first, then submissions
        urls_to_try = [
            hackathon_url + '/project-gallery',
            hackathon_url + '/submissions',
            hackathon_url + '/projects'
        ]
        
        projects_data = None
        for url in urls_to_try:
            soup = scraper.get_page_content(url)
            if soup and scraper.is_valid_page(soup):
                projects_data = scraper.extract_projects_data(soup)
                if projects_data and (projects_data['all_projects'] or projects_data['project_links']):
                    break

        if not projects_data:
            print(f"  ✗ No projects found")
            # Delete empty folder
            if os.path.exists(hackathon_folder) and not os.listdir(hackathon_folder):
                shutil.rmtree(hackathon_folder)
                print(f"  🗑️  Deleted empty folder: {past_hackathon_name}")
            return []

        # Get winning projects
        winning_projects = projects_data.get('winning_projects', [])

        # Scrape and save each project individually (INCREASED TO 25)
        detailed_winners = []
        for i, project in enumerate(winning_projects[:25], 1):  # Limit to 25 winners
            project_data = scraper.scrape_individual_project(project['url'], project['title'])
            if project_data:
                detailed_winners.append(project_data)

                # Save each project as individual JSON file
                safe_title = "".join(c for c in project['title'] if c.isalnum() or c in (' ', '-', '_')).strip()
                safe_title = safe_title.replace(' ', '_').replace('__', '_')[:40]
                project_filename = f"project_{i:03d}_{safe_title}.json"
                project_file = os.path.join(hackathon_folder, project_filename)

                with open(project_file, 'w', encoding='utf-8') as f:
                    json.dump(project_data, f, indent=2, ensure_ascii=False)

        # Delete folder if no winners were saved
        if not detailed_winners:
            if os.path.exists(hackathon_folder) and not os.listdir(hackathon_folder):
                shutil.rmtree(hackathon_folder)
                print(f"  🗑️  Deleted empty folder: {past_hackathon_name}")
            print(f"  ✗ {past_hackathon_name} - No winners saved\n")
        else:
            print(f"  ✓ {past_hackathon_name} - {len(detailed_winners)} winners saved\n")

        return detailed_winners
    
    def scrape_all_past_hackathons(self) -> List[Dict[str, Any]]:
        """Scrape winning projects from all past hackathons - returns flat list of projects"""
        print(f"\n{'='*60}")
        print(f"🏆 Scraping past hackathon winners")
        print(f"{'='*60}")

        all_winners = []

        for i, url in enumerate(self.past_hackathon_urls, 1):
            print(f"[{i}/{len(self.past_hackathon_urls)}] {url}")
            winners_list = self.scrape_past_hackathon_winners(url)
            if winners_list:
                all_winners.extend(winners_list)  # Flatten the list

        print(f"\n✓ Total {len(all_winners)} winners collected\n")

        return all_winners
    
    def generate_ideas_with_claude(self, rules_data: Dict[str, Any], winners_data: List[Dict[str, Any]]) -> str:
        """Use Claude to generate ideas based on rules and past winners"""
        import random

        print(f"\n{'='*60}")
        print(f"🤖 Generating ideas with Claude")
        print(f"{'='*60}")

        if not self.claude_client:
            print("✗ Claude not configured")
            return ""

        # Flatten winners_data if nested (handle both old and new structure)
        flat_winners = []
        for item in winners_data:
            if isinstance(item, dict):
                flat_winners.append(item)
            elif isinstance(item, list):
                flat_winners.extend(item)

        # RANDOMLY SAMPLE 100 projects for diversity in each generation cycle
        # This ensures each idea generation is unique and inspired by different projects
        sample_size = min(100, len(flat_winners))
        sampled_winners = random.sample(flat_winners, sample_size) if len(flat_winners) > sample_size else flat_winners

        print(f"🎲 Randomly sampled {sample_size} projects from {len(flat_winners)} total projects")

        # Summarize winners data
        winners_summary = []
        for project in sampled_winners:
            winners_summary.append({
                'name': project.get('title', project.get('name', '')),
                'tagline': project.get('tagline', ''),
                'description': project.get('description', '')[:500] if project.get('description') else '',
                'technologies': project.get('technologies', [])[:10]
            })
        
        # Summarize rules data
        rules_summary = {
            'event_name': rules_data.get('event_name', ''),
            'url': rules_data.get('url', ''),
            'overview': str(rules_data.get('rules_data', {}).get('overview', {}).get('text', ''))[:2000],
            'rules': str(rules_data.get('rules_data', {}).get('rules', {}).get('text', ''))[:2000],
            'prizes': str(rules_data.get('rules_data', {}).get('prizes', {}).get('text', ''))[:1000]
        }
        
        # Prepare the prompt - CHANGED TO GENERATE ONLY 2 IDEAS
        prompt = f"""
# Hackathon Idea Generation Task

You are an expert hackathon strategist. Your task is to generate winning project ideas for a NEW hackathon by learning from past winners.

## NEW HACKATHON RULES & REQUIREMENTS

{json.dumps(rules_summary, indent=2)}

## PAST WINNING PROJECTS (From multiple hackathons)

You have access to {len(winners_summary)} past winning projects. Here's a sample:

{json.dumps(winners_summary, indent=2)}

## YOUR TASK

Analyze the past winning projects to identify:
1. **Success Patterns**: What made these projects win?
2. **Technology Trends**: What tech stacks are popular and effective?
3. **Problem-Solution Fit**: What types of problems resonate with judges?
4. **Innovation Approaches**: How did winners innovate?
5. **Presentation Strategies**: How were winning ideas communicated?

Then, generate **7 highly innovative and diverse project ideas** for the NEW hackathon that:
- **Strictly follow** the new hackathon's rules, themes, and requirements
- **Learn from** the success patterns of past winners
- **Adapt** winning strategies to the new context
- Are **practical** to build in a hackathon timeframe
- Are **innovative** enough to stand out
- Are **DIFFERENT** from each other (explore different problem domains/approaches)

## OUTPUT FORMAT

For each idea, provide:

### Idea [Number]: [Catchy Project Name]

**Problem Statement**: Clear description of the problem being solved

**Solution Overview**: How the project addresses the problem

**Key Technologies**: Specific tech stack (inspired by past winners)

**Why It Wins**: 
- Alignment with new hackathon rules/themes
- Innovation factor (what makes it unique)
- Feasibility (can be built in time)
- Impact potential

**Inspired By**: Which past winning projects influenced this idea and how

**Implementation Roadmap**: Brief 3-5 step plan for building it

---

Generate 7 diverse, winning ideas now. Be specific, creative, and strategic. Make sure the ideas explore different problem spaces.
"""
        
        print("  Processing...")
        
        try:
            message = self.claude_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=8000,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            ideas = message.content[0].text

            # Save ideas to ideas.txt
            ideas_file = os.path.join(self.output_dir, "ideas.txt")
            with open(ideas_file, 'w', encoding='utf-8') as f:
                f.write(f"# Generated Hackathon Ideas\n")
                f.write(f"Generated: {datetime.now().isoformat()}\n")
                f.write(f"New Hackathon: {self.new_hackathon_url}\n")
                f.write(f"Based on {len(winners_summary)} projects from {len(self.past_hackathon_urls)} hackathons\n\n")
                f.write("="*60 + "\n\n")
                f.write(ideas)

            print(f"✓ Ideas generated\n")
            return ideas
            
        except Exception as e:
            print(f"✗ Error: {e}")
            return ""
    
    def run(self) -> str:
        """Run the complete idea generation workflow - ALWAYS generates fresh ideas"""
        print(f"\n{'='*60}")
        print(f"  Intelligent Hackathon Idea Generator")
        print(f"{'='*60}\n")

        # Step 1: Setup Claude
        if not self.setup_claude():
            return ""

        # Step 2: Scrape or load new hackathon rules (uses cache if available)
        rules_data = self.scrape_new_hackathon_rules()

        # Step 3: Scrape or load past hackathon winners (uses cache if available)
        if not self.past_hackathon_urls:
            print("⚠ Using default hackathons...")
            self.past_hackathon_urls = self.get_default_hackathons()

        winners_data = self.scrape_all_past_hackathons()

        # Step 4: ALWAYS generate fresh ideas with Claude (not cached)
        print(f"💡 Generating fresh ideas (always unique)...\n")
        ideas = self.generate_ideas_with_claude(rules_data, winners_data)

        print(f"{'='*60}")
        print(f"✓ Complete - Output: {self.output_dir}/")
        print(f"{'='*60}\n")

        return ideas
    
    def get_default_hackathons(self) -> List[str]:
        """Get a list of popular past hackathons to analyze"""
        return [
            # Original 5 (Adjusted Cal Hacks to a known public gallery)
            "https://cal-hacks-10-0.devpost.com", # CalHacks 10.0 (Fall 2023 - Public)
            "https://hack-mit-2023.devpost.com",
            "https://treehacks-2023.devpost.com",
            "https://pennapps-xxiii.devpost.com",
            "https://hacktheburghx.devpost.com",

            # Added Major Collegiate Hackathons (MLH) - Adjusted Fall 2024 links to older, public galleries
            "https://hackprinceton-spring-2024.devpost.com", # Replaced inaccessible Fall 2024 with public Spring 2024
            "https://hackharvard-2023.devpost.com",
            "https://hackru-spring-2024.devpost.com", # Replaced inaccessible Fall 2024 with public Spring 2024
            "https://technica-2023.devpost.com",
            "https://hacknyu-2023.devpost.com", # Replaced inaccessible 2024 with public 2023
            "https://hackrpi-2023.devpost.com",
            "https://hackwestern-x.devpost.com",
            "https://boilermake-x.devpost.com",
            # "https://tamudatathon-2023.devpost.com",

            # Added Sponsor/Themed Hackathons - Adjusted the Google 2024 link
            # "https://google-genai-hackathon-2023.devpost.com", # Replaced inaccessible 2024 with public 2023
            # "https://microsoft-ai-classroom.devpost.com",
            # "https://partyrock-generative-ai-hackathon.devpost.com",
            # "https://junction-2023.devpost.com",
            # "https://global-hack-week-ai-ml-2023.devpost.com"
        ]