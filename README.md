# AI Video Ad Generator

A one-click AI video ad generator for telecom retail stores. Built on [MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo) with Seedance video generation and DeepSeek creative AI.

## Features

- **One-click video generation**: Input a promotion description, AI generates creative scripts, storyboard prompts, and final videos
- **Seedance video generation**: AI-generated video footage via Volcano Engine ARK
- **DeepSeek creative engine**: Generates 6 creative concepts with different styles
- **Scene templates**: Quick-start with common telecom promotion templates
- **Reference image upload**: Upload store photos for consistent branding
- **Download & restyle**: Download videos or regenerate with a different style

## Quick Deploy on Railway

1. Fork this repo
2. Go to [Railway](https://railway.app) and login with GitHub
3. Click **New Project** -> **Deploy from GitHub repo** -> Select this repo
4. Add these environment variables in Railway:
   - DEEPSEEK_API_KEY - Your DeepSeek API key
   - VOLCENGINE_API_KEY - Your Volcano Engine ARK API key
   - VOLCENGINE_MODEL_NAME - Seedance model (default: doubao-seedance-1-0-pro-fast-251015)
5. Deploy!

## Local Development

`ash
pip install -r requirements.txt

# Create config.toml with your API keys
cp config.toml.example config.toml
# Edit config.toml with your keys

# Start servers
python start_servers.py
`

## Tech Stack

- **Frontend**: Streamlit
- **Backend**: FastAPI
- **Video Generation**: Volcano Engine Seedance API
- **Creative AI**: DeepSeek
- **Original Base**: MoneyPrinterTurbo
