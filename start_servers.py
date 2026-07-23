import subprocess, sys, time, os

print("Starting MoneyPrinterTurbo servers...")

# Start FastAPI backend
backend = subprocess.Popen(
    [sys.executable, "main.py"],
    cwd=os.path.dirname(os.path.abspath(__file__)),
    env={**os.environ, "LISTEN_HOST": "0.0.0.0", "LISTEN_PORT": "8080"}
)

time.sleep(3)
print("Backend started")

# Start Streamlit frontend
os.environ["STREAMLIT_SERVER_PORT"] = os.environ.get("PORT", "8501")
os.environ["STREAMLIT_SERVER_ADDRESS"] = "0.0.0.0"
os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"

frontend = subprocess.Popen(
    [sys.executable, "-m", "streamlit", "run", "webui/quick_app.py",
     "--server.port", os.environ["STREAMLIT_SERVER_PORT"],
     "--server.address", "0.0.0.0",
     "--server.headless", "true",
     "--browser.gatherUsageStats", "false"],
    cwd=os.path.dirname(os.path.abspath(__file__))
)

print(f"Frontend starting on port {os.environ['STREAMLIT_SERVER_PORT']}")

# Wait for either process to exit
backend.wait()
frontend.wait()
