# Hybrix

Hybrid training plans + AI coach for general hybrid athletes.

## Quick Start (Mac)

Open Terminal (Cmd + Space, type "Terminal", hit Enter) and run these commands:

```bash
# 1. Download the code
git clone https://github.com/Brix-Performance/hybrid-ai.git

# 2. Go into the folder
cd hybrid-ai

# 3. Install dependencies
pip3 install streamlit openai

# 4. Set up the AI Coach key
mkdir .streamlit
echo 'KIMI_API_KEY = "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"' > .streamlit/secrets.toml

# 5. Run the app
streamlit run app.py
```

A browser window opens automatically at `http://localhost:8501`.

## Features

**Plan Generator** — Enter your name, pick a fitness level and training days, and get a full weekly hybrid training plan with coach notes.

**AI Coach** — Chat with an AI-powered hybrid training coach. It knows your profile and your generated plan, so it can give specific advice about your workouts, form tips, modifications, recovery, and nutrition.

## Requirements

- Python 3
- No account needed — the AI coach runs on a free API

## Troubleshooting

- **"python3 not found"** — Install Python from https://python.org/downloads
- **"git not found"** — When prompted, click Install to get Mac Command Line Tools, then try again
- **AI Coach says "not configured"** — Make sure you ran step 4 above to create the secrets file
- **AI Coach is slow** — Normal! The free tier can take up to 2 minutes to respond
