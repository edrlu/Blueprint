"""
Main Devpost scraper class
"""

import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
import time
from typing import Dict, List, Any
from api.config.constants import (
    COMMON_TABS, TAB_MAPPING, WINNER_INDICATORS,
    DEFAULT_HEADERS, NAV_SELECTORS, ALTERNATIVE_TABS
)

from api.utils.data_utils import extract_main_topics, analyze_technologies


class DevpostScraper:
    def __init__(self, devpost_url):
        self.devpost_url = devpost_url.rstrip('/')
        self.base_url = self.devpost_url
        self.headers = DEFAULT_HEADERS
        self.scraped_data = {}
        self.tabs = {}
        self.event_name = ""

        # Extract event name from URL
        self.extract_event_name()

    def extract_event_name(self):
        """Extract event name from the Devpost URL"""
        try:
            # Remove protocol and www
            url_parts = self.devpost_url.replace('https://', '').replace('http://', '').replace('www.', '')
            
            # Extract the subdomain or path
            if '.devpost.com' in url_parts:
                # Format: event-name.devpost.com
                event_part = url_parts.split('.devpost.com')[0]
                if '/' in event_part:
                    event_part = event_part.split('/')[0]
                self.event_name = event_part.replace('-', '_').replace('.', '_')
            else:
                # Fallback to a generic name
                self.event_name = "devpost_event"
                
            # Clean up the name
            self.event_name = ''.join(c for c in self.event_name if c.isalnum() or c in '_-')
            if not self.event_name:
                self.event_name = "devpost_event"
                
        except Exception as e:
            print(f"Warning: Could not extract event name from URL: {e}")
            self.event_name = "devpost_event"
    
    def get_page_content(self, url):
        """Fetch page content with error handling"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)

            # Check for 403, 404, and other HTTP errors
            if response.status_code in [403, 404]:
                print(f"❌ Error fetching {url}: HTTP {response.status_code}")
                return None

            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            print(f"❌ Error fetching {url}: {e}")
            return None
    
    def is_valid_page(self, soup):
        """Check if a page is valid (not 404 or redirect)"""
        if not soup:
            return False
        
        # Check for 404 indicators
        title = soup.find('title')
        if title:
            title_text = title.get_text().lower()
            if any(indicator in title_text for indicator in ['not found', '404', 'error', 'page not found']):
                return False
        
        # Check for redirect indicators
        if soup.find('meta', {'http-equiv': 'refresh'}):
            return False
            
        # Check if page has meaningful content
        text_content = soup.get_text()
        if len(text_content.strip()) < 100:  # Too short to be meaningful
            return False
            
        return True
    
    def extract_text_content(self, soup):
        """Extract clean text content from soup"""
        if not soup:
            return ""
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text and clean it up
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def detect_available_tabs(self):
        """Auto-detect available tabs from the main page"""
        print("Detecting available tabs...")
        
        soup = self.get_page_content(self.base_url)
        if not soup:
            print("Could not load main page to detect tabs")
            return {}
        
        detected_tabs = {}
        
        # Look for navigation elements
        for selector in NAV_SELECTORS:
            nav_links = soup.select(selector)
            for link in nav_links:
                href = link.get('href', '')
                text = link.get_text().strip().lower()
                
                if href and text:
                    # Skip external links and non-tab links
                    if href.startswith('http') and 'devpost.com' not in href:
                        continue
                    if any(skip in text for skip in ['login', 'sign', 'register', 'about', 'contact', 'help']):
                        continue
                    
                    # Map common tab names
                    for tab_key, keywords in TAB_MAPPING.items():
                        if any(keyword in text for keyword in keywords):
                            # Clean up the href - only process relative URLs
                            if href.startswith('http'):
                                # Skip full URLs - they cause malformed concatenation
                                continue
                            elif href.startswith('/'):
                                clean_href = href
                            else:
                                clean_href = '/' + href
                            
                            detected_tabs[tab_key] = clean_href
                            break
        
        # Also look for common Devpost tab patterns in the URL structure
        for tab_name, tab_path in COMMON_TABS.items():
            if tab_name not in detected_tabs:  # Only test if not already detected
                # Try primary path first
                test_url = self.base_url + tab_path
                test_soup = self.get_page_content(test_url)
                if test_soup and self.is_valid_page(test_soup):
                    detected_tabs[tab_name] = tab_path
                else:
                    # Try alternative paths if primary fails
                    if tab_name in ALTERNATIVE_TABS:
                        for alt_path in ALTERNATIVE_TABS[tab_name]:
                            if alt_path != tab_path:  # Don't retry the same path
                                test_url = self.base_url + alt_path
                                test_soup = self.get_page_content(test_url)
                                if test_soup and self.is_valid_page(test_soup):
                                    detected_tabs[tab_name] = alt_path
                                    break
        
        self.tabs = detected_tabs
        print(f"Detected {len(detected_tabs)} tabs: {list(detected_tabs.keys())}")
        return detected_tabs
    
    def extract_structured_data(self, soup, tab_name):
        """Extract structured data based on tab type"""
        data = {
            'title': '',
            'headings': [],
            'links': [],
            'text_content': '',
            'images': [],
            'tables': [],
            'forms': []
        }
        
        if not soup:
            return data
        
        # Extract title
        title_tag = soup.find('title')
        if title_tag:
            data['title'] = title_tag.get_text().strip()
        
        # Extract headings
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        data['headings'] = [{'tag': h.name, 'text': h.get_text().strip()} for h in headings]
        
        # Extract links
        links = soup.find_all('a', href=True)
        data['links'] = [{'text': link.get_text().strip(), 'href': link['href']} for link in links]
        
        # Extract images
        images = soup.find_all('img')
        data['images'] = [{'src': img.get('src', ''), 'alt': img.get('alt', '')} for img in images]
        
        # Extract tables
        tables = soup.find_all('table')
        for table in tables:
            table_data = []
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                table_data.append([cell.get_text().strip() for cell in cells])
            data['tables'].append(table_data)
        
        # Extract forms
        forms = soup.find_all('form')
        for form in forms:
            form_data = {
                'action': form.get('action', ''),
                'method': form.get('method', ''),
                'inputs': []
            }
            inputs = form.find_all(['input', 'textarea', 'select'])
            for inp in inputs:
                form_data['inputs'].append({
                    'type': inp.get('type', inp.name),
                    'name': inp.get('name', ''),
                    'placeholder': inp.get('placeholder', ''),
                    'value': inp.get('value', '')
                })
            data['forms'].append(form_data)
        
        # Extract main text content
        data['text_content'] = self.extract_text_content(soup)
        
        return data
    
    def extract_projects_data(self, soup):
        """Extract project information from projects page"""
        projects_data = {
            'all_projects': [],
            'winning_projects': [],
            'project_links': []
        }
        
        if not soup:
            return projects_data
        
        # Look for project cards/containers - common patterns on Devpost
        project_containers = soup.find_all(['div', 'article'], class_=lambda x: x and any(
            keyword in x.lower() for keyword in ['project', 'submission', 'entry', 'card', 'software', 'app']
        ))
        
        # Also look for specific Devpost project selectors
        devpost_selectors = [
            '.software-entry',
            '.submission-entry', 
            '.project-card',
            '.app-card',
            '[data-software-id]',
            '.software'
        ]
        
        for selector in devpost_selectors:
            containers = soup.select(selector)
            project_containers.extend(containers)
        
        # If no specific containers found, look for links that might be projects
        if not project_containers:
            # Look for links that contain project URLs
            all_links = soup.find_all('a', href=True)
            project_links = []
            
            for link in all_links:
                href = link.get('href', '')
                text = link.get_text().strip()
                
                # Check if this looks like a project link
                if (('/software/' in href or '/projects/' in href or '/submissions/' in href) 
                    and text and len(text) > 3):
                    project_links.append({
                        'title': text,
                        'url': href if href.startswith('http') else self.base_url + href,
                        'is_winner': self.is_winning_project(link)
                    })
            
            projects_data['project_links'] = project_links
        else:
            # Extract from project containers
            for container in project_containers:
                # Find project title - try multiple selectors
                title_elem = None
                for selector in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a', '.title', '.name', '.software-name']:
                    title_elem = container.find(selector)
                    if title_elem and title_elem.get_text().strip():
                        break
                
                if title_elem:
                    title = title_elem.get_text().strip()
                    
                    # Find project link
                    link_elem = container.find('a', href=True)
                    if link_elem:
                        href = link_elem.get('href', '')
                        url = href if href.startswith('http') else self.base_url + href
                        
                        is_winner = self.is_winning_project(container)
                        
                        project_info = {
                            'title': title,
                            'url': url,
                            'is_winner': is_winner
                        }
                        
                        projects_data['all_projects'].append(project_info)
                        
                        if is_winner:
                            projects_data['winning_projects'].append(project_info)
        
        return projects_data
    
    def is_winning_project(self, element):
        """Check if a project element indicates it's a winning project"""
        if not element:
            return False
        
        # Look for winner indicators in text or classes
        text_content = element.get_text().lower()
        class_attr = ' '.join(element.get('class', [])).lower()
        
        return any(indicator in text_content or indicator in class_attr for indicator in WINNER_INDICATORS)
    
    def scrape_individual_project(self, project_url, project_title):
        """Scrape details from an individual project page"""
        print(f"  Scraping project: {project_title}")
        
        soup = self.get_page_content(project_url)
        if not soup:
            return None
        
        project_data = {
            'title': project_title,
            'url': project_url,
            'tagline': '',
            'description': '',
            'technologies': [],
            'team_members': [],
            'awards': [],
            'images': [],
            'links': [],
            'full_content': '',
            'submission_date': None
        }

        # Extract tagline first (usually near the top)
        tagline_selectors = [
            '#app-tagline',
            '.tagline',
            '.app-tagline',
            '.software-tagline',
            'meta[name="description"]',
            'meta[property="og:description"]'
        ]

        for selector in tagline_selectors:
            if selector.startswith('meta'):
                tagline_elem = soup.find('meta', attrs={'name': 'description'} if 'name=' in selector else {'property': 'og:description'})
                if tagline_elem:
                    tagline = tagline_elem.get('content', '').strip()
                    if tagline and len(tagline) > 10:
                        project_data['tagline'] = tagline
                        print(f"  ✓ Found tagline: {tagline[:50]}...")
                        break
            else:
                tagline_elem = soup.select_one(selector)
                if tagline_elem and tagline_elem.get_text().strip():
                    tagline = tagline_elem.get_text().strip()
                    if len(tagline) > 10:
                        project_data['tagline'] = tagline
                        print(f"  ✓ Found tagline: {tagline[:50]}...")
                        break

        # Extract full description (look for Devpost-specific content areas)
        desc_selectors = [
            '#app-details-left',
            '.app-details',
            '#gallery-body',
            '.project-description',
            '.description',
            '.app-content',
            '#app-details',
            'article.software-details',
            '.submission-details'
        ]

        for selector in desc_selectors:
            desc_elem = soup.select_one(selector)
            if desc_elem and desc_elem.get_text().strip():
                description = desc_elem.get_text().strip()

                # Only use if it's substantial (more than just a title)
                if len(description.split()) > 10:
                    # Limit to 300 words
                    words = description.split()
                    if len(words) > 300:
                        description = ' '.join(words[:300])
                        print(f"  ⚠️ Description truncated from {len(words)} to 300 words")

                    project_data['description'] = description
                    print(f"  ✓ Found description ({len(description.split())} words)")
                    break

        # Extract submission date from <time> tag
        time_elem = soup.find('time', class_='timeago')
        if time_elem and time_elem.get('datetime'):
            try:
                from datetime import datetime
                # Parse ISO 8601 datetime
                date_str = time_elem.get('datetime')
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                # Format as "Jun 22, 2025"
                project_data['submission_date'] = date_obj.strftime('%b %d, %Y')
                print(f"  ✓ Found submission date: {project_data['submission_date']}")
            except Exception as e:
                print(f"  ⚠️ Error parsing date: {e}")

        # Extract technologies used
        tech_elements = soup.find_all(['span', 'div'], class_=lambda x: x and any(
            keyword in x.lower() for keyword in ['tech', 'tag', 'skill', 'language']
        ))
        for tech in tech_elements:
            tech_text = tech.get_text().strip()
            if tech_text and len(tech_text) < 50:  # Reasonable tech name length
                project_data['technologies'].append(tech_text)
        
        # Extract team members
        team_elements = soup.find_all(['div', 'span'], class_=lambda x: x and any(
            keyword in x.lower() for keyword in ['team', 'member', 'author', 'creator']
        ))
        for member in team_elements:
            member_text = member.get_text().strip()
            if member_text and '@' in member_text:  # Likely an email/username
                project_data['team_members'].append(member_text)
        
        # Extract awards/prizes
        award_elements = soup.find_all(['div', 'span'], class_=lambda x: x and any(
            keyword in x.lower() for keyword in ['award', 'prize', 'winner', 'badge']
        ))
        for award in award_elements:
            award_text = award.get_text().strip()
            if award_text:
                project_data['awards'].append(award_text)
        
        # Extract images
        images = soup.find_all('img')
        for img in images:
            src = img.get('src', '')
            if src and not src.startswith('data:'):  # Skip data URLs
                project_data['images'].append({
                    'src': src if src.startswith('http') else self.base_url + src,
                    'alt': img.get('alt', '')
                })
        
        # Extract external links
        links = soup.find_all('a', href=True)
        for link in links:
            href = link.get('href', '')
            if href.startswith('http') and 'devpost.com' not in href:
                project_data['links'].append({
                    'text': link.get_text().strip(),
                    'url': href
                })
        
        # Extract full content
        project_data['full_content'] = self.extract_text_content(soup)
        
        return project_data
    
    def scrape_tab(self, tab_name, tab_path):
        """Scrape a specific tab - returns data only, no file writing"""
        url = self.base_url + tab_path
        soup = self.get_page_content(url)

        if soup:
            tab_data = self.extract_structured_data(soup, tab_name)

            if tab_name == 'projects':
                # Special handling for projects tab
                projects_data = self.extract_projects_data(soup)
                tab_data['projects_info'] = projects_data

            self.scraped_data[tab_name] = tab_data
            return True
        else:
            return False
    
    def scrape_winning_projects(self, winning_projects):
        """Scrape individual winning project pages - returns data only"""
        detailed_projects = []

        for project in winning_projects:
            project_details = self.scrape_individual_project(project['url'], project['title'])
            if project_details:
                detailed_projects.append(project_details)
            # Add delay between project scrapes
            time.sleep(2)

        return detailed_projects
    
    
    def run_scraper(self):
        """Run the complete scraping process - returns data only"""
        # Detect available tabs
        self.detect_available_tabs()

        if not self.tabs:
            return {}

        for tab_name, tab_path in self.tabs.items():
            self.scrape_tab(tab_name, tab_path)
            # Add delay to be respectful to the server
            time.sleep(1)

        return self.scraped_data
