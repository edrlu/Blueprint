# Security Setup Guide

## 🔐 API Key Configuration

This project requires API keys to function. **NEVER commit API keys to version control!**

### Quick Setup

1. **Copy the example environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` and add your API keys:**
   ```bash
   # Open .env in your text editor
   nano .env
   # or
   code .env
   ```

3. **Get your API keys:**
   - **Claude API Key** (Required):
     - Visit: https://console.anthropic.com/
     - Create an account or log in
     - Navigate to API Keys section
     - Create a new key
     - Copy and paste into `CLAUDE_API_KEY` in `.env`

   - **Gemini API Key** (Optional):
     - Visit: https://makersuite.google.com/app/apikey
     - Create an account or log in
     - Generate API key
     - Copy and paste into `GEMINI_API_KEY` in `.env`

4. **Install dependencies:**
   ```bash
   # Install Python dependencies (includes python-dotenv)
   pip install -r requirements.txt

   # Or if using virtual environment
   .venv/Scripts/activate  # Windows
   source .venv/bin/activate  # Mac/Linux
   pip install -r requirements.txt
   ```

### Environment Variables

Your `.env` file should look like this:

```env
# Claude API Key (Required)
CLAUDE_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxxxxxxx

# Gemini API Key (Optional)
GEMINI_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxxxxx

# AI Model Selection
AI_MODEL=claude

# Backend API URL
VITE_API_URL=http://localhost:8000
```

## 🚫 What NOT to Do

- ❌ **DO NOT** commit `.env` to git
- ❌ **DO NOT** share your `.env` file
- ❌ **DO NOT** hardcode API keys in code
- ❌ **DO NOT** post API keys in Discord/Slack
- ❌ **DO NOT** include keys in screenshots

## ✅ What TO Do

- ✅ **DO** use `.env.example` as a template
- ✅ **DO** keep `.env` in `.gitignore`
- ✅ **DO** use environment variables
- ✅ **DO** rotate keys if exposed
- ✅ **DO** use different keys for dev/prod

## 🔍 Files Protected

The following files are automatically ignored by git:

- `.env` and all `.env.*` files
- `api/config/settings.py` (if you modify it)
- Any `*.bak`, `*.backup`, `*.old` files

## 🚨 If Keys Are Exposed

If you accidentally commit API keys:

1. **Immediately revoke the keys:**
   - Claude: https://console.anthropic.com/settings/keys
   - Gemini: https://makersuite.google.com/app/apikey

2. **Generate new keys**

3. **Update your `.env` file**

4. **Remove from git history:**
   ```bash
   # Remove sensitive file from history
   git filter-branch --force --index-filter \
   "git rm --cached --ignore-unmatch path/to/file" \
   --prune-empty --tag-name-filter cat -- --all

   # Force push (only if necessary and you understand the implications)
   git push origin --force --all
   ```

## 📝 Adding New API Keys

If you need to add new API keys:

1. Add to `.env.example` (with placeholder):
   ```env
   NEW_API_KEY=your_new_api_key_here
   ```

2. Add to your personal `.env` (with real key):
   ```env
   NEW_API_KEY=actual-key-value
   ```

3. Update `api/config/settings.py`:
   ```python
   NEW_API_KEY = os.getenv("NEW_API_KEY")
   ```

4. Ensure `.gitignore` includes `.env`

## 🧪 Testing Security

Before pushing code, verify no keys are exposed:

```bash
# Search for potential API keys
grep -r "sk-ant-api" .
grep -r "AIzaSy" .

# Check what will be committed
git status
git diff --cached

# Verify .env is ignored
git check-ignore .env
```

Should return: `.env` (confirming it's ignored)

## 🏗️ Production Deployment

For production environments:

1. **Use environment variables** provided by your hosting platform:
   - Vercel: Project Settings → Environment Variables
   - Heroku: `heroku config:set CLAUDE_API_KEY=xxx`
   - AWS: Use AWS Secrets Manager
   - Docker: Use `--env-file` or docker-compose secrets

2. **Never use `.env` files in production** - use platform-specific secrets management

3. **Set up monitoring** for API usage to detect unauthorized access

## 📚 Additional Resources

- [Anthropic API Documentation](https://docs.anthropic.com/)
- [Google AI Studio](https://ai.google.dev/)
- [GitHub Security Best Practices](https://docs.github.com/en/code-security)
