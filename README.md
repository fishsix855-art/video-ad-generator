# AI Video Ad Generator

One-click AI video ad generator for telecom stores. Powered by Seedance video generation and DeepSeek creative AI.

## Quick Deploy (2 steps)

### Step 1: Deploy on Streamlit Cloud

1. Go to https://streamlit.io/cloud
2. Click **Sign in with GitHub**
3. Click **New app** (top right)
4. Select repo: ishsix855-art/video-ad-generator
5. Branch: master
6. Main file path: webui/quick_app.py
7. Click **Deploy!**

### Step 2: Add API Keys

In your app's settings on Streamlit Cloud, go to **Secrets** and add:

`	oml
DEEPSEEK_API_KEY = sk-your-key
VOLCENGINE_API_KEY = ark-your-key
VOLCENGINE_MODEL_NAME = doubao-seedance-1-0-pro-fast-251015
`

Click **Save** and the app will reboot. Done!

## Local Development

`ash
pip install -r requirements.txt
cp config.toml.example config.toml
# Edit config.toml with your API keys
streamlit run webui/quick_app.py
`

## Tech Stack

- Streamlit + Seedance API + DeepSeek
- Based on MoneyPrinterTurbo
