"""
Configuration constants and settings for the Devpost scraper
"""

# Common Devpost tab patterns
COMMON_TABS = {
    'overview': '',
    'projects': '/submissions',  # Fixed: most Devpost events use /submissions
    'updates': '/updates', 
    'rules': '/rules',
    'participants': '/participants',
    'project_gallery': '/project-gallery',
    'discussions': '/discussions',
    'prizes': '/prizes',
    'schedule': '/schedule',
    'mentors': '/mentors'
}

# Alternative tab patterns to try if primary ones fail
ALTERNATIVE_TABS = {
    'projects': ['/projects', '/submissions', '/entries'],
    'rules': ['/rules', '/guidelines', '/requirements'],
    'project_gallery': ['/project-gallery', '/gallery', '/winners', '/showcase'],
    'schedule': ['/schedule', '/timeline', '/agenda'],
    'prizes': ['/prizes', '/awards', '/sponsors'],
    'mentors': ['/mentors', '/judges', '/volunteers']
}

# Tab name mapping for different naming conventions
TAB_MAPPING = {
    'overview': ['overview', 'home', 'main', 'about'],
    'projects': ['projects', 'submissions', 'entries', 'submitted'],
    'updates': ['updates', 'news', 'announcements', 'blog'],
    'rules': ['rules', 'guidelines', 'requirements', 'criteria'],
    'participants': ['participants', 'teams', 'hackers', 'attendees'],
    'project_gallery': ['gallery', 'showcase', 'featured', 'winners'],
    'discussions': ['discussions', 'forum', 'chat', 'community'],
    'prizes': ['prizes', 'awards', 'sponsors', 'prize'],
    'schedule': ['schedule', 'timeline', 'agenda', 'events'],
    'mentors': ['mentors', 'judges', 'volunteers']
}

# Winner indicators for project detection
WINNER_INDICATORS = [
    'winner', 'first place', 'second place', 'third place',
    'grand prize', 'best', 'award', 'prize', '1st', '2nd', '3rd',
    'gold', 'silver', 'bronze', 'champion'
]

# Common technology keywords for analysis
TECH_KEYWORDS = [
    'python', 'javascript', 'react', 'node', 'java', 'c++', 'c#', 'swift', 'kotlin',
    'html', 'css', 'sql', 'mongodb', 'postgresql', 'mysql', 'redis', 'docker',
    'kubernetes', 'aws', 'azure', 'gcp', 'firebase', 'tensorflow', 'pytorch',
    'machine learning', 'ai', 'blockchain', 'ethereum', 'solidity', 'web3',
    'api', 'rest', 'graphql', 'microservices', 'mobile', 'ios', 'android',
    'flutter', 'react native', 'vue', 'angular', 'django', 'flask', 'express',
    'spring', 'laravel', 'rails', 'php', 'ruby', 'go', 'rust', 'scala'
]

# Common stop words to filter out from topic extraction
STOP_WORDS = [
    'this', 'that', 'with', 'from', 'they', 'have', 'been', 'were', 'said', 'each', 
    'which', 'their', 'time', 'will', 'about', 'there', 'could', 'other', 'after', 
    'first', 'well', 'also', 'where', 'much', 'some', 'very', 'when', 'here', 'just', 
    'into', 'over', 'think', 'back', 'then', 'only', 'come', 'right', 'work', 'life', 
    'know', 'place', 'year', 'live', 'me', 'take', 'get', 'go', 'see', 'make', 'way', 
    'up', 'out', 'many', 'them', 'can', 'new', 'what', 'these', 'so', 'she', 'do', 
    'how', 'if', 'her', 'would', 'like', 'him', 'has', 'two', 'more', 'no', 'than', 
    'been', 'call', 'who', 'its', 'now', 'find', 'long', 'down', 'day', 'did', 'come', 
    'made', 'may', 'part'
]

# HTTP headers for web scraping
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
}

# Navigation selectors for tab detection
NAV_SELECTORS = [
    'nav a', '.nav a', '.navigation a', '.menu a',
    '.tabs a', '.tab a', '.nav-tabs a', '.nav-pills a',
    'ul.nav a', '.navbar a', '.header a'
]

# Analysis notes for different sections
ANALYSIS_NOTES = {
    "overview": "This section contains the main event information, description, and key details about the hackathon.",
    "projects": "This section lists all submitted projects. Look for winning projects, popular technologies, and project categories.",
    "updates": "This section contains announcements, news, and updates about the event. Look for important dates and changes.",
    "rules": "This section contains the event rules, guidelines, and requirements. Important for understanding event structure.",
    "participants": "This section shows registered participants, teams, and attendees. Useful for understanding event scale.",
    "project_gallery": "This section showcases featured or winning projects with detailed information.",
    "discussions": "This section contains community discussions, Q&A, and participant interactions.",
    "prizes": "This section lists prizes, awards, and sponsors. Important for understanding event incentives.",
    "schedule": "This section contains the event timeline, agenda, and important dates.",
    "mentors": "This section lists mentors, judges, and volunteers involved in the event."
}
