# AI Video Ad Generator
One-click AI video ad generator for telecom stores. Seedance + DeepSeek.

## Deploy (2 minutes)

### 1. Deploy on Streamlit Cloud
Go to https://share.streamlit.io
- Sign in with GitHub
- Click **New app** -> Select this repo
- Main file: webui/quick_app.py
- Click **Deploy!**

### 2. Add Secrets
In the app dashboard, go to **Settings -> Secrets**, paste:

`
DEEPSEEK_API_KEY = sk-your-key
VOLCENGINE_API_KEY = ark-your-key
VOLCENGINE_MODEL_NAME = doubao-seedance-1-0-pro-fast-251015
LLM_PROVIDER = deepseek
`

Save and reboot. Done!

## Local Dev
`ash
pip install -r requirements.txt
cp config.toml.example config.toml
# edit keys in config.toml
streamlit run webui/quick_app.py
`
