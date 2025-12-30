from flask import Flask
from page_analyzer.config import get_database_url, get_secret_key, load_env

load_env()

app = Flask(__name__)
app.config["SECRET_KEY"] = get_secret_key()

# Stored for future DB integration (will be used in next steps)
app.config["DATABASE_URL"] = get_database_url()


@app.get("/")
def index():
    return "Page Analyzer is running!"
