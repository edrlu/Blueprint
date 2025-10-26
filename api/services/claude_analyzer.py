"""
Claude AI analysis module for Devpost scraper
"""

import json
import os
import time
from datetime import datetime
from typing import Dict, List, Any
import anthropic
from api.utils.data_utils import create_summary_data, create_master_data, create_readable_summary


class ClaudeAnalyzer:
    def __init__(self, scraper):
        self.scraper = scraper
        self.claude_client = None
        self.analysis_dir = os.path.join(scraper.output_dir, "ai_analysis")
        os.makedirs(self.analysis_dir, exist_ok=True)
    
    def setup_claude_api(self, api_key: str):
        """Setup Claude API with the provided API key"""
        try:
            self.claude_client = anthropic.Anthropic(api_key=api_key)
            print("[OK] Claude API configured successfully")
            return True
        except Exception as e:
            print(f"[ERROR] Error setting up Claude API: {e}")
            return False
    
    def create_analysis_package(self):
        """Create a comprehensive package optimized for AI analysis"""
        print("Creating AI analysis package...")
        
        # Create different analysis formats
        self.create_summary()
        self.create_structured_data()
        self.create_prompts()
        self.create_context_file()
        
        print(f"[OK] AI analysis package created in: {self.analysis_dir}")
        return self.analysis_dir
    
    def create_summary(self):
        """Create a comprehensive summary optimized for AI analysis"""
        summary_data = create_summary_data(
            self.scraper.scraped_data, 
            self.scraper.event_name, 
            self.scraper.devpost_url
        )
        
        # Save summary
        summary_file = os.path.join(self.analysis_dir, "event_summary.json")
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, indent=2, ensure_ascii=False)
        
        # Create human-readable summary
        summary_text = create_readable_summary(summary_data, self.scraper.event_name)
        summary_txt_file = os.path.join(self.analysis_dir, "event_summary.txt")
        with open(summary_txt_file, 'w', encoding='utf-8') as f:
            f.write(summary_text)
    
    def create_structured_data(self):
        """Create structured data files optimized for AI analysis"""
        master_data = create_master_data(
            self.scraper.scraped_data,
            self.scraper.event_name,
            self.scraper.devpost_url
        )
        
        # Save master data file
        master_file = os.path.join(self.analysis_dir, "master_data.json")
        with open(master_file, 'w', encoding='utf-8') as f:
            json.dump(master_data, f, indent=2, ensure_ascii=False)
        
        # Create individual section files for focused analysis
        for section_name, section_data in master_data["sections"].items():
            section_file = os.path.join(self.analysis_dir, f"{section_name}_analysis.json")
            with open(section_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "section": section_name,
                    "data": section_data,
                    "analysis_notes": self.get_analysis_notes(section_name)
                }, f, indent=2, ensure_ascii=False)
    
    def get_analysis_notes(self, section_name: str) -> str:
        """Get analysis notes for each section"""
        from api.config.constants import ANALYSIS_NOTES
        return ANALYSIS_NOTES.get(section_name, "This section contains event-related information that can be analyzed for insights.")
    
    def create_prompts(self):
        """Create ready-to-use prompts for AI analysis"""
        prompts = {
            "comprehensive_analysis": f"""
# Comprehensive Analysis of {self.scraper.event_name.replace('_', ' ').title()}

Please analyze the following hackathon data and provide insights on:

1. **Event Overview**: Summarize the main purpose, goals, and structure of this hackathon
2. **Project Analysis**: Analyze the winning projects, common technologies, and innovation trends
3. **Participant Insights**: What can you learn about the participants and their backgrounds?
4. **Event Success Factors**: What made this event successful based on the data?
5. **Technology Trends**: What technologies were most popular and why?
6. **Recommendations**: What recommendations would you make for future similar events?

Use the provided data files to support your analysis with specific examples and evidence.
""",
            
            "winning_projects_focus": """
# Winning Projects Deep Dive

Analyze the winning projects from this hackathon and provide:

1. **Project Categories**: What types of projects won and why?
2. **Technology Stack Analysis**: What technologies were used in winning projects?
3. **Innovation Patterns**: What innovative approaches or solutions were used?
4. **Team Composition**: What can you learn about successful teams?
5. **Problem-Solution Fit**: How well did winning projects address real problems?
6. **Lessons Learned**: What can future participants learn from these winners?

Provide specific examples from the winning projects data.
""",
            
            "trend_analysis": """
# Hackathon Trend Analysis

Based on this hackathon data, analyze:

1. **Technology Trends**: What technologies are gaining popularity in hackathons?
2. **Project Themes**: What problem domains are most popular?
3. **Event Evolution**: How are hackathons evolving based on this data?
4. **Success Patterns**: What patterns lead to successful hackathon projects?
5. **Industry Insights**: What does this tell us about current tech industry trends?
6. **Future Predictions**: What trends do you predict for future hackathons?

Support your analysis with data from the provided files.
""",
            
            "comparative_analysis": """
# Comparative Hackathon Analysis

Use this hackathon data to compare with other hackathons you know about:

1. **Scale Comparison**: How does this event compare in size and scope?
2. **Technology Differences**: How do the technologies used compare to other events?
3. **Project Quality**: How do the winning projects compare to other hackathons?
4. **Event Structure**: What's unique about this event's structure?
5. **Success Metrics**: How would you measure this event's success?
6. **Best Practices**: What best practices can be identified?

Provide specific comparisons and insights.
""",
            
            "creative_ideas": f"""
# Creative Hackathon Ideas Based on {self.scraper.event_name.replace('_', ' ').title()}

Based on the hackathon data provided, generate innovative and creative project ideas that could win future hackathons:

1. **Problem Analysis**: What problems did the winning projects solve? What gaps exist?
2. **Technology Trends**: What emerging technologies could be combined in new ways?
3. **Market Opportunities**: What real-world problems are underserved?
4. **Innovation Patterns**: What made the winning projects successful? How can we build on that?
5. **Creative Combinations**: What unexpected technology combinations could work?
6. **Future-Ready Ideas**: What ideas would be relevant in 1-2 years?

Generate 5-10 specific, actionable project ideas with:
- Clear problem statement
- Proposed solution approach
- Key technologies to use
- Why it would be innovative
- Potential impact

Make the ideas practical enough to build in a hackathon timeframe but innovative enough to stand out.
"""
        }
        
        # Save each prompt as a separate file
        for prompt_name, prompt_content in prompts.items():
            prompt_file = os.path.join(self.analysis_dir, f"prompt_{prompt_name}.txt")
            with open(prompt_file, 'w', encoding='utf-8') as f:
                f.write(prompt_content)
        
        # Create a master prompt file
        master_prompt_file = os.path.join(self.analysis_dir, "all_prompts.txt")
        with open(master_prompt_file, 'w', encoding='utf-8') as f:
            f.write("# All Analysis Prompts\n\n")
            for prompt_name, prompt_content in prompts.items():
                f.write(f"## {prompt_name.replace('_', ' ').title()}\n")
                f.write(prompt_content)
                f.write("\n\n" + "="*50 + "\n\n")
    
    def create_context_file(self):
        """Create a context file that explains how to use the data with AI"""
        context_content = f"""
# How to Use This Data with Claude AI

## Overview
This package contains scraped data from the Devpost event: {self.scraper.event_name.replace('_', ' ').title()}
URL: {self.scraper.devpost_url}

## Files Included

### Core Data Files
- `master_data.json` - Complete structured data in JSON format
- `event_summary.json` - High-level summary and statistics
- `event_summary.txt` - Human-readable summary

### Section-Specific Files
- `{{section}}_analysis.json` - Individual section data with analysis notes
- `{{section}}.json` & `{{section}}.txt` - Raw scraped data for each section

### Winning Projects (if available)
- `winning_projects/` folder with individual project details
- `all_winning_projects.json` - Combined winning projects data

### Analysis Prompts
- `prompt_comprehensive_analysis.txt` - Full event analysis
- `prompt_winning_projects_focus.txt` - Deep dive into winning projects
- `prompt_trend_analysis.txt` - Technology and trend analysis
- `prompt_comparative_analysis.txt` - Compare with other hackathons
- `prompt_creative_ideas.txt` - Generate innovative project ideas
- `all_prompts.txt` - All prompts in one file

## How to Use with Claude

### Method 1: Direct Upload
1. Upload the `master_data.json` file to Claude
2. Use one of the provided prompts
3. Ask Claude to analyze the data

### Method 2: Section-by-Section Analysis
1. Upload individual `{{section}}_analysis.json` files
2. Ask specific questions about each section
3. Combine insights for comprehensive analysis

### Method 3: Focused Analysis
1. Upload `event_summary.txt` for quick overview
2. Upload specific winning project files for detailed project analysis
3. Use targeted prompts for specific insights

## Recommended Analysis Workflow

1. **Start with Overview**: Use `event_summary.txt` to get familiar with the event
2. **Deep Dive**: Use `master_data.json` with comprehensive analysis prompt
3. **Focus Areas**: Use specific prompts for areas of interest
4. **Compare**: Use comparative analysis prompt with other hackathon data

## Data Structure Notes

- All JSON files are UTF-8 encoded
- Text content has been cleaned for AI analysis
- Links are preserved with both text and URLs
- Images include alt text and source URLs
- Tables and forms are preserved in structured format

## Tips for Better Analysis

1. **Be Specific**: Ask Claude to provide specific examples from the data
2. **Request Evidence**: Ask for quotes or data points to support conclusions
3. **Compare**: Ask Claude to compare different sections or projects
4. **Trend Analysis**: Ask about patterns and trends in the data
5. **Actionable Insights**: Request specific recommendations based on findings

## Example Queries

- "Analyze the winning projects and identify the most successful technology stacks"
- "What patterns do you see in the project descriptions that led to success?"
- "Compare the technologies used in this hackathon to industry trends"
- "What recommendations would you make for future hackathon organizers based on this data?"
- "Identify the most innovative solutions and explain why they were successful"
- "Generate 10 creative project ideas based on the trends and gaps you see in this data"

Generated on: {datetime.now().isoformat()}
"""
        
        context_file = os.path.join(self.analysis_dir, "README_AI_Usage.txt")
        with open(context_file, 'w', encoding='utf-8') as f:
            f.write(context_content)
    
    def analyze_with_claude(self, analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """Analyze the scraped data using Claude AI"""
        if not self.claude_client:
            print("[ERROR] Claude API not configured. Please call setup_claude_api() first.")
            return {}
        
        print(f"[AI] Starting Claude analysis: {analysis_type}")
        
        try:
            if analysis_type == "comprehensive":
                return self._comprehensive_claude_analysis()
            elif analysis_type == "winning_projects":
                return self._winning_projects_claude_analysis()
            elif analysis_type == "trends":
                return self._trend_analysis_claude()
            elif analysis_type == "comparative":
                return self._comparative_analysis_claude()
            elif analysis_type == "creative_ideas":
                return self._creative_ideas_analysis()
            else:
                print(f"[ERROR] Unknown analysis type: {analysis_type}")
                return {}
                
        except Exception as e:
            print(f"[ERROR] Error during Claude analysis: {e}")
            return {}
    
    def _comprehensive_claude_analysis(self) -> Dict[str, Any]:
        """Perform comprehensive analysis using Claude"""
        # Load master data
        master_data_file = os.path.join(self.analysis_dir, "master_data.json")
        if not os.path.exists(master_data_file):
            print("❌ Master data file not found")
            return {}
        
        with open(master_data_file, 'r', encoding='utf-8') as f:
            master_data = json.load(f)
        
        # Load the comprehensive analysis prompt
        prompt_file = os.path.join(self.analysis_dir, "prompt_comprehensive_analysis.txt")
        if os.path.exists(prompt_file):
            with open(prompt_file, 'r', encoding='utf-8') as f:
                prompt = f.read()
        else:
            prompt = f"""
# Comprehensive Analysis of {self.scraper.event_name.replace('_', ' ').title()}

Please analyze the following hackathon data and provide insights on:

1. **Event Overview**: Summarize the main purpose, goals, and structure of this hackathon
2. **Project Analysis**: Analyze the winning projects, common technologies, and innovation trends
3. **Participant Insights**: What can you learn about the participants and their backgrounds?
4. **Event Success Factors**: What made this event successful based on the data?
5. **Technology Trends**: What technologies were most popular and why?
6. **Recommendations**: What recommendations would you make for future similar events?

Use the provided data to support your analysis with specific examples and evidence.
"""
        
        # Prepare the data for Claude
        data_text = f"""
HACKATHON DATA FOR ANALYSIS:

Event: {master_data['metadata']['event_name']}
URL: {master_data['metadata']['url']}
Scraped: {master_data['metadata']['scraped_at']}

SECTIONS AVAILABLE: {', '.join(master_data['sections'].keys())}

DETAILED DATA:
{json.dumps(master_data, indent=2)}
"""
        
        # Send to Claude
        try:
            message = self.claude_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4096,
                messages=[
                    {
                        "role": "user",
                        "content": f"{prompt}\n\n{data_text}"
                    }
                ]
            )
            
            analysis_result = {
                "analysis_type": "comprehensive",
                "event_name": self.scraper.event_name,
                "timestamp": datetime.now().isoformat(),
                "claude_response": message.content[0].text,
                "data_sections_analyzed": list(master_data['sections'].keys())
            }
            
            # Save the analysis result
            self._save_analysis_result("comprehensive", analysis_result)
            print("[OK] Comprehensive analysis completed and saved")
            return analysis_result
            
        except Exception as e:
            print(f"[ERROR] Error calling Claude API: {e}")
            return {}
    
    def _winning_projects_claude_analysis(self) -> Dict[str, Any]:
        """Analyze winning projects specifically"""
        # Load winning projects data
        winning_projects_file = os.path.join(self.scraper.output_dir, "winning_projects", "all_winning_projects.json")
        if not os.path.exists(winning_projects_file):
            print("❌ No winning projects data found")
            return {}
        
        with open(winning_projects_file, 'r', encoding='utf-8') as f:
            winning_projects = json.load(f)
        
        prompt = """
# Winning Projects Deep Dive Analysis

Analyze the winning projects from this hackathon and provide:

1. **Project Categories**: What types of projects won and why?
2. **Technology Stack Analysis**: What technologies were used in winning projects?
3. **Innovation Patterns**: What innovative approaches or solutions were used?
4. **Team Composition**: What can you learn about successful teams?
5. **Problem-Solution Fit**: How well did winning projects address real problems?
6. **Lessons Learned**: What can future participants learn from these winners?

Provide specific examples from the winning projects data.
"""
        
        data_text = f"""
WINNING PROJECTS DATA:

{json.dumps(winning_projects, indent=2)}
"""
        
        try:
            message = self.claude_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4096,
                messages=[
                    {
                        "role": "user",
                        "content": f"{prompt}\n\n{data_text}"
                    }
                ]
            )
            
            analysis_result = {
                "analysis_type": "winning_projects",
                "event_name": self.scraper.event_name,
                "timestamp": datetime.now().isoformat(),
                "claude_response": message.content[0].text,
                "projects_analyzed": len(winning_projects)
            }
            
            # Save the analysis
            self._save_analysis_result("winning_projects", analysis_result)
            print("[OK] Winning projects analysis completed and saved")
            return analysis_result
            
        except Exception as e:
            print(f"[ERROR] Error analyzing winning projects: {e}")
            return {}
    
    def _trend_analysis_claude(self) -> Dict[str, Any]:
        """Perform trend analysis using Claude"""
        # Load summary data
        summary_file = os.path.join(self.analysis_dir, "event_summary.json")
        if not os.path.exists(summary_file):
            print("❌ Event summary not found")
            return {}
        
        with open(summary_file, 'r', encoding='utf-8') as f:
            summary_data = json.load(f)
        
        prompt = """
# Hackathon Trend Analysis

Based on this hackathon data, analyze:

1. **Technology Trends**: What technologies are gaining popularity in hackathons?
2. **Project Themes**: What problem domains are most popular?
3. **Event Evolution**: How are hackathons evolving based on this data?
4. **Success Patterns**: What patterns lead to successful hackathon projects?
5. **Industry Insights**: What does this tell us about current tech industry trends?
6. **Future Predictions**: What trends do you predict for future hackathons?

Support your analysis with data from the provided information.
"""
        
        data_text = f"""
HACKATHON SUMMARY DATA:

{json.dumps(summary_data, indent=2)}
"""
        
        try:
            message = self.claude_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4096,
                messages=[
                    {
                        "role": "user",
                        "content": f"{prompt}\n\n{data_text}"
                    }
                ]
            )
            
            analysis_result = {
                "analysis_type": "trend_analysis",
                "event_name": self.scraper.event_name,
                "timestamp": datetime.now().isoformat(),
                "claude_response": message.content[0].text
            }
            
            # Save the analysis
            self._save_analysis_result("trend_analysis", analysis_result)
            print("[OK] Trend analysis completed and saved")
            return analysis_result
            
        except Exception as e:
            print(f"[ERROR] Error in trend analysis: {e}")
            return {}
    
    def _comparative_analysis_claude(self) -> Dict[str, Any]:
        """Perform comparative analysis using Claude"""
        # Load master data for comparison
        master_data_file = os.path.join(self.analysis_dir, "master_data.json")
        if not os.path.exists(master_data_file):
            print("❌ Master data file not found")
            return {}
        
        with open(master_data_file, 'r', encoding='utf-8') as f:
            master_data = json.load(f)
        
        prompt = """
# Comparative Hackathon Analysis

Use this hackathon data to compare with other hackathons you know about:

1. **Scale Comparison**: How does this event compare in size and scope?
2. **Technology Differences**: How do the technologies used compare to other events?
3. **Project Quality**: How do the winning projects compare to other hackathons?
4. **Event Structure**: What's unique about this event's structure?
5. **Success Metrics**: How would you measure this event's success?
6. **Best Practices**: What best practices can be identified?

Provide specific comparisons and insights.
"""
        
        data_text = f"""
HACKATHON DATA FOR COMPARISON:

{json.dumps(master_data, indent=2)}
"""
        
        try:
            message = self.claude_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4096,
                messages=[
                    {
                        "role": "user",
                        "content": f"{prompt}\n\n{data_text}"
                    }
                ]
            )
            
            analysis_result = {
                "analysis_type": "comparative",
                "event_name": self.scraper.event_name,
                "timestamp": datetime.now().isoformat(),
                "claude_response": message.content[0].text
            }
            
            # Save the analysis
            self._save_analysis_result("comparative", analysis_result)
            print("[OK] Comparative analysis completed and saved")
            return analysis_result
            
        except Exception as e:
            print(f"[ERROR] Error in comparative analysis: {e}")
            return {}
    
    def _creative_ideas_analysis(self) -> Dict[str, Any]:
        """Generate creative hackathon ideas based on the data"""
        # Load master data for comprehensive analysis
        master_data_file = os.path.join(self.analysis_dir, "master_data.json")
        if not os.path.exists(master_data_file):
            print("[ERROR] Master data file not found")
            return {}
        
        with open(master_data_file, 'r', encoding='utf-8') as f:
            master_data = json.load(f)
        
        prompt = f"""
# Creative Hackathon Ideas Based on {self.scraper.event_name.replace('_', ' ').title()}

Based on the hackathon data provided, generate innovative and creative project ideas that could win future hackathons:

1. **Problem Analysis**: What problems did the winning projects solve? What gaps exist?
2. **Technology Trends**: What emerging technologies could be combined in new ways?
3. **Market Opportunities**: What real-world problems are underserved?
4. **Innovation Patterns**: What made the winning projects successful? How can we build on that?
5. **Creative Combinations**: What unexpected technology combinations could work?
6. **Future-Ready Ideas**: What ideas would be relevant in 1-2 years?

Generate 5-10 specific, actionable project ideas with:
- Clear problem statement
- Proposed solution approach
- Key technologies to use
- Why it would be innovative
- Potential impact

Make the ideas practical enough to build in a hackathon timeframe but innovative enough to stand out.
"""
        
        data_text = f"""
HACKATHON DATA FOR CREATIVE IDEAS:

Event: {master_data['metadata']['event_name']}
URL: {master_data['metadata']['url']}
Scraped: {master_data['metadata']['scraped_at']}

SECTIONS AVAILABLE: {', '.join(master_data['sections'].keys())}

DETAILED DATA:
{json.dumps(master_data, indent=2)}
"""
        
        try:
            message = self.claude_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4096,
                messages=[
                    {
                        "role": "user",
                        "content": f"{prompt}\n\n{data_text}"
                    }
                ]
            )
            
            analysis_result = {
                "analysis_type": "creative_ideas",
                "event_name": self.scraper.event_name,
                "timestamp": datetime.now().isoformat(),
                "claude_response": message.content[0].text
            }
            
            # Save the analysis
            self._save_analysis_result("creative_ideas", analysis_result)
            print("[OK] Creative ideas analysis completed and saved")
            return analysis_result
            
        except Exception as e:
            print(f"[ERROR] Error in creative ideas analysis: {e}")
            return {}
    
    def _save_analysis_result(self, analysis_type: str, analysis_result: Dict[str, Any]):
        """Save analysis result to files"""
        # Save as JSON
        analysis_file = os.path.join(self.analysis_dir, f"claude_{analysis_type}_analysis.json")
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_result, f, indent=2, ensure_ascii=False)
        
        # Save as readable text
        analysis_txt_file = os.path.join(self.analysis_dir, f"claude_{analysis_type}_analysis.txt")
        with open(analysis_txt_file, 'w', encoding='utf-8') as f:
            f.write(f"# Claude AI Analysis - {analysis_type.replace('_', ' ').title()}\n")
            f.write(f"Event: {self.scraper.event_name.replace('_', ' ').title()}\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n\n")
            f.write("="*50 + "\n\n")
            f.write(analysis_result['claude_response'])
    
    def run_all_claude_analyses(self) -> Dict[str, Any]:
        """Run all available Claude analyses"""
        if not self.claude_client:
            print("[ERROR] Claude API not configured. Please call setup_claude_api() first.")
            return {}
        
        print("[AI] Running all Claude analyses...")
        
        all_results = {}
        analyses = ["comprehensive", "winning_projects", "trends", "comparative", "creative_ideas"]
        
        for analysis_type in analyses:
            print(f"\n[ANALYSIS] Running {analysis_type} analysis...")
            result = self.analyze_with_claude(analysis_type)
            if result:
                all_results[analysis_type] = result
                time.sleep(2)  # Be respectful to the API
        
        # Save combined results
        if all_results:
            combined_file = os.path.join(self.analysis_dir, "all_claude_analyses.json")
            with open(combined_file, 'w', encoding='utf-8') as f:
                json.dump(all_results, f, indent=2, ensure_ascii=False)
            
            print(f"\n[SUCCESS] All analyses completed! Results saved to: {combined_file}")
        
        return all_results
