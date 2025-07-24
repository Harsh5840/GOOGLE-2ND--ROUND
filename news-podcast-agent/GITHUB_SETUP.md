# 🚀 GitHub Setup Guide

This guide will help you publish your News Podcast Agent to GitHub and set it up for collaboration.

## 📋 Prerequisites

- [Git](https://git-scm.com/downloads) installed on your system
- [GitHub account](https://github.com/signup) created
- Your project folder ready with all files

## 🔧 Step-by-Step Setup

### 1. Initialize Git Repository

Open terminal in your project folder and run:

```bash
cd "c:\Users\VICTUS 15\Desktop\ioio\news-podcast-agent"
git init
```

### 2. Add Files to Git

```bash
# Add all files (respecting .gitignore)
git add .

# Check what files will be committed
git status

# Commit your initial version
git commit -m "Initial commit: News Podcast Agent with FastAPI backend

- Complete FastAPI REST API for podcast generation
- Google Cloud TTS integration with API key authentication
- Web interface with real-time job tracking
- Next.js compatible backend
- Comprehensive documentation and examples"
```

### 3. Create GitHub Repository

1. Go to [GitHub](https://github.com) and sign in
2. Click the **"+"** button in the top right corner
3. Select **"New repository"**
4. Fill in the details:
   - **Repository name**: `news-podcast-agent`
   - **Description**: `AI-powered news podcast generator with FastAPI backend and Google Cloud TTS`
   - **Visibility**: Choose Public or Private
   - **DO NOT** initialize with README (we already have one)
5. Click **"Create repository"**

### 4. Connect Local Repository to GitHub

Copy the commands from GitHub (they'll look like this):

```bash
git remote add origin https://github.com/YOURUSERNAME/news-podcast-agent.git
git branch -M main
git push -u origin main
```

Replace `YOURUSERNAME` with your actual GitHub username.

### 5. Verify Upload

1. Refresh your GitHub repository page
2. You should see all your files uploaded
3. The README.md should display automatically

## 🔒 Security Checklist

Before pushing to GitHub, ensure:

- ✅ `.env` file is in `.gitignore` (it is!)
- ✅ No API keys in code (they're in environment variables)
- ✅ No sensitive files committed
- ✅ `.env.template` shows required variables without actual keys

## 📝 Repository Settings

### Enable Issues and Discussions
1. Go to your repository on GitHub
2. Click **Settings** tab
3. Scroll to **Features** section
4. Enable:
   - ✅ Issues
   - ✅ Discussions (optional)
   - ✅ Wiki (optional)

### Add Topics/Tags
1. Click the ⚙️ gear icon next to "About" on your repo homepage
2. Add topics: `ai`, `podcast`, `fastapi`, `google-cloud`, `tts`, `news`, `python`, `nextjs`

### Create Release
1. Go to **Releases** on your repo
2. Click **"Create a new release"**
3. Tag: `v1.0.0`
4. Title: `News Podcast Agent v1.0.0`
5. Description:
```markdown
## 🎙️ Initial Release

### Features
- ✨ Complete FastAPI backend for podcast generation
- 🤖 AI-powered script creation with Google Gemini
- 🎵 High-quality TTS with Google Cloud Studio voices
- 🌐 Web interface with real-time progress tracking
- 📱 Next.js/React compatible REST API
- 🔒 Secure API key authentication

### Quick Start
1. Clone the repository
2. Copy `.env.template` to `.env` and add your Google API key
3. Run `python run_api.py`
4. Open `frontend_example.html` or visit http://localhost:8000/docs

### API Endpoints
- `POST /api/v1/podcast/generate` - Generate podcasts
- `GET /api/v1/jobs/{job_id}` - Check generation status
- `GET /api/v1/files/{filename}` - Download audio files
- `POST /api/v1/tts` - Direct text-to-speech conversion

See [API_README.md](API_README.md) for complete documentation.
```

## 🤝 Collaboration Setup

### Branch Protection (Optional)
1. Go to **Settings** → **Branches**
2. Add rule for `main` branch:
   - ✅ Require pull request reviews
   - ✅ Require status checks to pass

### Issue Templates
Create `.github/ISSUE_TEMPLATE/` folder with:

#### Bug Report Template
```markdown
---
name: Bug report
about: Create a report to help us improve
title: '[BUG] '
labels: bug
assignees: ''
---

**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. See error

**Expected behavior**
What you expected to happen.

**Environment:**
- OS: [e.g. Windows 10]
- Python version: [e.g. 3.11]
- Browser: [e.g. Chrome 91]

**Additional context**
Add any other context about the problem here.
```

#### Feature Request Template
```markdown
---
name: Feature request
about: Suggest an idea for this project
title: '[FEATURE] '
labels: enhancement
assignees: ''
---

**Is your feature request related to a problem?**
A clear description of what the problem is.

**Describe the solution you'd like**
A clear description of what you want to happen.

**Additional context**
Add any other context about the feature request here.
```

## 📊 GitHub Actions (Optional)

Create `.github/workflows/ci.yml` for automated testing:

```yaml
name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.10, 3.11]

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v3
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .
    
    - name: Test imports
      run: |
        python -c "from app.api_server import app; print('✅ API server imports successfully')"
        python -c "from app.tools import synthesize_speech; print('✅ Tools import successfully')"
```

## 🎯 Next Steps

After setting up GitHub:

1. **Share your repository** with the community
2. **Add contributors** if working with a team
3. **Create documentation** in the Wiki
4. **Set up GitHub Pages** for project website (optional)
5. **Add badges** to README for build status, license, etc.

## 🆘 Troubleshooting

### Common Issues

**"Permission denied" when pushing:**
- Check if you're using the correct repository URL
- Ensure you have push access to the repository
- Try using SSH instead of HTTPS

**Large files rejected:**
- Check if any audio files are being committed
- Ensure `.gitignore` is working properly
- Use `git rm --cached filename` to remove accidentally added files

**API keys exposed:**
- Remove the commit with: `git reset --hard HEAD~1` (if not pushed yet)
- If already pushed, rotate your API keys immediately
- Add the file to `.gitignore` and commit the fix

## 📞 Support

If you need help:
1. Check the [GitHub documentation](https://docs.github.com/)
2. Create an issue in your repository
3. Ask in the [GitHub Community](https://github.community/)

Happy coding! 🚀
