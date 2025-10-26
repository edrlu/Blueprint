import requests
import json
from bs4 import BeautifulSoup
import re
import time
from datetime import datetime
import anthropic
import hashlib


# ========================================
# UTILITY FUNCTIONS
# ========================================

def truncate_to_word_limit(text, max_words=300):
    """
    Enforce strict word limit on any text.
    This is called EVERYWHERE to ensure no description exceeds 300 words.
    """
    if not text:
        return ""

    words = text.split()
    if len(words) > max_words:
        truncated = ' '.join(words[:max_words])
        print(f"  ⚠️ Truncated {len(words)} words → {max_words} words")
        return truncated
    return text


def generate_project_hash(description):
    """
    Generate unique hash for a project based on its description.
    Used to detect true duplicates vs similar projects.
    """
    # Normalize: lowercase, remove extra spaces, strip
    normalized = ' '.join(description.lower().split())
    return hashlib.md5(normalized.encode()).hexdigest()


# ========================================
# MAIN FRAUD DETECTOR CLASS
# ========================================

class HackathonFraudDetector:
    def __init__(self, claude_api_key, exclude_url=None):
        self.github_api = "https://api.github.com/search/repositories"
        self.devpost_base = "https://devpost.com"
        self.client = anthropic.Anthropic(api_key=claude_api_key)
        self.model_name = "claude-sonnet-4-20250514"

        # Track searches to prevent duplicates across runs
        self.search_cache = {}
        self.processed_projects = set()  # Track by hash

        # Normalize the URL to exclude (submitted project)
        self.exclude_url = self._normalize_url(exclude_url) if exclude_url else None

    def _normalize_url(self, url):
        """Normalize URL for comparison by removing query params, fragments, trailing slashes"""
        if not url:
            return None
        # Remove query parameters and fragments
        clean_url = url.split('?')[0].split('#')[0]
        # Remove trailing slash and convert to lowercase
        return clean_url.rstrip('/').lower().strip()

    def generate_search_strategies(self, description):
        """
        Generate UNIQUE, project-specific search strategies using Claude.
        Uses full description context to create targeted queries.
        """
        print("🤖 Generating project-specific search strategies...")

        # Truncate input description first
        description = truncate_to_word_limit(description, 300)

        prompt = f"""You are an expert at generating SIMPLE search queries to find similar projects on Devpost and GitHub.

TARGET PROJECT DESCRIPTION:
{description}

Your task: Generate 8-10 SIMPLE, BROAD queries that will return MANY results on Devpost/GitHub.

CRITICAL RULES - READ CAREFULLY:
1. Keep queries SHORT: 1-3 words maximum (not 2-5, not 4-6, just 1-3 words!)
2. Be BROAD, not specific - we want to find MORE projects, not fewer
3. Use SIMPLE, COMMON words that appear everywhere
4. Think like a regular person searching, not a technical expert
5. NO technical jargon, NO framework names, NO specific technologies
6. Focus on PROBLEM/GOAL, not implementation

Generate queries in these categories:

GOAL/IMPACT (3 queries) - What problem is solved?:
- 1-2 words about the core problem (e.g., "fact check", "mood tracker", "wildlife protect")
- Simple impact/benefit (e.g., "mental health", "animal safety", "news verify")
- End goal (e.g., "reduce misinformation", "track emotions")

CATEGORY (3 queries) - What type of project?:
- Simple category (e.g., "fact checker", "mood app", "wildlife camera")
- Problem domain (e.g., "misinformation", "mental health", "conservation")

TECHNOLOGY (2-3 queries) - Only if very general:
- Only super common tech (e.g., "AI detector", "browser extension", "mobile app")
- NO specific frameworks (NO "React", NO "Svelte", NO "WXT")

OUTPUT FORMAT (JSON only):
{{
  "goal_impact": [
    {{"query": "1-3 words", "reason": "simple goal"}},
    ...
  ],
  "category": [
    {{"query": "1-3 words", "reason": "broad category"}},
    ...
  ],
  "technology": [
    {{"query": "1-3 words", "reason": "general tech"}},
    ...
  ]
}}

GOOD EXAMPLES (SIMPLE & BROAD):
For a fact-checking browser extension:
✓ PERFECT: "fact check", "fake news", "misinformation", "news verify", "AI fact", "browser extension"
✗ BAD: "real-time browser extension fact-checking", "AI agent fleet deployment", "primary source citation"

For wildlife detection camera:
✓ PERFECT: "wildlife", "animal detection", "conservation", "endangered species", "camera trap"
✗ BAD: "YOLOv8 edge deployment", "camera trap system deployment"

For mood tracker:
✓ PERFECT: "mood tracker", "mental health", "emotion log", "wellbeing app"
✗ BAD: "sentiment-aware therapeutic dialogue", "longitudinal pattern recognition"

REMEMBER: Each query should be just 1-3 SIMPLE words. We want to cast a WIDE net and find LOTS of projects!

Generate queries now:"""

        try:
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )

            result_text = response.content[0].text.strip()

            # Clean up markdown and extract JSON
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()

            # Remove any leading/trailing whitespace and control characters
            result_text = result_text.strip()

            # Detect if Claude refused to generate JSON (responds with explanation)
            if not result_text or result_text[0] not in ['{', '[']:
                # Claude responded with plain text instead of JSON
                print(f"⚠️ Claude responded with explanation instead of JSON")
                print(f"⚠️ Response: {result_text[:300]}...")

                # Check if it's an error about invalid input
                if any(phrase in result_text.lower() for phrase in ['cannot analyze', 'missing', 'invalid', 'not provided', 'not a specific project']):
                    raise Exception(f"Invalid project description - Claude could not process it. Description may be too short, generic, or missing.")
                else:
                    raise Exception(f"Claude returned text instead of JSON: {result_text[:200]}")

            # Try to parse JSON with better error handling
            try:
                strategies = json.loads(result_text)
            except json.JSONDecodeError as e:
                print(f"⚠️ JSON parsing error at position {e.pos}: {e.msg}")
                print(f"⚠️ Problematic text: {result_text[:200]}...")

                # Try to find JSON object in the text
                import re
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    try:
                        strategies = json.loads(json_match.group(0))
                        print("✓ Recovered JSON from text")
                    except:
                        raise Exception(f"Could not parse JSON response: {e}")
                else:
                    raise Exception(f"No valid JSON found in response: {e}")

            # Flatten all categories (updated category names)
            all_queries = []
            for category in ['goal_impact', 'category', 'technology']:
                if category in strategies:
                    all_queries.extend(strategies[category])

            print(f"✓ Generated {len(all_queries)} unique search strategies:")
            for i, q in enumerate(all_queries[:5], 1):  # Show first 5
                print(f"  {i}. '{q['query']}'")

            if len(all_queries) > 5:
                print(f"  ... and {len(all_queries) - 5} more")

            return all_queries

        except Exception as e:
            print(f"⚠️ AI generation error: {e}")
            import traceback
            traceback.print_exc()

            # Intelligent fallback: extract key phrases
            words = description.split()
            fallback_queries = []

            # Try to extract meaningful phrases (3-5 words)
            if len(words) >= 5:
                fallback_queries.append({
                    "query": ' '.join(words[:5]),
                    "reason": "First key phrase from description"
                })
            if len(words) >= 10:
                fallback_queries.append({
                    "query": ' '.join(words[5:10]),
                    "reason": "Second key phrase from description"
                })

            return fallback_queries if fallback_queries else [
                {"query": description[:50], "reason": "Fallback - first 50 chars"}
            ]

    def search_github(self, query_obj, max_results=10):
        """Search GitHub with strict word limits on descriptions"""
        query = query_obj['query']

        # Check cache to avoid duplicate searches
        cache_key = f"github:{query}"
        if cache_key in self.search_cache:
            print(f"\n🔍 GitHub: '{query}' (CACHED)")
            return self.search_cache[cache_key]

        print(f"\n🔍 GitHub: '{query}'")

        try:
            params = {
                'q': query,
                'sort': 'stars',
                'order': 'desc',
                'per_page': max_results
            }
            headers = {
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': 'Mozilla/5.0'
            }

            response = requests.get(self.github_api, params=params, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                results = []

                print(f"  📦 GitHub returned {len(data.get('items', []))} items")

                for repo in data.get('items', [])[:max_results]:
                    # Check if this is the excluded URL (submitted project)
                    repo_url = repo['html_url']
                    normalized_repo_url = self._normalize_url(repo_url)

                    if self.exclude_url and normalized_repo_url == self.exclude_url:
                        print(f"  ⏭️ Skipping submitted project: {repo['name']} (URL: {normalized_repo_url})")
                        continue

                    # ENFORCE 300 WORD LIMIT ON DESCRIPTION
                    raw_description = repo.get('description', 'No description')
                    limited_description = truncate_to_word_limit(raw_description, 300)

                    # Generate hash to detect exact duplicates
                    proj_hash = generate_project_hash(limited_description)

                    # Skip if we've seen this exact project before
                    if proj_hash in self.processed_projects:
                        print(f"  ⏭️ Skipping duplicate: {repo['name']}")
                        continue

                    self.processed_projects.add(proj_hash)

                    results.append({
                        'platform': 'GitHub',
                        'name': repo['name'],
                        'full_name': repo['full_name'],
                        'description': limited_description,  # TRUNCATED
                        'url': repo['html_url'],
                        'stars': repo['stargazers_count'],
                        'language': repo.get('language', 'Unknown'),
                        'created_at': repo.get('created_at', ''),
                        'updated_at': repo.get('updated_at', ''),
                        'search_query': query,
                        'hash': proj_hash
                    })

                print(f"  ✓ Found {len(results)} repositories (after deduplication and exclusion)")
                if self.exclude_url:
                    print(f"  🔒 Excluded URL: {self.exclude_url}")

                # Cache results
                self.search_cache[cache_key] = results
                return results
            else:
                print(f"  ⚠️ Status: {response.status_code}")
                return []

        except Exception as e:
            print(f"  ⚠️ Error: {e}")
            return []

    def _fetch_project_date(self, project_url):
        """Fetch submission date from individual Devpost project page"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            }

            response = requests.get(project_url, headers=headers, timeout=10)
            if response.status_code != 200:
                return None

            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find the time element
            time_elem = soup.find('time', class_='timeago')
            if time_elem and time_elem.get('datetime'):
                from datetime import datetime
                date_str = time_elem.get('datetime')
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                return date_obj.strftime('%b %d, %Y')
        except Exception as e:
            # Silently fail - dates are nice to have but not critical
            pass
        return None

    def search_devpost(self, query_obj, max_pages=3):
        """Search Devpost with strict word limits on descriptions"""
        query = query_obj['query']

        # Check cache
        cache_key = f"devpost:{query}"
        if cache_key in self.search_cache:
            print(f"\n🔍 Devpost: '{query}' (CACHED)")
            return self.search_cache[cache_key]

        print(f"\n🔍 Devpost: '{query}'")

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

        results = []
        seen_urls = set()

        for page in range(1, max_pages + 1):
            try:
                search_url = f"{self.devpost_base}/software/search"
                params = {'page': page, 'query': query}

                response = requests.get(search_url, params=params, headers=headers, timeout=15)

                if response.status_code != 200:
                    print(f"  ⚠️ Page {page} status: {response.status_code}")
                    break

                soup = BeautifulSoup(response.content, 'html.parser')
                project_links = soup.find_all('a', class_='block-wrapper-link')

                if not project_links:
                    break

                print(f"  📦 Devpost page {page} returned {len(project_links)} project links")

                page_results = 0
                for link in project_links:
                    try:
                        project_url = link.get('href', '')
                        if not project_url.startswith('http'):
                            project_url = self.devpost_base + project_url

                        # Check if this is the excluded URL (submitted project)
                        normalized_project_url = self._normalize_url(project_url)

                        if self.exclude_url and normalized_project_url == self.exclude_url:
                            print(f"  ⏭️ Skipping submitted project (URL: {normalized_project_url})")
                            continue

                        if project_url in seen_urls:
                            continue
                        seen_urls.add(project_url)

                        entry = link.find('div', class_='software-entry')
                        if not entry:
                            continue

                        name_elem = entry.find('h5')
                        name = name_elem.get_text(strip=True) if name_elem else 'Unknown'

                        tagline_elem = entry.find('p', class_='tagline')
                        raw_description = tagline_elem.get_text(strip=True) if tagline_elem else 'No description'

                        # ENFORCE 300 WORD LIMIT
                        limited_description = truncate_to_word_limit(raw_description, 300)

                        # Generate hash
                        proj_hash = generate_project_hash(limited_description)

                        # Skip duplicates
                        if proj_hash in self.processed_projects:
                            print(f"  ⏭️ Skipping duplicate: {name}")
                            continue

                        self.processed_projects.add(proj_hash)

                        winner_badge = entry.find('aside', class_='entry-badge')
                        is_winner = bool(winner_badge and 'winner' in winner_badge.get_text().lower())

                        likes = self._extract_number(entry.find('span', class_='like-count'))
                        comments = self._extract_number(entry.find('span', class_='comment-count'))

                        # Fetch submission date from the individual project page for ALL projects
                        submission_date = self._fetch_project_date(project_url)
                        if submission_date:
                            print(f"    📅 {submission_date}")

                        results.append({
                            'platform': 'Devpost',
                            'name': name,
                            'description': limited_description,  # TRUNCATED
                            'url': project_url,
                            'likes': likes,
                            'comments': comments,
                            'is_winner': is_winner,
                            'search_query': query,
                            'hash': proj_hash,
                            'submission_date': submission_date
                        })
                        page_results += 1

                    except Exception as e:
                        continue

                print(f"  Page {page}: {page_results} projects")
                time.sleep(2)  # Rate limiting

            except Exception as e:
                print(f"  ⚠️ Page {page} error: {e}")
                break

        print(f"  ✓ Total: {len(results)} unique projects (after deduplication and exclusion)")
        if self.exclude_url:
            print(f"  🔒 Excluded URL: {self.exclude_url}")

        # Cache results
        self.search_cache[cache_key] = results
        return results

    def _extract_number(self, element):
        """Extract number from element text"""
        if not element:
            return 0
        text = element.get_text(strip=True)
        match = re.search(r'(\d+)', text)
        return int(match.group(1)) if match else 0

    def ai_analyze_similarity(self, original_description, similar_projects):
        """Use AI with semantic analysis to detect true similarity vs keyword overlap"""
        print("\n🤖 AI performing semantic similarity analysis...")

        # ENFORCE 300 WORD LIMIT ON INPUT
        original_description = truncate_to_word_limit(original_description, 300)

        # Analyze top 20 projects
        top_projects = similar_projects[:20]

        # Validate all project descriptions are under limit
        for proj in top_projects:
            proj['description'] = truncate_to_word_limit(proj['description'], 300)

        projects_text = ""
        for i, proj in enumerate(top_projects, 1):
            projects_text += f"\n{i}. [{proj['platform']}] {proj['name']}\n"
            projects_text += f"   Desc: {proj['description']}\n"
            if proj['platform'] == 'GitHub':
                projects_text += f"   Stars: {proj['stars']}, Lang: {proj['language']}, Created: {proj.get('created_at', 'N/A')}\n"
            else:
                projects_text += f"   Likes: {proj['likes']}, Winner: {proj.get('is_winner', False)}\n"

        prompt = f"""Expert in plagiarism detection and semantic similarity analysis. Analyze CORE INNOVATION, not just keywords.

SUBMITTED PROJECT:
{original_description}

CANDIDATE PROJECTS:
{projects_text}

CRITICAL: Avoid false positives from keyword overlap. Focus on SEMANTIC SIMILARITY of the core innovation.

For EACH project, analyze these dimensions independently:

1. PROBLEM BEING SOLVED (weight: 35%)
   - What specific pain point/problem does each project address?
   - Are they solving the SAME problem or different problems?
   - Score: 0 (completely different problem) to 100 (identical problem)

2. SOLUTION APPROACH (weight: 40%)
   - What is the CORE INNOVATION/unique approach?
   - How is the solution architected/designed?
   - Is it the same creative approach or different methodology?
   - Score: 0 (completely different solution) to 100 (identical approach)

3. IMPLEMENTATION SPECIFICS (weight: 15%)
   - Tech stack (but NOTE: React+Node is common, not suspicious alone)
   - Unique technical decisions that show copying vs coincidence
   - Score: 0 (different tech) to 100 (identical stack + architecture)

4. TARGET USE CASE (weight: 10%)
   - Who uses it and how specifically?
   - Same narrow niche or broad category?
   - Score: 0 (different audience/use) to 100 (identical niche)

FINAL SIMILARITY SCORE:
Calculate weighted average. Then apply corrections:
- If project >2 years old: reduce score by 15 points (common ideas evolve)
- If project in saturated domain (chatbots, todo apps): reduce by 10 points
- If PROBLEM is same but SOLUTION is different: max score = 45
- If keywords match but problem/solution differ: max score = 30

FRAUD RISK RULES (strict):
- HIGH: At least 2 projects with score >80 AND same problem+solution
- MEDIUM: At least 1 project >75, OR 3+ projects >60 with same problem
- LOW: All else

OUTPUT for each project:
- problem_score (0-100)
- solution_score (0-100)
- implementation_score (0-100)
- use_case_score (0-100)
- final_similarity (weighted, corrected)
- reasoning: "Problem: [same/diff]. Solution: [same/diff]. Why score is X."

JSON:
{{
  "project_scores": [
    {{
      "name": "...",
      "similarity": 0-100,
      "problem_score": 0-100,
      "solution_score": 0-100,
      "implementation_score": 0-100,
      "use_case_score": 0-100,
      "reasoning": "detailed analysis"
    }},
    ...
  ],
  "fraud_risk": "HIGH/MEDIUM/LOW",
  "red_flags": ["specific concern"],
  "originality_score": 0-100,
  "summary": "verdict with evidence",
  "recommendation": "action"
}}"""

        try:
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=8000,
                messages=[{"role": "user", "content": prompt}]
            )

            result_text = response.content[0].text.strip()

            # Clean up markdown and extract JSON
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()

            # Remove any leading/trailing whitespace
            result_text = result_text.strip()

            # Detect if Claude refused to generate JSON (responds with explanation)
            if not result_text or result_text[0] not in ['{', '[']:
                # Claude responded with plain text instead of JSON
                print(f"⚠️ Claude responded with explanation instead of JSON for AI analysis")
                print(f"⚠️ Response: {result_text[:300]}...")

                # Check if it's an error about invalid input
                if any(phrase in result_text.lower() for phrase in ['cannot analyze', 'missing', 'invalid', 'not provided', 'description is missing']):
                    raise Exception(f"Invalid project description for AI analysis - Claude could not process it. Description may be too short, generic, or missing.")
                else:
                    raise Exception(f"Claude returned text instead of JSON: {result_text[:200]}")

            # Try to parse JSON with better error handling
            try:
                analysis = json.loads(result_text)
            except json.JSONDecodeError as e:
                print(f"⚠️ AI analysis JSON parsing error at position {e.pos}: {e.msg}")
                print(f"⚠️ Problematic text: {result_text[:200]}...")

                # Try to find JSON object in the text
                import re
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    try:
                        analysis = json.loads(json_match.group(0))
                        print("✓ Recovered JSON from text")
                    except:
                        raise Exception(f"Could not parse AI analysis JSON: {e}")
                else:
                    raise Exception(f"No valid JSON found in AI response: {e}")

            # Merge AI scores with project data
            for i, proj in enumerate(top_projects):
                if i < len(analysis['project_scores']):
                    proj['ai_similarity'] = analysis['project_scores'][i]['similarity']
                    proj['ai_reasoning'] = analysis['project_scores'][i]['reasoning']
                else:
                    proj['ai_similarity'] = 0
                    proj['ai_reasoning'] = "Not analyzed"

            return analysis

        except Exception as e:
            print(f"⚠️ AI analysis error: {e}")
            import traceback
            traceback.print_exc()
            return {
                "project_scores": [],
                "fraud_risk": "UNKNOWN",
                "red_flags": [],
                "originality_score": 50,
                "summary": "AI analysis failed",
                "recommendation": "Manual review required"
            }

    def save_detailed_report(self, project_name, description, all_projects, ai_analysis, filename):
        """Save comprehensive fraud detection report"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("="*100 + "\n")
            f.write("HACKATHON FRAUD DETECTION REPORT\n")
            f.write("="*100 + "\n\n")

            f.write(f"Project Name: {project_name}\n")
            f.write(f"Description: {description}\n")
            f.write(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("="*100 + "\n")
            f.write("AI FRAUD ASSESSMENT\n")
            f.write("="*100 + "\n")
            f.write(f"Fraud Risk: {ai_analysis.get('fraud_risk', 'UNKNOWN')}\n")
            f.write(f"Originality Score: {ai_analysis.get('originality_score', 0)}/100\n\n")

            f.write("Summary:\n")
            f.write(ai_analysis.get('summary', 'No summary available') + "\n\n")

            f.write("Recommendation:\n")
            f.write(ai_analysis.get('recommendation', 'Manual review required') + "\n\n")

            red_flags = ai_analysis.get('red_flags', [])
            if red_flags:
                f.write("Red Flags:\n")
                for flag in red_flags:
                    f.write(f"  ⚠️ {flag}\n")
                f.write("\n")

            f.write("="*100 + "\n")
            f.write("SIMILAR PROJECTS FOUND\n")
            f.write("="*100 + "\n\n")

            # Sort by AI similarity
            sorted_projects = sorted(
                all_projects,
                key=lambda x: x.get('ai_similarity', 0),
                reverse=True
            )

            for i, proj in enumerate(sorted_projects, 1):
                f.write(f"\n{'='*100}\n")
                f.write(f"PROJECT #{i}\n")
                f.write(f"{'='*100}\n")
                f.write(f"Name: {proj['name']}\n")
                f.write(f"Platform: {proj['platform']}\n")
                f.write(f"URL: {proj['url']}\n")

                if 'ai_similarity' in proj:
                    f.write(f"AI Similarity Score: {proj['ai_similarity']}/100\n")
                    f.write(f"AI Analysis: {proj.get('ai_reasoning', 'N/A')}\n")

                f.write(f"Search Query: {proj.get('search_query', 'N/A')}\n")

                if proj['platform'] == 'GitHub':
                    f.write(f"Stars: {proj['stars']}\n")
                    f.write(f"Language: {proj['language']}\n")
                    f.write(f"Created: {proj.get('created_at', 'N/A')}\n")
                else:
                    f.write(f"Likes: {proj['likes']}\n")
                    f.write(f"Comments: {proj['comments']}\n")
                    f.write(f"Winner: {'Yes' if proj.get('is_winner') else 'No'}\n")

                f.write(f"\nDescription:\n{proj['description']}\n")

    def analyze_fraud(self, project_info):
        """Main fraud detection analysis"""
        project_name = project_info['name']
        description = project_info['description']

        print("\n" + "="*100)
        print("🚨 HACKATHON FRAUD DETECTION SYSTEM")
        print("="*100)
        print(f"\nProject: {project_name}")
        print(f"Description: {description[:100]}...\n")

        # CLEAR CACHE FOR NEW ANALYSIS
        self.search_cache.clear()
        self.processed_projects.clear()
        print("✓ Cleared cache for fresh analysis")

        # Generate project-specific strategies
        search_strategies = self.generate_search_strategies(description)

        # Search platforms
        all_projects = []

        print("\n" + "="*100)
        print("SEARCHING DEVPOST (PRIORITY)")
        print("="*100)
        for strategy in search_strategies:
            results = self.search_devpost(strategy, max_pages=2)
            all_projects.extend(results)
            time.sleep(1)

        print("\n" + "="*100)
        print("SEARCHING GITHUB (SUPPLEMENTARY)")
        print("="*100)
        for strategy in search_strategies:
            results = self.search_github(strategy, max_results=8)
            all_projects.extend(results)
            time.sleep(1)

        print(f"\n📊 Total unique projects found: {len(all_projects)}")
        print(f"   Devpost: {sum(1 for p in all_projects if p['platform'] == 'Devpost')}")
        print(f"   GitHub: {sum(1 for p in all_projects if p['platform'] == 'GitHub')}")

        if not all_projects:
            print("\n✅ No similar projects found - Appears highly original")
            return {
                'fraud_risk': 'LOW',
                'originality_score': 95,
                'similar_projects': []
            }

        # AI analysis
        ai_analysis = self.ai_analyze_similarity(description, all_projects)

        # Generate report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"fraud_report_{project_name.replace(' ', '_')}_{timestamp}.txt"
        self.save_detailed_report(project_name, description, all_projects, ai_analysis, filename)

        # Print summary
        print("\n" + "="*100)
        print("🎯 FRAUD DETECTION RESULTS")
        print("="*100)
        print(f"Fraud Risk: {ai_analysis.get('fraud_risk', 'UNKNOWN')}")
        print(f"Originality Score: {ai_analysis.get('originality_score', 0)}/100")
        print(f"\n{ai_analysis.get('summary', 'No summary available')}")

        red_flags = ai_analysis.get('red_flags', [])
        if red_flags:
            print("\n⚠️ Red Flags Detected:")
            for flag in red_flags:
                print(f"   • {flag}")

        print(f"\n💡 Recommendation:\n{ai_analysis.get('recommendation', 'Manual review required')}")

        print(f"\n📄 Full report saved: {filename}")
        print("="*100 + "\n")

        return {
            'fraud_risk': ai_analysis.get('fraud_risk'),
            'originality_score': ai_analysis.get('originality_score'),
            'similar_projects': all_projects,
            'ai_analysis': ai_analysis
        }


def main():
    import os
    from dotenv import load_dotenv

    load_dotenv()
    CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")

    if not CLAUDE_API_KEY:
        raise ValueError("CLAUDE_API_KEY not found in environment variables")

    detector = HackathonFraudDetector(claude_api_key=CLAUDE_API_KEY)

    # Project to analyze
    project_info = {
        'name': 'SmartCam AI',
        'description': 'Transform passive recording systems into custom security cameras with AI-powered computer vision to detect suspicious activity and send real-time alerts to property owners through a mobile app'
    }

    result = detector.analyze_fraud(project_info)


if __name__ == "__main__":
    main()
