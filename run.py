"""
BrewBean Coffee — Multi-Branch Sales & Marketing Analytics System
Main entry point for running the Flask application server.
"""

from pathlib import Path
from dotenv import load_dotenv

# Ensure root .env is loaded before creating the app instance
load_dotenv(dotenv_path=Path(__file__).resolve().parent / '.env', override=True)

from app import create_app

app = create_app()

if __name__ == '__main__':
    print("==================================================")
    print("  BrewBean Coffee Analytics System Starting...")
    print(f"  DB Config: {app.config['DB_HOST']}:{app.config['DB_PORT']} ({app.config['DB_NAME']})")
    print("  Access web UI at: http://127.0.0.1:5000/")
    print("  Access health status at: http://127.0.0.1:5000/health")
    print("==================================================")
    app.run(host='127.0.0.1', port=5000, debug=True)
