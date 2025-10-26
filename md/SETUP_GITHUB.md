# 🚀 Push to GitHub - Step by Step

## 1. Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `blueprint-hackathon-ai` (or whatever you want)
3. Description: "AI-powered hackathon idea generator with beautiful UI"
4. Make it **Public** or **Private**
5. **DO NOT** initialize with README (we already have one)
6. Click "Create repository"

## 2. Run These Commands

Open PowerShell in the Blueprint folder and run:

```bash
# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: Blueprint AI Hackathon Idea Generator"

# Connect to your repo (REPLACE WITH YOUR URL)
git remote add origin https://github.com/YOUR_USERNAME/blueprint-hackathon-ai.git

# Push
git branch -M main
git push -u origin main
```

## 3. Replace YOUR_USERNAME

In the command above, replace:
- `YOUR_USERNAME` with your actual GitHub username
- `blueprint-hackathon-ai` with your repo name if different

## Example

If your username is `johndoe`:
```bash
git remote add origin https://github.com/johndoe/blueprint-hackathon-ai.git
```

## 4. Done! 🎉

Your repo is now live at:
`https://github.com/YOUR_USERNAME/blueprint-hackathon-ai`

## ⚠️ Important Notes

- Your API key is **NOT** included (it's in `.gitignore`)
- Users will need to copy `config_settings.example.py` to `config_settings.py`
- Users will need to add their own Claude API key

## 📝 Update README

After pushing, you might want to:
1. Rename `PROJECT_SUMMARY.md` to `README.md`
2. Add screenshots
3. Add a demo video
4. Update the repo URL in the README

## 🔐 Security

✅ API keys are gitignored  
✅ Generated data folders are gitignored  
✅ Virtual environment is gitignored  
✅ Node modules are gitignored  

Safe to push!
