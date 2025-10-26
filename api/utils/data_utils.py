"""
Data processing utilities for the Devpost scraper
"""

import re
import json
from typing import Dict, List, Any
from datetime import datetime
from api.config.constants import TECH_KEYWORDS, STOP_WORDS, ANALYSIS_NOTES


def extract_main_topics(text: str) -> List[str]:
    """Extract main topics from text content"""
    if not text:
        return []

    # Simple keyword extraction (can be enhanced with NLP libraries)
    words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
    word_freq = {}
    for word in words:
        if word not in STOP_WORDS:
            word_freq[word] = word_freq.get(word, 0) + 1

    # Return top 10 most frequent words
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, freq in sorted_words[:10]]


def analyze_technologies(winning_projects: List[Dict]) -> Dict[str, int]:
    """Analyze common technologies in winning projects"""
    tech_count = {}

    for project in winning_projects:
        # Extract from project titles and descriptions
        project_text = f"{project.get('title', '')} {project.get('description', '')}".lower()

        for tech in TECH_KEYWORDS:
            if tech in project_text:
                tech_count[tech] = tech_count.get(tech, 0) + 1

    return dict(sorted(tech_count.items(), key=lambda x: x[1], reverse=True))


def clean_text_for_ai(text: str) -> str:
    """Clean and format text for optimal AI analysis"""
    if not text:
        return ""

    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)

    # Remove common web artifacts
    text = re.sub(r'Skip to main content', '', text, flags=re.IGNORECASE)
    text = re.sub(r'Cookie policy', '', text, flags=re.IGNORECASE)
    text = re.sub(r'Privacy policy', '', text, flags=re.IGNORECASE)

    # Clean up the text
    text = text.strip()

    return text


def get_analysis_notes(section_name: str) -> str:
    """Get analysis notes for each section"""
    return ANALYSIS_NOTES.get(section_name, "This section contains event-related information that can be analyzed for insights.")


def create_readable_summary(summary_data: Dict, event_name: str) -> str:
    """Create a human-readable summary for Gemini"""
    summary = f"""
# {event_name.replace('_', ' ').title()} - Event Analysis Summary

## Event Overview
- **Event Name**: {event_name.replace('_', ' ').title()}
- **URL**: {summary_data['event_overview']['url']}
- **Scraped Date**: {summary_data['event_overview']['scraped_date']}
- **Total Sections**: {summary_data['event_overview']['total_tabs']}
- **Available Sections**: {', '.join(summary_data['event_overview']['available_sections'])}

## Content Summary by Section
"""

    for section, data in summary_data['content_summary'].items():
        summary += f"""
### {section.title()}
- **Title**: {data['title']}
- **Headings**: {data['headings_count']} headings found
- **Links**: {data['links_count']} links found
- **Content Length**: {data['text_length']} characters
- **Key Headings**: {', '.join(data['key_headings'][:3])}
- **Main Topics**: {', '.join(data['main_topics'][:5])}
"""

    if summary_data['winning_projects_analysis']:
        wp = summary_data['winning_projects_analysis']
        summary += f"""
## Winning Projects Analysis
- **Total Projects**: {wp['total_projects']}
- **Winning Projects**: {wp['winning_projects_count']}
- **Winning Project Titles**: {', '.join(wp['winning_project_titles'][:5])}
- **Common Technologies**: {', '.join(list(wp['common_technologies'].keys())[:5])}
"""

    return summary


def create_summary_data(scraped_data: Dict, event_name: str, devpost_url: str) -> Dict[str, Any]:
    """Create comprehensive summary data for analysis"""
    summary_data = {
        "event_overview": {
            "name": event_name,
            "url": devpost_url,
            "scraped_date": datetime.now().isoformat(),
            "total_tabs": len(scraped_data),
            "available_sections": list(scraped_data.keys())
        },
        "content_summary": {},
        "key_insights": {},
        "winning_projects_analysis": {}
    }

    # Analyze each tab
    for tab_name, tab_data in scraped_data.items():
        summary_data["content_summary"][tab_name] = {
            "title": tab_data.get('title', ''),
            "headings_count": len(tab_data.get('headings', [])),
            "links_count": len(tab_data.get('links', [])),
            "text_length": len(tab_data.get('text_content', '')),
            "key_headings": [h['text'] for h in tab_data.get('headings', [])[:5]],
            "main_topics": extract_main_topics(tab_data.get('text_content', ''))
        }

    # Special analysis for projects
    if 'projects' in scraped_data and 'projects_info' in scraped_data['projects']:
        projects_info = scraped_data['projects']['projects_info']
        summary_data["winning_projects_analysis"] = {
            "total_projects": len(projects_info.get('all_projects', [])),
            "winning_projects_count": len(projects_info.get('winning_projects', [])),
            "winning_project_titles": [p['title'] for p in projects_info.get('winning_projects', [])],
            "common_technologies": analyze_technologies(projects_info.get('winning_projects', []))
        }

    return summary_data


def create_master_data(scraped_data: Dict, event_name: str, devpost_url: str) -> Dict[str, Any]:
    """Create master data structure for AI analysis"""
    master_data = {
        "metadata": {
            "event_name": event_name,
            "url": devpost_url,
            "scraped_at": datetime.now().isoformat(),
            "data_version": "1.0"
        },
        "sections": {}
    }

    for tab_name, tab_data in scraped_data.items():
        # Clean and structure the data for AI consumption
        clean_data = {
            "title": tab_data.get('title', ''),
            "headings": [h['text'] for h in tab_data.get('headings', [])],
            "main_content": clean_text_for_ai(tab_data.get('text_content', '')),
            "links": [{"text": link['text'], "url": link['href']} for link in tab_data.get('links', [])],
            "images": [{"alt": img['alt'], "src": img['src']} for img in tab_data.get('images', [])],
            "tables": tab_data.get('tables', []),
            "forms": tab_data.get('forms', [])
        }

        # Add special handling for projects
        if tab_name == 'projects' and 'projects_info' in tab_data:
            clean_data['projects_info'] = tab_data['projects_info']

        master_data["sections"][tab_name] = clean_data

    return master_data
