"""
FastAPI server for Blueprint idea generator
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
import asyncio
import json
from api.services.idea_generator import IdeaGenerator
from api.services.similarity_reports import HackathonFraudDetector
from api.config.settings import CLAUDE_API_KEY, GEMINI_API_KEY
import anthropic
import google.generativeai as genai

app = FastAPI(title="Blueprint API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GenerateRequest(BaseModel):
    hackathon_url: str
    past_hackathons: Optional[List[str]] = None

async def generate_ideas_stream(hackathon_url: str, past_hackathons: Optional[List[str]] = None):
    """Stream progress updates while generating ideas"""
    
    try:
        # Send initial status
        yield f"data: {json.dumps({'status': 'Initializing...', 'progress': 'Setting up generator'})}\n\n"
        await asyncio.sleep(0.1)
        
        # Create generator
        generator = IdeaGenerator(
            new_hackathon_url=hackathon_url,
            past_hackathon_urls=past_hackathons
        )
        
        yield f"data: {json.dumps({'status': 'Setting up Claude AI...', 'progress': 'Configuring AI'})}\n\n"
        await asyncio.sleep(0.1)
        
        # Setup Claude
        if not generator.setup_claude(CLAUDE_API_KEY):
            yield f"data: {json.dumps({'error': 'Failed to setup Claude API'})}\n\n"
            return
        
        yield f"data: {json.dumps({'status': 'Scraping new hackathon rules...', 'progress': 'Extracting rules and requirements'})}\n\n"
        await asyncio.sleep(0.1)

        # Scrape new hackathon rules
        rules_data = generator.scrape_new_hackathon_rules()

        # Check if scraping failed (403/404 or invalid link)
        if not rules_data or len(rules_data) == 0:
            yield f"data: {json.dumps({'error': 'Invalid link. Unable to access the hackathon page (403/404 error or invalid URL)'})}\n\n"
            return

        yield f"data: {json.dumps({'status': 'Rules scraped successfully', 'progress': 'Found hackathon requirements'})}\n\n"
        await asyncio.sleep(0.1)
        
        # Get past hackathons
        if not generator.past_hackathon_urls:
            yield f"data: {json.dumps({'status': 'Using default past hackathons...', 'progress': 'Selecting 5 popular hackathons'})}\n\n"
            generator.past_hackathon_urls = generator.get_default_hackathons()
            await asyncio.sleep(0.1)
        
        yield f"data: {json.dumps({'status': 'Scraping past hackathon winners...', 'progress': f'Analyzing {len(generator.past_hackathon_urls)} hackathons'})}\n\n"
        await asyncio.sleep(0.1)
        
        # Scrape past hackathons
        winners_data = []
        for i, url in enumerate(generator.past_hackathon_urls, 1):
            yield f"data: {json.dumps({'status': f'Scraping hackathon {i}/{len(generator.past_hackathon_urls)}', 'progress': f'Analyzing {url}'})}\n\n"
            await asyncio.sleep(0.1)
            
            winners = generator.scrape_past_hackathon_winners(url)
            if winners:
                winners_data.append(winners)
        
        yield f"data: {json.dumps({'status': 'Generating ideas with Claude AI...', 'progress': 'Synthesizing winning patterns'})}\n\n"
        await asyncio.sleep(0.1)
        
        # Generate ideas
        try:
            print(f"[DEBUG] Calling Claude with {len(winners_data)} hackathons of data")
            print(f"[DEBUG] Rules data size: {len(str(rules_data))} chars")
            print(f"[DEBUG] Winners data size: {len(str(winners_data))} chars")
            
            ideas = generator.generate_ideas_with_claude(rules_data, winners_data)
            print(f"[DEBUG] Claude returned {len(ideas) if ideas else 0} characters")
            
            if not ideas or len(ideas) < 100:
                error_msg = f"Claude returned insufficient content ({len(ideas) if ideas else 0} chars). Check: 1) API key is valid, 2) Not rate limited, 3) Model name is correct"
                print(f"[ERROR] {error_msg}")
                yield f"data: {json.dumps({'error': error_msg})}\n\n"
                return
            
            # Verify file was created
            ideas_file = f"{generator.output_dir}/ideas.txt"
            import os
            if not os.path.exists(ideas_file):
                print(f"[ERROR] Ideas file was not created at {ideas_file}")
                yield f"data: {json.dumps({'error': 'Ideas file was not created'})}\n\n"
                return

            print(f"[SUCCESS] Ideas file created: {ideas_file}")
            result = {
                'output_dir': generator.output_dir,
                'ideas_file': ideas_file
            }
            yield f"data: {json.dumps({'status': 'Complete!', 'result': result})}\n\n"
            
        except Exception as e:
            print(f"[ERROR] Claude API error: {e}")
            import traceback
            traceback.print_exc()
            yield f"data: {json.dumps({'error': f'Claude API error: {str(e)}'})}\n\n"
            
    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"

@app.post("/generate")
async def generate_ideas(request: GenerateRequest):
    """Generate hackathon ideas endpoint"""
    print(f"[API] Received request: {request.hackathon_url}")
    return StreamingResponse(
        generate_ideas_stream(request.hackathon_url, request.past_hackathons),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "message": "Blueprint API is running"}

@app.get("/ideas/{file_path:path}")
async def get_ideas(file_path: str):
    """Parse and return ideas from the generated file"""
    try:
        import os
        import re
        
        # Read the ideas file
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Ideas file not found")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse ideas from the content
        ideas = []
        
        # Split by idea headers
        idea_sections = re.split(r'### Idea (\d+):', content)
        
        # Skip the first element (header before first idea)
        for i in range(1, len(idea_sections), 2):
            if i + 1 >= len(idea_sections):
                break
                
            number = int(idea_sections[i].strip())
            idea_content = idea_sections[i + 1]
            
            # Extract title (first line)
            lines = idea_content.strip().split('\n')
            title = lines[0].strip() if lines else "Untitled"
            
            # Extract sections using regex
            problem_match = re.search(r'\*\*Problem Statement\*\*:\s*(.+?)(?=\n\n\*\*|\n\*\*|$)', idea_content, re.DOTALL)
            solution_match = re.search(r'\*\*Solution Overview\*\*:\s*(.+?)(?=\n\n\*\*|\n\*\*|$)', idea_content, re.DOTALL)
            tech_match = re.search(r'\*\*Key Technologies\*\*:\s*\n(.+?)(?=\n\*\*|$)', idea_content, re.DOTALL)
            why_match = re.search(r'\*\*Why It Wins\*\*:\s*\n(.+?)(?=\n\*\*|$)', idea_content, re.DOTALL)
            inspired_match = re.search(r'\*\*Inspired By\*\*:\s*(.+?)(?=\n\n\*\*|\n\*\*|$)', idea_content, re.DOTALL)
            roadmap_match = re.search(r'\*\*Implementation Roadmap\*\*:\s*\n(.+?)(?=\n\n###|\n###|$)', idea_content, re.DOTALL)
            
            # Parse technologies (bulleted list)
            technologies = []
            if tech_match:
                tech_text = tech_match.group(1).strip()
                technologies = [line.strip('- ').strip() for line in tech_text.split('\n') if line.strip().startswith('-')]
            
            # Parse why it wins (bulleted list)
            why_wins = []
            if why_match:
                why_text = why_match.group(1).strip()
                why_wins = [line.strip('- ').strip() for line in why_text.split('\n') if line.strip().startswith('-')]
            
            # Parse roadmap (numbered list)
            roadmap = []
            if roadmap_match:
                roadmap_text = roadmap_match.group(1).strip()
                roadmap = [re.sub(r'^\d+\.\s*', '', line.strip()) for line in roadmap_text.split('\n') if line.strip() and re.match(r'^\d+\.', line.strip())]
            
            ideas.append({
                'number': number,
                'title': title,
                'problem': problem_match.group(1).strip() if problem_match else '',
                'solution': solution_match.group(1).strip() if solution_match else '',
                'technologies': technologies,
                'whyItWins': why_wins,
                'inspiredBy': inspired_match.group(1).strip() if inspired_match else '',
                'roadmap': roadmap
            })
        
        return {"ideas": ideas}
        
    except Exception as e:
        print(f"Error parsing ideas: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

#for anuragg
@app.post("/breakdown")
async def generate_breakdown(request: dict):
    """Generate detailed step-by-step implementation instructions using Gemini"""
    try:
        import os
        import json

        idea = request.get('idea')
        hackathon_folder = request.get('hackathon_folder')

        if not idea:
            raise HTTPException(status_code=400, detail="Idea is required")

        # Get hackathon schedule if available
        schedule_text = ""
        if hackathon_folder and os.path.exists(hackathon_folder):
            rules_file = os.path.join(hackathon_folder, "rules.json")
            if os.path.exists(rules_file):
                with open(rules_file, 'r', encoding='utf-8') as f:
                    rules_data = json.load(f)
                    schedule_data = rules_data.get('rules_data', {}).get('schedule', {})
                    if schedule_data:
                        schedule_text = schedule_data.get('text', '')

        # Configure Gemini
        genai.configure(api_key=GEMINI_API_KEY)

        # Use gemini-2.0-flash-exp with longer timeout settings
        model = genai.GenerativeModel(
            'gemini-2.0-flash-exp',
            generation_config={
                'max_output_tokens': 8000,
                'temperature': 0.7,
            }
        )

        # Create prompt
        prompt = f"""You are an expert hackathon mentor. Create a detailed, step-by-step implementation guide for this project idea.

PROJECT IDEA:
Title: {idea.get('title', 'Untitled')}
Problem: {idea.get('problem', '')}
Solution: {idea.get('solution', '')}
Technologies: {', '.join(idea.get('technologies', []))}

{f'HACKATHON SCHEDULE:\n{schedule_text}\n' if schedule_text else ''}

Create a comprehensive implementation guide with:

1. **Project Setup** (15-30 min)
   - Environment setup
   - Dependencies installation
   - Project structure

2. **Core Features** (broken into 2-3 hour chunks)
   - Feature 1: [Name] - What to build and how
   - Feature 2: [Name] - What to build and how
   - Feature 3: [Name] - What to build and how

3. **Integration** (1-2 hours)
   - Connect all components
   - API integration
   - Testing

4. **Polish & Demo** (1-2 hours)
   - UI/UX improvements
   - Demo preparation
   - Presentation tips

5. **Time Management Tips**
   - Prioritization advice
   - What to build first
   - What can be mocked/simplified

For each step, provide:
- Estimated time
- Specific code examples or pseudocode
- Common pitfalls to avoid
- Quick wins and shortcuts

Make it practical, actionable, and optimized for hackathon time constraints.
"""

        # Generate response with Gemini - with NO timeout (let it complete)
        try:
            # Set request_options to allow longer processing time
            response = model.generate_content(
                prompt,
                request_options={'timeout': 120}  # 2 minute timeout instead of default
            )

            breakdown = response.text

            # Verify we got a valid response
            if not breakdown or len(breakdown) < 100:
                raise Exception("Gemini returned insufficient content")

            return {
                "breakdown": breakdown,
                "has_schedule": bool(schedule_text)
            }

        except Exception as e:
            error_msg = str(e).lower()

            # More specific error handling
            if 'timeout' in error_msg or 'deadline' in error_msg:
                raise HTTPException(status_code=504, detail="The AI is taking longer than expected. This usually means it's generating a very detailed guide. Please try again.")
            elif 'quota' in error_msg or 'rate limit' in error_msg:
                raise HTTPException(status_code=429, detail="API rate limit reached. Please wait a moment and try again.")
            elif 'invalid' in error_msg or 'bad request' in error_msg:
                raise HTTPException(status_code=400, detail=f"Invalid request to Gemini: {str(e)}")
            else:
                raise HTTPException(status_code=500, detail=f"Gemini API error: {str(e)}")

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error generating breakdown: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

class SimilarityRequest(BaseModel):
    devpost_url: str

async def check_similarity_stream(devpost_url: str):
    """Stream similarity check results as they are found"""
    try:
        from api.services.devpost_scraper import DevpostScraper

        # Clean URL - remove query parameters and normalize
        if '?' in devpost_url:
            devpost_url = devpost_url.split('?')[0]

        # Remove trailing slashes and fragments
        devpost_url = devpost_url.rstrip('/').split('#')[0]

        # Normalize URL (convert to lowercase for comparison)
        submitted_project_url = devpost_url.lower().strip()

        # Initial status
        yield f"data: {json.dumps({'status': 'Fetching project details...', 'progress': 'Loading Devpost project'})}\n\n"
        await asyncio.sleep(0.1)

        # Scrape project from Devpost
        scraper = DevpostScraper(devpost_url)
        project_data = scraper.scrape_individual_project(devpost_url, "Target Project")

        if not project_data:
            yield f"data: {json.dumps({'error': 'Invalid link. Unable to access the Devpost project (403/404 error or invalid URL)'})}\n\n"
            return

        project_name = project_data.get('title', 'Unknown Project')
        submission_date = project_data.get('submission_date', None)
        description = project_data.get('description', project_data.get('tagline', ''))

        if not description:
            yield f"data: {json.dumps({'error': 'Invalid link. Project description not found on this page'})}\n\n"
            return

        # Validate description is meaningful (not just the platform name or too short)
        description_words = description.split()
        if len(description_words) < 10:
            yield f"data: {json.dumps({'error': 'Project description is too short or invalid. Please ensure the Devpost project has a proper description (at least 10 words).'})}\n\n"
            return

        # Check if description is just generic platform names
        if description.strip().lower() in ['devpost', 'github', 'hackathon']:
            yield f"data: {json.dumps({'error': 'Invalid project description. The scraper only found the platform name. Please check the Devpost URL.'})}\n\n"
            return

        # Limit description to 300 words
        words = description.split()
        if len(words) > 300:
            description = ' '.join(words[:300])
            print(f"⚠️ Description truncated from {len(words)} to 300 words")

        yield f"data: {json.dumps({'status': f'Analyzing: {project_name}', 'progress': 'Initializing detector'})}\n\n"
        await asyncio.sleep(0.1)

        # Initialize FRESH detector instance (avoids cache pollution between requests)
        # Pass the submitted project URL to exclude it from results
        detector = HackathonFraudDetector(claude_api_key=CLAUDE_API_KEY, exclude_url=submitted_project_url)
        print(f"✓ Created fresh detector for: {project_name}")
        print(f"✓ Excluding URL: {submitted_project_url}")

        yield f"data: {json.dumps({'status': 'Generating project-specific search strategies', 'progress': 'Analyzing description'})}\n\n"
        await asyncio.sleep(0.1)

        # Generate PROJECT-SPECIFIC strategies
        strategies = detector.generate_search_strategies(description)
        yield f"data: {json.dumps({'status': 'Strategies generated', 'progress': f'Created {len(strategies)} unique queries for this project'})}\n\n"
        await asyncio.sleep(0.1)

        # Search and stream results
        all_projects = []
        github_count = 0
        devpost_count = 0
        seen_urls = set()  # Track URLs to prevent duplicates

        # Add the submitted project URL to seen_urls to exclude it from results
        seen_urls.add(submitted_project_url)

        # Use top 4 strategies for focused results
        top_strategies = strategies[:min(4, len(strategies))]

        # Devpost search FIRST - more relevant for hackathon projects
        for i, strategy in enumerate(top_strategies, 1):
            yield f"data: {json.dumps({'status': f'Searching Devpost', 'progress': f'Strategy {i}/{len(top_strategies)}: {strategy["query"]}'})}\n\n"
            await asyncio.sleep(0.1)

            results = detector.search_devpost(strategy, max_pages=1)
            for result in results:
                # Normalize URL for comparison
                normalized_url = result['url'].lower().strip().rstrip('/').split('?')[0].split('#')[0]

                if normalized_url not in seen_urls:
                    seen_urls.add(normalized_url)
                    devpost_count += 1
                    all_projects.append(result)
                    yield f"data: {json.dumps({'project': result, 'source_progress': f'Devpost: {devpost_count}'})}\n\n"
                    await asyncio.sleep(0.05)

            await asyncio.sleep(0.5)

        # GitHub search SECOND - supplementary results
        for i, strategy in enumerate(top_strategies, 1):
            yield f"data: {json.dumps({'status': f'Searching GitHub', 'progress': f'Strategy {i}/{len(top_strategies)}: {strategy["query"]}'})}\n\n"
            await asyncio.sleep(0.1)

            results = detector.search_github(strategy, max_results=3)  # Reduced from 5 to 3
            for result in results:
                # Normalize URL for comparison
                normalized_url = result['url'].lower().strip().rstrip('/').split('?')[0].split('#')[0]

                if normalized_url not in seen_urls:
                    seen_urls.add(normalized_url)
                    github_count += 1
                    all_projects.append(result)
                    yield f"data: {json.dumps({'project': result, 'source_progress': f'GitHub: {github_count}'})}\n\n"
                    await asyncio.sleep(0.05)

            await asyncio.sleep(0.5)

        # all_projects already has duplicates removed via seen_urls tracking above
        unique_projects = all_projects

        yield f"data: {json.dumps({'status': 'AI analyzing similarities...', 'progress': f'Found {len(unique_projects)} unique projects (GitHub: {github_count}, Devpost: {devpost_count})'})}\n\n"
        await asyncio.sleep(0.1)

        if unique_projects:
            # AI analysis - analyze top 20 most relevant projects
            projects_to_analyze = unique_projects[:20]

            yield f"data: {json.dumps({'status': 'Running AI similarity analysis...', 'progress': f'Analyzing {len(projects_to_analyze)} projects'})}\n\n"
            await asyncio.sleep(0.1)

            ai_analysis = detector.ai_analyze_similarity(description, projects_to_analyze)

            # Stream updated scores for each project
            for i, proj in enumerate(projects_to_analyze):
                if i < len(ai_analysis.get('project_scores', [])):
                    proj['ai_similarity'] = ai_analysis['project_scores'][i]['similarity']
                    proj['ai_reasoning'] = ai_analysis['project_scores'][i]['reasoning']

                    # Stream the updated project with similarity score
                    yield f"data: {json.dumps({'project_update': proj, 'analysis_progress': f'{i+1}/{len(projects_to_analyze)}'})}\n\n"
                    await asyncio.sleep(0.05)

            yield f"data: {json.dumps({'status': 'Complete', 'result': {'fraud_risk': ai_analysis.get('fraud_risk'), 'originality_score': ai_analysis.get('originality_score'), 'total_projects': len(unique_projects), 'submission_date': submission_date, 'project_name': project_name}})}\n\n"
        else:
            yield f"data: {json.dumps({'status': 'Complete', 'result': {'fraud_risk': 'LOW', 'originality_score': 95, 'total_projects': 0, 'submission_date': submission_date, 'project_name': project_name}})}\n\n"

    except Exception as e:
        print(f"Similarity check error: {e}")
        import traceback
        traceback.print_exc()
        yield f"data: {json.dumps({'error': str(e)})}\n\n"

@app.post("/similarity-check")
async def check_similarity(request: SimilarityRequest):
    """Check similarity for a Devpost project"""
    print(f"[API] Similarity check request: {request.devpost_url}")
    return StreamingResponse(
        check_similarity_stream(request.devpost_url),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Blueprint API server...")
    print("📍 Frontend: http://localhost:5173")
    print("📍 API: http://localhost:8000")
    print("📍 Docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)